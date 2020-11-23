import skia
import glfw
import os
import traceback
from time import time

class Canvas:
	RELOAD_INTERVAL = 0.2
	def __init__(self, main_module, drawy_module):
		self.main_module = main_module
		self.drawy_module = drawy_module
		self.main_path = main_module.__file__
		self.files_mtime = {}
		self.last_reload = time()
		self.drawy_vars = [n for n in dir(self.drawy_module) if n.isupper() and n[0] != '_']
		print(self.drawy_vars)

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
				self.KEY_NAMES[v] = name.lower()
			elif n.startswith('MOUSE_BUTTON_'):
				self.MOUSE_NAMES[v] = n[13:].lower()

	def run(self, width, height, resizable, title, background_color):
		self.init_glfw()
		glfw.window_hint(glfw.RESIZABLE, resizable)
		window = glfw.create_window(width, height, title, None, None)
		glfw.make_context_current(window)
		glfw.swap_interval(1) # vsync

		glfw.set_key_callback(window, self.key_callback)
		glfw.set_mouse_button_callback(window, self.mouse_button_callback)
		glfw.set_framebuffer_size_callback(window, self.framebuffer_size_callback)

		self.reset_canvas_size(*glfw.get_framebuffer_size(window))

		context = self.drawy_module
		context.FRAME = 0
		self.call_main_function('init', [])

		while not glfw.window_should_close(window):
			canvas = context._canvas
			context.MOUSE_POSITION = tuple(glfw.get_cursor_pos(window))
			canvas.clear(background_color)
			self.reload_main_if_modified()
			self.sync_context_with_main()
			self.draw_frame()

			context.FRAME += 1
			canvas.flush()

			glfw.swap_buffers(window)
			glfw.poll_events()

		canvas.getGrContext().abandonContext()
		glfw.terminate()

	def key_callback(self, window, key, scancode, action, mods):
		name = self.KEY_NAMES[key]
		if action in (glfw.PRESS, glfw.REPEAT):
			self.call_main_function('on_key', [name])

	def mouse_button_callback(self, window, button, action, mods):
		name = self.MOUSE_NAMES[button]
		if action == glfw.PRESS:
			self.call_main_function('on_click', [name])

	def framebuffer_size_callback(self, window, width, height):
		self.reset_canvas_size(width, height)

	def draw_frame(self):
		try:
			self.main_module.draw()
			self.handled_exception = False
		except:
			if not getattr(self, 'handled_exception', False):
				traceback.print_exc()
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
			except:
				traceback.print_exc()

	def check_is_file_modified(self, file):
		mtime = os.path.getmtime(file)
		old_mtime = self.files_mtime.get(file, mtime)
		self.files_mtime[file] = mtime
		return mtime > old_mtime

	def reload_module(self, m):
		m.__loader__.exec_module(m)

	def reset_canvas_size(self, w, h):
		self.drawy_module._canvas = Canvas.new_skia_canvas(w, h)
		self.drawy_module.WIDTH = w
		self.drawy_module.HEIGHT = h

	def call_main_function(self, fname, args):
		if hasattr(self.main_module, fname):
			try:
				f = getattr(self.main_module, fname)
				return f(*args[:f.__code__.co_argcount])
			except:
				traceback.print_exc()

	@staticmethod
	def new_skia_canvas(w, h):
		glContext = skia.GrDirectContext.MakeGL()
		fbInfo = skia.GrGLFramebufferInfo(0, 0x8058) # GL_RGBA8
		target = skia.GrBackendRenderTarget(w, h, 0, 0, fbInfo)

		surface = skia.Surface.MakeFromBackendRenderTarget(
			glContext, target, 
			skia.GrSurfaceOrigin.kBottomLeft_GrSurfaceOrigin,
			skia.ColorType.kRGBA_8888_ColorType, None)
		surface
		return surface.getCanvas()
