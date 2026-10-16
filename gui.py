import pygame
import sys
from world import WumpusEnvironment
from agent import LogicAgent

GRID_SIZE = 4
TILE_SIZE = 150
WINDOW_SIZE = GRID_SIZE * TILE_SIZE
FPS = 30

COLOR_BG = (30, 30, 30)
COLOR_UNVISITED = (50, 50, 50)
COLOR_VISITED = (200, 200, 200)
COLOR_SAFE = (150, 255, 150)
COLOR_LINE = (100, 100, 100)
COLOR_AGENT = (0, 150, 255)
COLOR_WUMPUS = (200, 50, 50)
COLOR_PIT = (20, 20, 20)
COLOR_GOLD = (255, 215, 0)

pygame.init()
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Wumpus World Logic")
clock = pygame.time.Clock()
font = pygame.font.SysFont('arial', 24, bold=True)
small_font = pygame.font.SysFont('arial', 14)

def map_coords(x: int, y: int):
    return x - 1, GRID_SIZE - y

def draw_grid(env, agent, message):
    screen.fill(COLOR_BG)
    frontier = set()
    
    if not agent.visited:
        frontier.add((1, 1))
    else:
        for vx, vy in agent.visited:
            for nx, ny in agent.kb.get_adjacent(vx, vy):
                if (nx, ny) not in agent.visited:
                    frontier.add((nx, ny))

    for x in range(1, GRID_SIZE + 1):
        for y in range(1, GRID_SIZE + 1):
            col, row = map_coords(x, y)
            rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)

            if (x, y) in agent.visited:
                pygame.draw.rect(screen, COLOR_VISITED, rect)
            elif (x, y) in frontier and agent.kb.ask_is_safe(x, y) and not agent.has_gold:
                pygame.draw.rect(screen, COLOR_SAFE, rect)
            else:
                pygame.draw.rect(screen, COLOR_UNVISITED, rect)

            pygame.draw.rect(screen, COLOR_LINE, rect, 2)
            center_x, center_y = rect.x + TILE_SIZE // 2, rect.y + TILE_SIZE // 2
            
            if (x, y) in agent.visited:
                percepts = env.get_percept(x, y)
                texts = []
                if percepts["breeze"]: texts.append("Breeze")
                if percepts["stench"]: texts.append("Stench")
                for i, t in enumerate(texts):
                    screen.blit(small_font.render(t, True, (100, 0, 100)), (rect.x + 5, rect.y + 5 + (i * 15)))

            if (x, y) in env.pits:
                pygame.draw.circle(screen, COLOR_PIT, (center_x, center_y), 30)
                screen.blit(font.render("PIT", True, (255, 255, 255)), (center_x - 15, center_y - 12))
            
            if (x, y) == env.wumpus:
                pygame.draw.circle(screen, COLOR_WUMPUS, (center_x, center_y), 30)
                screen.blit(font.render("WUMPUS", True, (255, 255, 255)), (center_x - 40, center_y - 12))
                
            if (x, y) == env.gold and not agent.has_gold:
                pygame.draw.polygon(screen, COLOR_GOLD, [(center_x, center_y - 30), (center_x - 20, center_y + 20), (center_x + 20, center_y + 20)])
                screen.blit(font.render("GOLD", True, (0, 0, 0)), (center_x - 25, center_y - 10))

            if (x, y) == agent.current_pos:
                color = COLOR_GOLD if agent.has_gold else COLOR_AGENT
                pygame.draw.circle(screen, color, (center_x, center_y), 20)
                screen.blit(font.render("A", True, (0, 0, 0) if agent.has_gold else (255, 255, 255)), (center_x - 8, center_y - 12))

    screen.blit(font.render(message, True, (255, 255, 255), (0, 0, 0)), (10, WINDOW_SIZE - 40))
    pygame.display.flip()

def main():
    env = WumpusEnvironment()
    agent = LogicAgent(size=GRID_SIZE)
    msg = "Press SPACE to Step"
    game_over = False
    draw_grid(env, agent, msg)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not game_over:
                x, y = agent.current_pos
                percepts = env.get_percept(x, y)
                
                # Check Win Condition: Escaped with gold
                if agent.has_gold and agent.current_pos == (1, 1):
                    msg = "ESCAPED! Climbed out of the cave with the GOLD!"
                    game_over = True
                    
                # Check Gold Acquistion
                elif percepts["glitter"] and not agent.has_gold:
                    msg = f"Grabbed Gold at ({x}, {y})! Retracing steps to (1,1)..."
                    agent.has_gold = True
                    
                # Standard Movement Phase
                else:
                    if not agent.has_gold:
                        # Exploration
                        agent.perceive_and_tell(percepts)
                        nxt = agent.choose_next_move()
                        status_prefix = "Exploring"
                    else:
                        # Retracing
                        nxt = agent.choose_return_move()
                        status_prefix = "Escaping"
                        
                    if nxt is None:
                        msg = "Stymied. No safe moves left."
                        game_over = True
                    else:
                        msg = f"{status_prefix} -> Moving to {nxt}..."
                        agent.current_pos = nxt
                        
                draw_grid(env, agent, msg)
        clock.tick(FPS)

if __name__ == "__main__":
    main()