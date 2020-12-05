from drawy import *
import random
from collections import deque

class Global:
    snake: deque[Point]
    apple: Point
    dir_queue: deque[Point]
    dir: Point
    status: str
g: Global

SIZE = 20
SQUARE_SIZE = WIDTH / SIZE
ALIVE_COLOR = (20, 220, 20)
DEAD_COLOR = (200, 30, 30)
APPLE_COLOR = (200, 20, 20)
BACKGROUND_COLOR = (20, 20, 20)
LINES_COLOR = (15, 15, 15)

UP = Point(0, -1)
DOWN = Point(0, 1)
LEFT = Point(-1, 0)
RIGHT = Point(1, 0)

def init():
    g.snake = deque()
    for i in range(3):
        g.snake.append(Point(SIZE, SIZE) // 2 + (i, 0))
    g.dir_queue = deque()
    g.dir = RIGHT
    g.status = 'alive'
    g.apple = g.snake[0]
    spawn_apple()

def spawn_apple():
    p = g.apple
    while p == g.apple or p in g.snake:
        p = Point(random.randrange(0, SIZE), random.randrange(0, SIZE))
    g.apple = p

def draw_block(p, color):
    draw_square(p * SQUARE_SIZE, SQUARE_SIZE, color)

def move():
    head = g.snake[-1]
    if g.dir_queue:
        g.dir = g.dir_queue.popleft()
    head += g.dir
    head %= SIZE

    if head == g.apple:
        spawn_apple()
    else:
        g.snake.popleft()

    if head in g.snake:
        g.status = 'dead'
    g.snake.append(head)

def draw():
    if FRAME % (REFRESH_RATE // 10) == 0 and g.status == 'alive':
        move()
    snake_color = ALIVE_COLOR if g.status == 'alive' else DEAD_COLOR

    for i, p in enumerate(reversed(g.snake)):
        draw_block(p, [*snake_color, 255 - i * 120 // len(g.snake)])
    draw_block(g.apple, APPLE_COLOR)

    for i in range(SIZE + 1):
        draw_line((i * SQUARE_SIZE, 0), (i * SQUARE_SIZE, HEIGHT), LINES_COLOR, thickness=2)
        draw_line((0, i * SQUARE_SIZE), (WIDTH, i * SQUARE_SIZE), LINES_COLOR, thickness=2)

    if g.status == 'dead':
        draw_rectangle((0, 0), WIDTH, HEIGHT, (200, 200, 200, 100))
        draw_text('Game Over', Point(HEIGHT, WIDTH) / 2, 'black', size=150)
        draw_text('(press SPACE to restart)', Point(HEIGHT, WIDTH + 150) / 2, 'black', size=30)

def on_key(key):
    last = g.dir_queue[-1] if g.dir_queue else g.dir
    if key == 'left' and last != RIGHT:
        g.dir_queue.append(LEFT)
    elif key == 'right' and last != LEFT:
        g.dir_queue.append(RIGHT)
    elif key == 'up' and last != DOWN:
        g.dir_queue.append(UP)
    elif key == 'down' and last != UP:
        g.dir_queue.append(DOWN)
    if key == ' ' and g.status == 'dead':
        init()


run(width=1000, height=1000, title='Snake', background_color=BACKGROUND_COLOR)