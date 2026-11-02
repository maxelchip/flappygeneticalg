"""Play Flappy Bird manually with the shared game physics."""

import sys

try:
    import pygame
except ImportError:
    pygame = None

from flappy_game import (
    GROUND_Y,
    PIPE_GAP,
    PIPE_WIDTH,
    WINDOW_H,
    WINDOW_W,
    FlappyGame,
)


SKY_BLUE = (135, 206, 235)
PIPE_GREEN = (34, 139, 34)
GROUND_BROWN = (222, 184, 135)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)


def draw_game(screen, game, bird, font, score, game_over):
    screen.fill(SKY_BLUE)

    for pipe in game.pipes:
        top_height = pipe.gap_y - PIPE_GAP // 2
        bottom_y = pipe.gap_y + PIPE_GAP // 2
        pygame.draw.rect(screen, PIPE_GREEN, (pipe.x, 0, PIPE_WIDTH, top_height))
        pygame.draw.rect(
            screen,
            PIPE_GREEN,
            (pipe.x, bottom_y, PIPE_WIDTH, GROUND_Y - bottom_y),
        )

    bird_x, bird_y, bird_width, bird_height = bird.rect()
    pygame.draw.rect(
        screen,
        YELLOW,
        (bird_x, bird_y, bird_width, bird_height),
    )
    pygame.draw.rect(
        screen,
        GROUND_BROWN,
        (0, GROUND_Y, WINDOW_W, WINDOW_H - GROUND_Y),
    )

    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (8, 8))

    if game_over:
        message = font.render("Game over - press SPACE to restart", True, BLACK)
        screen.blit(message, message.get_rect(center=(WINDOW_W // 2, WINDOW_H // 2)))


def reset_game():
    game = FlappyGame()
    return game, game.spawn_bird(), 0, False


def run():
    if pygame is None:
        print("Pygame is required. Install dependencies with: pip install -r requirements.txt")
        return 1

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("Flappy Bird")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18)
    game, bird, score, game_over = reset_game()
    running = True

    while running:
        flap = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP):
                    if game_over:
                        game, bird, score, game_over = reset_game()
                    else:
                        flap = True
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                flap = True

        if not game_over:
            bird.apply_action(flap)
            bird.step()
            pipe = game.next_pipe_for_bird(bird)

            if pipe.collides_with(bird) or bird.is_offscreen_or_ground():
                bird.alive = False
                game_over = True
            elif bird.x > pipe.x + PIPE_WIDTH and id(bird) not in pipe.passed_birds:
                pipe.passed_birds.add(id(bird))
                score += 1

            game.tick()

        draw_game(screen, game, bird, font, score, game_over)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(run())
