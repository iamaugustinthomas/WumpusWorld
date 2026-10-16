import pygame
import sys
from world import WumpusEnvironment
from agent import LogicAgent

# --- Constants & Settings ---
GRID_SIZE = 4
TILE_SIZE = 150
WINDOW_SIZE = GRID_SIZE * TILE_SIZE
FPS = 30

# Colors
COLOR_BG = (30, 30, 30)
COLOR_UNVISITED = (50, 50, 50)
COLOR_VISITED = (200, 200, 200)
COLOR_SAFE = (150, 255, 150)
COLOR_LINE = (100, 100, 100)
COLOR_TEXT = (0, 0, 0)
COLOR_AGENT = (0, 150, 255)
COLOR_WUMPUS = (200, 50, 50)
COLOR_PIT = (20, 20, 20)
COLOR_GOLD = (255, 215, 0)

pygame.init()
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Wumpus World - Predicate Calculus Agent")
clock = pygame.time.Clock()
font = pygame.font.SysFont('arial', 24, bold=True)
small_font = pygame.font.SysFont('arial', 14)


def map_coords(x: int, y: int):
    """Maps Wumpus Cartesian (1-4, 1-4) to Pygame screen coordinates (col, row)."""
    col = x - 1
    row = GRID_SIZE - y  # y=1 is at the bottom
    return col, row


def draw_grid(env, agent, message):
    screen.fill(COLOR_BG)

    for x in range(1, GRID_SIZE + 1):
        for y in range(1, GRID_SIZE + 1):
            col, row = map_coords(x, y)
            rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)

            # Determine tile color based on agent's knowledge
            if (x, y) in agent.visited:
                pygame.draw.rect(screen, COLOR_VISITED, rect)
            elif agent.kb.ask_is_safe(x, y):
                pygame.draw.rect(screen, COLOR_SAFE, rect)
            else:
                pygame.draw.rect(screen, COLOR_UNVISITED, rect)

            pygame.draw.rect(screen, COLOR_LINE, rect, 2)

            # Draw Ground Truth Entities (Only if visited or game over, but for demo we show visited)
            if (x, y) in agent.visited:
                # Percepts
                percepts = env.get_percept(x, y)
                percept_texts = []
                if percepts["breeze"]: percept_texts.append("Breeze")
                if percepts["stench"]: percept_texts.append("Stench")
                
                for i, p_txt in enumerate(percept_texts):
                    txt_surface = small_font.render(p_txt, True, (100, 0, 100))
                    screen.blit(txt_surface, (rect.x + 5, rect.y + 5 + (i * 15)))

            # Draw Hazard Overlays (Revealing true environment)
            center_x, center_y = rect.x + TILE_SIZE // 2, rect.y + TILE_SIZE // 2
            
            if (x, y) in env.pits:
                pygame.draw.circle(screen, COLOR_PIT, (center_x, center_y), 30)
                screen.blit(font.render("PIT", True, (255, 255, 255)), (center_x - 15, center_y - 12))
            
            if (x, y) == env.wumpus:
                pygame.draw.circle(screen, COLOR_WUMPUS, (center_x, center_y), 30)
                screen.blit(font.render("WUMPUS", True, (255, 255, 255)), (center_x - 40, center_y - 12))
                
            if (x, y) == env.gold:
                pygame.draw.polygon(screen, COLOR_GOLD, [
                    (center_x, center_y - 30), (center_x - 20, center_y + 20), (center_x + 20, center_y + 20)
                ])
                screen.blit(font.render("GOLD", True, (0, 0, 0)), (center_x - 25, center_y - 10))

            # Draw Agent
            if (x, y) == agent.current_pos:
                pygame.draw.circle(screen, COLOR_AGENT, (center_x, center_y), 20)
                screen.blit(font.render("A", True, (255, 255, 255)), (center_x - 8, center_y - 12))

    # Draw Status Message at bottom
    msg_surface = font.render(message, True, (255, 255, 255), (0, 0, 0))
    screen.blit(msg_surface, (10, WINDOW_SIZE - 40))

    pygame.display.flip()


def main():
    env = WumpusEnvironment()
    agent = LogicAgent(size=GRID_SIZE)
    
    status_message = "Press SPACE to Step"
    game_over = False

    draw_grid(env, agent, status_message)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not game_over:
                x, y = agent.current_pos
                percepts = env.get_percept(x, y)

                if percepts["glitter"]:
                    status_message = f"WIN! Gold found at ({x}, {y})!"
                    agent.has_gold = True
                    game_over = True
                else:
                    # Update Logic KB
                    agent.perceive_and_tell(percepts)
                    next_pos = agent.choose_next_move()

                    if next_pos is None:
                        status_message = "Stymied. No safe moves left."
                        game_over = True
                    else:
                        status_message = f"Logic proved {next_pos} safe. Moving..."
                        agent.current_pos = next_pos

                draw_grid(env, agent, status_message)

        clock.tick(FPS)

if __name__ == "__main__":
    main()