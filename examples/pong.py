from drawy import *
from typing import List
import random

PADDLE_HEIGHT = 150
PADDLE_WIDTH = 20
BALL_SIZE = 15
INITIAL_SPEED = 500 / REFRESH_RATE
SPEED_INCREMENT = 0.1
FOREGROUND = 'white'

class Global:
    ball: Point
    paddles: List[Point]
    dir: Point
    scores: List[int]
    speed: float
g: Global

def init():
    reset_ball()
    g.paddles = [Point(PADDLE_WIDTH / 2, HEIGHT / 2), Point(WIDTH - 1 - PADDLE_WIDTH / 2, HEIGHT / 2)]
    g.scores = [0, 0]

def reset_ball():
    g.ball = Point(WIDTH, HEIGHT) / 2
    g.dir = Point(random.choice((-1, 1)), random.choice((-1, 1))).normalized()
    g.speed = INITIAL_SPEED

def update():
    movement = INITIAL_SPEED
    if is_key_pressed('7') or is_key_pressed('q'):
        g.paddles[0].y -= movement
    elif is_key_pressed('4') or is_key_pressed('a'):
        g.paddles[0].y += movement
    elif is_key_pressed('9') or is_key_pressed('o'):
        g.paddles[1].y -= movement
    elif is_key_pressed('6') or is_key_pressed('l'):
        g.paddles[1].y += movement

    for p in g.paddles:
        p.y %= HEIGHT

    g.ball += g.dir * g.speed
    
    if g.ball.y - BALL_SIZE <= 0 or g.ball.y + BALL_SIZE >= HEIGHT:
        g.dir.y *= -1

    if g.ball.x + BALL_SIZE >= WIDTH:
        g.scores[0] += 1
        reset_ball()
    elif g.ball.x - BALL_SIZE <= 0:
        g.scores[1] += 1
        reset_ball()
    
    DW = PADDLE_WIDTH / 2
    DH = PADDLE_HEIGHT / 2
    if g.dir.x > 0:
        p = g.paddles[1]
    else:
        p = g.paddles[0]
    d = abs(p - g.ball) - BALL_SIZE - (DW, DH)
    if d.y <= 0 and d.x <= 0:
        g.dir.x *= -1
        g.dir.y -= (p.y - g.ball.y) / DH / 2
        g.dir = g.dir.normalized()
        g.speed += SPEED_INCREMENT

def draw():
    update()
    draw_line((WIDTH / 2, 0), (WIDTH / 2, HEIGHT), FOREGROUND)

    for i, s in enumerate(g.scores):
        draw_text(str(s), (WIDTH / 2 - 80 + 160 * i, 60), FOREGROUND, size=80)
    
    for p in g.paddles:
        draw_rectangle(p - Point(PADDLE_WIDTH, PADDLE_HEIGHT) / 2, PADDLE_WIDTH, PADDLE_HEIGHT, FOREGROUND)
    
    draw_circle(g.ball, PADDLE_WIDTH, FOREGROUND)


run(width=900, height=500, title="Pong", background_color='black')