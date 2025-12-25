import random
import math

WINDOW_W = 288
WINDOW_H = 512
GROUND_Y = 450

PIPE_WIDTH = 52
PIPE_GAP = 100
PIPE_X_SPACING = 200  
PIPE_SPEED = 3

GRAVITY = 0.8
FLAP_V = -9.0
MAX_VY = 12.0

class Bird:
    def __init__(self, x=60, y=WINDOW_H//2):
        self.x = x
        self.y = y
        self.vy = 0.0
        self.alive = True
        self.score = 0
        self.passed = False

    def apply_action(self, flap: bool):
        if flap:
            self.vy = FLAP_V

    def step(self):
        self.vy += GRAVITY
        if self.vy > MAX_VY:
            self.vy = MAX_VY
        self.y += self.vy

    def rect(self):
        size = 24
        return (self.x - size//2, int(self.y - size//2), size, size)

    def is_offscreen_or_ground(self):
        if self.y > GROUND_Y - 10:
            return True
        if self.y < 0:
            return True
        return False

class Pipe:
    def __init__(self, x):
        self.x = x
        margin = 60
        self.gap_y = random.randint(margin + PIPE_GAP//2, GROUND_Y - margin - PIPE_GAP//2)
        self.passed_birds = set()

    def step(self):
        self.x -= PIPE_SPEED

    def collides_with(self, bird: Bird):
        bx, by, bw, bh = bird.rect()
        top_h = self.gap_y - PIPE_GAP//2
        bottom_y = self.gap_y + PIPE_GAP//2
        if bx + bw > self.x and bx < self.x + PIPE_WIDTH:
            if by < top_h or by + bh > bottom_y:
                return True
        return False

class FlappyGame:

    def __init__(self, render=False):
        self.render_mode = render
        self.reset()

    def reset(self):
        self.birds = []
        self.pipes = []
        self.t = 0
        self.next_pipe_x = WINDOW_W + 40
        for i in range(3):
            p = Pipe(self.next_pipe_x + i * PIPE_X_SPACING)
            self.pipes.append(p)

    def spawn_bird(self):
        b = Bird()
        self.birds.append(b)
        return b

    def next_pipe_for_bird(self, bird):
        for p in self.pipes:
            if p.x + PIPE_WIDTH > bird.x - 10:
                return p
        return self.pipes[-1]

    def step(self):
        for p in self.pipes:
            p.step()
        if len(self.pipes) and self.pipes[0].x + PIPE_WIDTH < -50:
            self.pipes.pop(0)
            new_x = self.pipes[-1].x + PIPE_X_SPACING
            self.pipes.append(Pipe(new_x))
        self.t += 1

    def tick(self):
        self.step()

    def summary(self):
        return {
            "t": self.t,
            "num_birds": len(self.birds),
            "num_pipes": len(self.pipes),
        }
