from __future__ import annotations
import skia
import math
import sys
from .drawer import Drawer

FRAME: int = 0
MOUSE_POSITION: Point = None
WIDTH: int = 1
HEIGHT: int = 1
REFRESH_RATE: int = 1

class Global: pass
g = Global()

class Align:
	CENTER = 'center'
	LEFT = 'left'
	RIGHT = 'right'
	TOP = 'top'
	BOTTOM = 'bottom'

_canvas: skia.Canvas = None
_drawer: Drawer = None

def draw_rectangle(left_top: tuple[float, float], width: float, height: float, color, *, fill=True, border_thickness=8):
	if fill:
		border_thickness = 0
	x, y = left_top
	_canvas.drawRect(skia.Rect.MakeXYWH(x, y, width, height), Color._paint(color, fill, border_thickness))

def draw_square(left_top: tuple[float, float], side: float, color, *, fill=True, border_thickness=8):
	draw_rectangle(left_top, side, side, color, fill=fill, border_thickness=border_thickness)

def draw_circle(center: tuple[float, float], radius: float, color, *, fill=True, border_thickness=8):
	if fill:
		border_thickness = 0
	x, y = center
	_canvas.drawCircle(x, y, radius, Color._paint(color, fill, border_thickness))

def draw_line(start_point: tuple[float, float], end_point: tuple[float, float], color, *, thickness=8):
	x0, y0 = start_point
	x1, y1 = end_point
	_canvas.drawLine(x0, y0, x1, y1, Color._paint(color, True, thickness))

def draw_poligon(points: list[tuple[float, float]], color, *, fill=True, border_thickness=8):
	if fill:
		border_thickness = 0
	p = skia.Path()
	p.addPoly([skia.Point(*p) for p in points], close=True)
	_canvas.drawPath(p, Color._paint(color, fill, border_thickness))

def draw_triangle(point_1: tuple[float, float], point_2: tuple[float, float], point_3: tuple[float, float], color, *, fill=True, border_thickness=8):
	draw_poligon([point_1, point_2, point_3], color, fill=fill, border_thickness=border_thickness)

def draw_text(text: str, point: tuple[float, float], color, *, size=40, font='Arial', align_x=Align.CENTER, align_y=Align.CENTER):
	if align_x not in (Align.LEFT, Align.CENTER, Align.RIGHT):
		raise ValueError(f"align_x bad value {align_x!r}.\nValid values are: {', '.join(map(repr, [Align.LEFT, Align.CENTER, Align.RIGHT]))}.")
	if align_y not in (Align.TOP, Align.CENTER, Align.BOTTOM):
		raise ValueError(f"align_y bad value {align_x!r}.\nValid values are: {', '.join(map(repr, [Align.TOP, Align.CENTER, Align.BOTTOM]))}.")

	try:
		cache = globals()['_text_cache']
	except:
		cache = globals()['_text_cache'] = {}
	try:
		blob, offsets = cache[(text, font, size)]
	except:
		sfont = skia.Font(skia.Typeface(font), size)
		blob: skia.TextBlob = skia.TextBlob.MakeFromText(text, sfont)
		glyphs = sfont.textToGlyphs(text)
		bounds = sfont.getBounds(glyphs)
		positions = sfont.getXPos(glyphs)
		min_y = min(-b.fBottom for b in bounds)
		max_y = max(-b.fTop for b in bounds)
		# take the average of the centers as the text center
		center_y = sum(-b.centerY() for b in bounds) / len(bounds)
		min_x = positions[0] + bounds[0].fLeft
		max_x = positions[-1] + bounds[-1].fRight
		center_x = (min_x + max_x) / 2
		offsets = {'min_x': min_x, 'center_x': center_x, 'max_x': max_x, 'min_y': min_y, 'center_y': center_y, 'max_y': max_y}
		cache[(text, font, size)] = blob, offsets

	x, y = point
	if align_x == 'left':
		x -= offsets['max_x']
	elif align_x == 'center':
		x -= offsets['center_x']
	elif align_x == 'right':
		x -= offsets['min_x']
	if align_y == 'bottom':
		y += offsets['max_y']
	elif align_y == 'center':
		y += offsets['center_y']
	elif align_y == 'top':
		y += offsets['min_y']

	_canvas.drawTextBlob(blob, x, y, Color._paint(color))
	# w = offsets['max_x'] - offsets['min_x']
	# h = offsets['max_y'] - offsets['min_y']
	# draw_rectangle((x + offsets['min_x'], y - offsets['max_y']), w, h, 'red', fill=False, border_thickness=1)

def draw_image(file_name: str, left_top: tuple[float, float], width: float, height: float):
	try:
		cache = globals()['_image_cache']
	except:
		cache = globals()['_image_cache'] = {}
	if file_name in cache:
		img = cache[file_name]
	else:
		img = skia.Image.open(file_name)
		cache[file_name] = img
	x, y = left_top
	_canvas.drawImageRect(img, skia.Rect.MakeXYWH(x, y, width, height))

def is_key_pressed(key):
	return _drawer.is_key_pressed(key)

def is_mouse_pressed(button='left'):
	return _drawer.is_mouse_pressed(button)

class Color:
	Transparent = skia.ColorTRANSPARENT
	Black = skia.ColorBLACK
	DarkGray = skia.ColorDKGRAY
	Gray = skia.ColorGRAY
	LightGray = skia.ColorLTGRAY
	White = skia.ColorWHITE
	Red = skia.ColorRED
	Green = skia.ColorGREEN
	Blue = skia.ColorBLUE
	Yellow = skia.ColorYELLOW
	Cyan = skia.ColorCYAN
	Magenta = skia.ColorMAGENTA

	_color_names = {
		'transparent': Transparent,
		'black': Black,
		'darkgray': DarkGray,
		'gray': Gray,
		'lightgray': LightGray,
		'white': White,
		'red': Red,
		'green': Green,
		'blue': Blue,
		'yellow': Yellow,
		'cyan': Cyan,
		'magenta': Magenta,
	}

	_cache = {}

	@staticmethod
	def from_hsv(h, s, v, alpha=255):
		return skia.HSVToColor([h, s, v], alpha)

	@staticmethod
	def _from_name(name: str) -> int:
		return Color._color_names[name]

	@staticmethod
	def _from_hex(color_hex: str) -> int:
		color_hex = color_hex.lstrip('#')
		if len(color_hex) in (3, 4):
			color_hex = ''.join(c+c for c in color_hex)
		assert len(color_hex) in (6, 8), f"The length of color_hex must be 3, 4, 6 or 8, not {len(color_hex)}."

		channels = [int(color_hex[i:i+2], 16) for i in range(0, len(color_hex), 2)]
		if len(channels) == 3:
			channels.append(255)
		return skia.Color(*channels)


	@staticmethod
	def _from_whatever(x) -> int:
		if isinstance(x, str):
			return Color._from_hex(x) if x.startswith('#') else Color._from_name(x)
		elif isinstance(x, (tuple, list)):
			if len(x) == 4:
				return skia.Color(*x)
			else:
				return skia.Color(*x, 255)
		else:
			return x

	@staticmethod
	def _paint(x, fill=True, thickness=0) -> skia.Paint:
		style = skia.Paint.kStrokeAndFill_Style if fill else skia.Paint.kStroke_Style
		color = Color._from_whatever(x)
		cache_key = (color, fill, thickness)
		if cache_key not in Color._cache:
			p = skia.Paint(AntiAlias=True, StrokeWidth=thickness, Color=color, Style=style)
			Color._cache[cache_key] = p
			return p
		return Color._cache[cache_key]


class Point:
	def __init__(self, x: float, y: float):
		self.x = x
		self.y = y

	@property
	def magnitude(self) -> Point:
		return math.sqrt(self.x * self.x + self.y * self.y)

	@property
	def radians(self) -> float:
		return math.atan2(self.y, self.x)

	@property
	def degrees(self) -> float:
		return math.degrees(self.radians)

	def normalized(self) -> Point:
		return self / self.magnitude

	def as_int(self) -> Point:
		return Point(int(self.x), int(self.y))

	def is_inside_rectangle(self, left_top: Point, width: float, height: float):
		return 0 <= self.x - left_top[0] < width and 0 <= self.y - left_top[1] < height

	def is_inside_circle(self, center: Point, radius: float):
		return abs(self - Point(*center)).magnitude <= radius

	def __getitem__(self, key: int) -> float:
		if key == 0:
			return self.x
		elif key == 1:
			return self.y
		else:
			raise IndexError()

	def __iter__(self):
		yield self.x
		yield self.y

	def __eq__(self, other):
		if other is None or len(other) != 2:
			return NotImplemented
		x, y = other
		return self.x == x and self.y == y

	def __len__(self):
		return 2

	def __neg__(self):
		return Point(-self.x, -self.y)

	def __abs__(self):
		return Point(abs(self.x), abs(self.y))

	def _get_other_point(self, other):
		if isinstance(other, (Point, tuple, list)):
			assert len(other) == 2, f"The length of the {type(other).__name__} must be 2."
			return other
		else:
			return other, other

	def __add__(self, other) -> Point:
		x, y = self._get_other_point(other)
		return Point(self.x + x, self.y + y)

	def __radd__(self, other) -> Point:
		return self.__add__(other)

	def __sub__(self, other) -> Point:
		x, y = self._get_other_point(other)
		return Point(self.x - x, self.y - y)

	def __rsub__(self, other) -> Point:
		return Point(*other).__sub__(self)

	def __mul__(self, other) -> Point:
		x, y = self._get_other_point(other)
		return Point(self.x * x, self.y * y)

	def __rmul__(self, other) -> Point:
		return self.__mul__(other)

	def __truediv__(self, other) -> Point:
		x, y = self._get_other_point(other)
		return Point(self.x / x, self.y / y)

	def __rtruediv__(self, other) -> Point:
		return Point(*other).__truediv__(self)

	def __floordiv__(self, other) -> Point:
		x, y = self._get_other_point(other)
		return Point(self.x // x, self.y // y)

	def __rfloordiv__(self, other) -> Point:
		return Point(*other).__floordiv__(self)

	def __mod__(self, other) -> Point:
		x, y = self._get_other_point(other)
		return Point(self.x % x, self.y % y)

	def __rmod__(self, other) -> Point:
		return Point(*other).__mod__(self)

	def __str__(self):
		return f'Point(x={self.x}, y={self.y})'

def run(width=640, height=480, *, resizable=False, title="drawy", background_color=Color.White):
	global _drawer

	PROPS = '_DRAWER_PROPS'
	background_color = Color._from_whatever(background_color)
	if _drawer is not None:
		props = globals()[PROPS]
		if width != props['width'] or height != props['height']:
			props['width'], props['height'] = width, height
			_drawer.change_size(width, height)
		if title != props['title']:
			props['title'] = title
			_drawer.change_title(title)
		if background_color != props['background_color']:
			props['background_color'] = background_color
			_drawer.change_background_color(background_color)
	else:
		globals()[PROPS] = {'width': width, 'height': height, 'title': title, 'background_color': background_color}
		main_module = sys.modules['__main__']
		this_module = sys.modules[__name__]
		_drawer = Drawer(main_module, this_module)
		_drawer.run(width, height, resizable, title, background_color)
