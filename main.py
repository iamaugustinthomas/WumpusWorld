from world import WumpusEnvironment
from agent import LogicAgent


def run_simulation():
    # Setup environment
    # Grid: 4x4
    # Wumpus at (1, 3), Pits at (3, 1), (3, 3), (4, 4), Gold at (2, 3)
    env = WumpusEnvironment()
    agent = LogicAgent(size=4)

    print("=== STARTING WUMPUS WORLD LOGICAL AGENT ===")
    
    max_steps = 15
    for step in range(max_steps):
        x, y = agent.current_pos
        percepts = env.get_percept(x, y)

        if percepts["glitter"]:
            print(f"\n WIN! Gold found at ({x}, {y}) in {step} steps!")
            agent.has_gold = True
            break

        # Pass percepts into logic engine
        agent.perceive_and_tell(percepts)

        # Decide next step using inference
        next_pos = agent.choose_next_move()

        if next_pos is None:
            print("\n[Agent] Stymied. No remaining provably safe tiles to explore.")
            break

        agent.current_pos = next_pos


if __name__ == "__main__":
    run_simulation()