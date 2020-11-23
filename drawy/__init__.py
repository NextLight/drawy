import skia
import sys
from typing import Tuple, List
from .canvas import Canvas as _Canvas

FRAME: int = 0
MOUSE_POSITION: Tuple[float, float] = (0., 0.)
HEIGHT: int = 0
WIDTH: int = 0

_canvas: skia.Canvas = None

def draw_rectangle(left_top: Tuple[float, float], width: float, height: float, color, *, fill=True, border_thickness=8):
	if fill:
		border_thickness = 0
	x, y = left_top
	_canvas.drawRect(skia.Rect.MakeXYWH(x, y, width, height), Color._paint(color, fill, border_thickness))

def draw_square(left_top: Tuple[float, float], side: float, color, *, fill=True, border_thickness=8):
	draw_rectangle(left_top, side, side, color, fill=fill, border_thickness=border_thickness)

def draw_circle(center: Tuple[float, float], radius: float, color, *, fill=True, border_thickness=8):
	if fill:
		border_thickness = 0
	x, y = center
	_canvas.drawCircle(x, y, radius, Color._paint(color, fill, border_thickness))

def draw_line(start_point: Tuple[float, float], end_point: Tuple[float, float], color, *, thickness=8):
	x0, y0 = start_point
	x1, y1 = end_point
	_canvas.drawLine(x0, y0, x1, y1, Color._paint(color, True, thickness))

def draw_poligon(points: List[Tuple[float, float]], color, *, fill=True, border_thickness=8):
	if fill:
		border_thickness = 0
	p = skia.Path()
	p.addPoly([skia.Point(*p) for p in points], close=True)
	_canvas.drawPath(p, Color._paint(color, fill, border_thickness))

def draw_triangle(p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float], color, *, fill=True, border_thickness=8):
	draw_poligon([p1, p2, p3], color, fill=fill, border_thickness=border_thickness)

def draw_text(text: str, point: Tuple[float, float], color, size=40, font='Arial'):
	x, y = point
	_canvas.drawSimpleText(text, x, y, skia.Font(skia.Typeface(font), size), Color._paint(color))

def draw_image(file_name: str, left_top: Tuple[float, float], width: float, height: float):
	if '_images_cache' not in globals():
		globals()['_images_cache'] = {}
	if file_name in _images_cache:
		img = _images_cache[file_name]
	else:
		img = skia.Image.open(file_name)
		_images_cache[file_name] = img
	x, y = left_top
	_canvas.drawImageRect(img, skia.Rect.MakeXYWH(x, y, width, height))

class Global: pass
g = Global()

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
	def _from_string(name: str) -> int:
		return Color._color_names[name]

	@staticmethod
	def _from_whatever(x) -> int:
		if isinstance(x, str):
			return Color._from_string(x)
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

def run(width=640, height=480, *, resizable=False, title="drawy", background_color=Color.White):
	ALREADY_RUN = '_DRAWY_RUN_'
	if ALREADY_RUN in globals():
		return
	globals()[ALREADY_RUN] = True

	main_module = sys.modules['__main__']
	this_module = sys.modules[__name__]

	background_color = Color._from_whatever(background_color)
	_Canvas(main_module, this_module).run(width, height, resizable, title, background_color)
