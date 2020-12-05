import skia
import glfw
import os
import sys
import traceback
from time import time
from types import ModuleType

class Drawer:
	RELOAD_INTERVAL = 0.2
	def __init__(self, main_module: ModuleType, drawy_module: ModuleType):
		self.main_module = main_module
		self.drawy_module = drawy_module
		self.main_path = main_module.__file__
		self.files_mtime = {}
		self.last_reload = time()
		self.drawy_vars = [n for n in dir(self.drawy_module) if n.isupper() and n[0] != '_']

	def init_glfw(self):
		glfw.init()
		self.KEY_NAMES = {}
		self.MOUSE_NAMES = {}
		for n, v in vars(glfw).items():
			if n.startswith('KEY_'):
				if v == glfw.KEY_SPACE:
					name = ' '
				elif 0 < v < 128:
					name = glfw.get_key_name(v, 0)
				else:
					name = n[4:]
				if name.startswith('KP_'):
					name = name[3:]
				self.KEY_NAMES[v] = name.lower()
			elif n.startswith('MOUSE_BUTTON_'):
				self.MOUSE_NAMES[v] = n[13:].lower()

	def run(self, width, height, resizable, title, background_color):
		self.init_glfw()
		glfw.window_hint(glfw.RESIZABLE, resizable)
		window = glfw.create_window(width, height, title, None, None)
		self.window = window
		self.refresh_rate = glfw.get_video_mode(glfw.get_primary_monitor()).refresh_rate
		glfw.make_context_current(window)
		glfw.swap_interval(1) # vsync

		glfw.set_key_callback(window, self.key_callback)
		glfw.set_mouse_button_callback(window, self.mouse_button_callback)
		glfw.set_framebuffer_size_callback(window, self.framebuffer_size_callback)
		glfw.set_monitor_callback(self.monitor_callback)

		self.reset_canvas_size(*glfw.get_framebuffer_size(window))
		self.monitor_callback()
		self.change_background_color(background_color)

		context = self.drawy_module
		context.FRAME = 0
		self.sync_context_with_main()
		self.reload_module(self.main_module)

		try:
			self.call_from_main("init", [], reraise=True)
		except:
			return

		while not glfw.window_should_close(window):
			self.reload_main_if_modified()
			canvas = context._canvas
			context.MOUSE_POSITION = context.Point(*glfw.get_cursor_pos(window))
			canvas.clear(self.background_color)
			self.sync_context_with_main()
			self.draw_frame()

			canvas.flush()
			glfw.swap_buffers(window)
			glfw.poll_events()
			context.FRAME += 1

		self.gpu_context.abandonContext()
		glfw.terminate()

	def change_size(self, width, height):
		glfw.set_window_size(self.window, width, height)

	def change_title(self, title):
		glfw.set_window_title(self.window, title)

	def change_background_color(self, background_color):
		self.background_color = background_color

	def key_callback(self, window, key, scancode, action, mods):
		name = self.KEY_NAMES[key]
		if action in (glfw.PRESS, glfw.REPEAT):
			self.call_from_main('on_key', [name])

	def mouse_button_callback(self, window, button, action, mods):
		name = self.MOUSE_NAMES[button]
		if action == glfw.PRESS:
			self.call_from_main('on_click', [name])

	def framebuffer_size_callback(self, window, width, height):
		old_w, old_h = self.drawy_module.WIDTH, self.drawy_module.HEIGHT
		self.reset_canvas_size(width, height)
		self.call_from_main('on_resize', [old_w, old_h])

	def monitor_callback(self, *args):
		self.drawy_module.REFRESH_RATE = glfw.get_video_mode(glfw.get_primary_monitor()).refresh_rate

	def draw_frame(self):
		try:
			self.main_module.draw()
		except:
			if not getattr(self, 'handled_exception', False):
				Drawer.print_last_traceback()
				self.handled_exception = True

	def sync_context_with_main(self):
		for name in self.drawy_vars:
			self.main_module.__dict__[name] = self.drawy_module.__dict__[name]

	def reload_main_if_modified(self):
		if time() - self.last_reload < self.RELOAD_INTERVAL:
			return
		self.last_reload = time()
		if self.check_is_file_modified(self.main_path):
			try:
				self.reload_module(self.main_module)
				self.handled_exception = False
				print("Reloaded!", file=sys.stderr)
			except:
				Drawer.print_last_traceback()

	def check_is_file_modified(self, file):
		mtime = os.path.getmtime(file)
		old_mtime = self.files_mtime.get(file, mtime)
		self.files_mtime[file] = mtime
		return mtime > old_mtime

	def reload_module(self, m: ModuleType):
		m.__loader__.exec_module(m)

	def reset_canvas_size(self, w, h):
		self.gpu_context, self.surface = Drawer.new_skia_context_surface(w, h)
		self.drawy_module._canvas = self.surface.getCanvas()
		self.drawy_module.WIDTH = w
		self.drawy_module.HEIGHT = h

	def call_from_main(self, fname: str, args: list, *, reraise=False):
		if not hasattr(self.main_module, fname):
			return

		f = getattr(self.main_module, fname)
		if not callable(f):
			return

		try:
			return f(*args[:f.__code__.co_argcount])
		except:
			Drawer.print_last_traceback()
			if reraise:
				raise sys.exc_info()[1]

	@staticmethod
	def print_last_traceback(*, hide_this_file=True):
		etype, value, tb = sys.exc_info()
		if hide_this_file:
			while tb and tb.tb_frame.f_code.co_filename.lower() == __file__.lower():
				tb = tb.tb_next
		traceback.print_exception(etype, value, tb)


	@staticmethod
	def new_skia_context_surface(w, h) -> (skia.GrDirectContext, skia.Surface):
		glContext = skia.GrDirectContext.MakeGL()
		fbInfo = skia.GrGLFramebufferInfo(0, 0x8058) # GL_RGBA8
		target = skia.GrBackendRenderTarget(w, h, 0, 0, fbInfo)

		surface = skia.Surface.MakeFromBackendRenderTarget(
			glContext, target,
			skia.GrSurfaceOrigin.kBottomLeft_GrSurfaceOrigin,
			skia.ColorType.kRGBA_8888_ColorType, None)
		return glContext, surface
