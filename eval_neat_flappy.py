import neat
import pickle
import time
import argparse
import os
import sys
import numpy as np
CURRENT_GENERATION = 0

class GenerationReporter(neat.reporting.BaseReporter):
    def start_generation(self, generation):
        global CURRENT_GENERATION
        CURRENT_GENERATION = generation

from flappy_game import FlappyGame, Bird, PIPE_SPEED, PIPE_WIDTH, WINDOW_W, WINDOW_H, GROUND_Y, PIPE_GAP

try:
    import pygame
    PYGAME_AVAILABLE = True
except Exception:
    PYGAME_AVAILABLE = False
def eval_genomes(genomes, config, render=False, save_frames=False, frame_dir="frames", frame_skip=2):
    print("[DEBUG] eval_genomes called. #genomes =", len(genomes))
    sys.stdout.flush()

    game = FlappyGame(render=False)
    nets = []
    birds = []
    ge = []

    for gid, genome in genomes:
        genome.fitness = 0.0
        nets.append(neat.nn.FeedForwardNetwork.create(genome, config))
        birds.append(game.spawn_bird())
        ge.append(genome)

    print(f"[DEBUG] Spawned {len(birds)} birds. pipes={len(game.pipes)}")
    sys.stdout.flush()

    clock = None
    screen = None
    font = None
    if render and PYGAME_AVAILABLE:
        pygame.init()
        screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        clock = pygame.time.Clock()
        font = pygame.font.SysFont("Arial", 18)
        print("[DEBUG] Pygame window opened.")
        sys.stdout.flush()
    elif render and not PYGAME_AVAILABLE:
        print("[DEBUG] Render requested but pygame not available.")
        sys.stdout.flush()

    if save_frames:
        os.makedirs(frame_dir, exist_ok=True)
        frame_count = 0

    steps = 0
    MAX_STEPS = 2000
    while len(birds) > 0 and steps < MAX_STEPS:
        steps += 1
        if steps % 100 == 0:
            print(f"[DEBUG] steps={steps}, alive={len(birds)}, pipes={len(game.pipes)}")
            sys.stdout.flush()

        if render and PYGAME_AVAILABLE:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    print("[DEBUG] Quit event received. Exiting eval loop.")
                    sys.stdout.flush()
                    pygame.quit()
                    return

        to_kill = []
        for i, bird in enumerate(list(birds)): 
            pipe = game.next_pipe_for_bird(bird)
            inputs = np.array([bird.y / WINDOW_H,
                               bird.vy / 20.0,
                               (pipe.x - bird.x) / WINDOW_W,
                               (pipe.gap_y - bird.y) / WINDOW_H,
                               (PIPE_SPEED) / 10.0])
            outputs = nets[i].activate(inputs)
            flap = outputs[0] > 0.5
            bird.apply_action(flap)
            bird.step()

            ge[i].fitness += 0.05

            if pipe.collides_with(bird):
                print(f"[DEBUG] Collision: bird_id={id(bird)} at x={bird.x:.1f}, y={bird.y:.1f} with pipe x={pipe.x:.1f}")
                sys.stdout.flush()
                try:
                    idx = birds.index(bird)
                except ValueError:
                    idx = None
                if idx is not None:
                    to_kill.append(idx)
                ge[i].fitness -= 1.0
                continue  

            bird_id = id(bird)
            if (bird.x > pipe.x + PIPE_WIDTH) and (bird_id not in pipe.passed_birds):
                ge[i].fitness += 5.0
                pipe.passed_birds.add(bird_id)
                bird.score += 1
                print(f"[DEBUG] Pass: bird_id={bird_id} score={bird.score} (pipe.x={pipe.x:.1f})")
                sys.stdout.flush()

            if bird.is_offscreen_or_ground():
                print(f"[DEBUG] Offscreen/ground: bird_id={id(bird)} y={bird.y:.1f}")
                sys.stdout.flush()
                try:
                    idx = birds.index(bird)
                except ValueError:
                    idx = None
                if idx is not None:
                    to_kill.append(idx)

        if to_kill:
            print(f"[DEBUG] Killing {len(to_kill)} birds at step {steps}.")
            sys.stdout.flush()

        for idx in reversed(sorted(set(to_kill))):
            birds.pop(idx)
            nets.pop(idx)
            ge.pop(idx)

        game.tick()

        if render and PYGAME_AVAILABLE:
            screen.fill((135, 206, 235))  
            for p in game.pipes:
                top_rect = pygame.Rect(p.x, 0, PIPE_WIDTH, p.gap_y - PIPE_GAP//2)
                bot_top = p.gap_y + PIPE_GAP//2
                bot_rect = pygame.Rect(p.x, bot_top, PIPE_WIDTH, GROUND_Y - bot_top)
                pygame.draw.rect(screen, (34,139,34), top_rect)
                pygame.draw.rect(screen, (34,139,34), bot_rect)
            for b in birds:
                bx, by, bw, bh = b.rect()
                pygame.draw.rect(screen, (255,255,0), pygame.Rect(bx, by, bw, bh))
            pygame.draw.rect(screen, (222,184,135), pygame.Rect(0, GROUND_Y, WINDOW_W, WINDOW_H - GROUND_Y))
            if font:
                txt = font.render(f"Alive: {len(birds)}  Steps: {steps}", True, (0,0,0))
                screen.blit(txt, (8, 8))
                gen_txt = font.render(f"Gen: {CURRENT_GENERATION}", True, (0,0,0))
                screen.blit(gen_txt, (8, 30))
                

            pygame.display.flip()
            clock.tick(60)

        if save_frames and PYGAME_AVAILABLE:
            if steps % frame_skip == 0:
                surf = pygame.Surface((WINDOW_W, WINDOW_H))
                surf.fill((135,206,235))
                for p in game.pipes:
                    top_rect = pygame.Rect(p.x, 0, PIPE_WIDTH, p.gap_y - PIPE_GAP//2)
                    bot_top = p.gap_y + PIPE_GAP//2
                    bot_rect = pygame.Rect(p.x, bot_top, PIPE_WIDTH, GROUND_Y - bot_top)
                    pygame.draw.rect(surf, (34,139,34), top_rect)
                    pygame.draw.rect(surf, (34,139,34), bot_rect)
                for b in birds:
                    bx, by, bw, bh = b.rect()
                    pygame.draw.rect(surf, (255,255,0), pygame.Rect(bx, by, bw, bh))
                pygame.draw.rect(surf, (222,184,135), pygame.Rect(0, GROUND_Y, WINDOW_W, WINDOW_H - GROUND_Y))
                filename = os.path.join(frame_dir, f"frame_{steps:05d}.png")
                pygame.image.save(surf, filename)

    print(f"[DEBUG] eval_genomes finished: steps={steps}, alive={len(birds)}")
    sys.stdout.flush()
    return

def run(config_file, generations=30, render=False, headless_frames=False):
    print(f"[DEBUG] Starting run; config={config_file}, gens={generations}, render={render}, frames={headless_frames}")
    sys.stdout.flush()
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)
    print("[DEBUG] Config parsed.")
    sys.stdout.flush()

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(GenerationReporter()) 
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    print("[DEBUG] Population created. pop_size:", config.pop_size)
    sys.stdout.flush()

    def eval_wrapper(genomes, config_inner):
        return eval_genomes(genomes, config_inner, render=render, save_frames=headless_frames, frame_dir="frames")

    winner = p.run(eval_wrapper, generations)
    print("[DEBUG] p.run finished. winner saved next.")
    sys.stdout.flush()

    with open("winner.pkl", "wb") as f:
        pickle.dump(winner, f)
    print("Winner saved to winner.pkl")
    with open("stats.pkl", "wb") as f:
        pickle.dump(stats, f)
    print("[DEBUG] stats saved to stats.pkl")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="neat-config.cfg")
    parser.add_argument("--gens", type=int, default=30)
    parser.add_argument("--render", action="store_true", help="Open pygame window (local only).")
    parser.add_argument("--frames", action="store_true", help="Save frames into ./frames (for Colab/Video). Requires pygame.")
    args = parser.parse_args()
    run(args.config, generations=args.gens, render=args.render, headless_frames=args.frames)
