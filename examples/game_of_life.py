from drawy import *
import random

SIZE = 25
SQUARE_SIZE = WIDTH / SIZE
DEAD_COLOR = (20, 20, 20)
ALIVE_COLOR = (20, 220, 20)
LINE_COLOR = (15, 15, 15)

class Global:
    cells: list[list[bool]]
    status: list[list[bool]]
    pause: bool
    click_status: bool
g: Global

def randomize_cells():
    g.cells = [[random.choice((True, False)) for _ in range(SIZE)] for _ in range(SIZE)]

def clear_cells():
    g.cells = [[False] * SIZE for _ in range(SIZE)]

def init():
    randomize_cells()
    g.status = [[False] * SIZE for _ in range(SIZE)]
    g.pause = False
    g.click_status = None

def draw_block(p, color):
    draw_square(p * SQUARE_SIZE, SQUARE_SIZE, color)

def logic():
    for x in range(SIZE):
        for y in range(SIZE):
            count = 0
            for dx, dy in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):
                count += g.cells[(x + dx) % SIZE][(y + dy) % SIZE]
            if g.cells[x][y]:
                g.status[x][y] = count in (2, 3)
            else:
                g.status[x][y] = count == 3
    g.cells, g.status = g.status, g.cells

def draw():
    if not g.pause and FRAME % (REFRESH_RATE // 10) == 0:
        logic()
    if is_mouse_pressed():
        x, y = (MOUSE_POSITION / SQUARE_SIZE).as_int()
        if g.click_status is None:
            g.click_status = not g.cells[x][y]
        g.cells[x][y] = g.click_status
    else:
        g.click_status = None


    for x in range(SIZE):
        for y in range(SIZE):
            if g.cells[x][y]:
                draw_block(Point(x, y), ALIVE_COLOR)

    for i in range(SIZE + 1):
        draw_line((i * SQUARE_SIZE, 0), (i * SQUARE_SIZE, HEIGHT), LINE_COLOR, thickness=2)
        draw_line((0, i * SQUARE_SIZE), (WIDTH, i * SQUARE_SIZE), LINE_COLOR, thickness=2)

    if g.pause:
        draw_text("P", (WIDTH-8, 10), 'white', align_x='left', align_y='bottom')

def on_key(key):
    if key == ' ':
        g.pause = not g.pause
    elif key == 'c':
        clear_cells()
    elif key == 'r':
        randomize_cells()

run(width=1000, height=1000, title="Game of Life", background_color=DEAD_COLOR)