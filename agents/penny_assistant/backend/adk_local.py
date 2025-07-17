"""
Run Penny locally with ADK, memorybank, and evaluation support.
"""
from adk.agent import Agent
from adk.memorybank import MemoryBank
from adk.evaluation import Evaluator

# TODO: Define your agent logic, tools, and prompts
# TODO: Configure MemoryBank (local or cloud)
# TODO: Set up Evaluator for local evaluation

def main():
    # Example stubs
    memorybank = MemoryBank()
    agent = Agent(memorybank=memorybank)
    evaluator = Evaluator()
    # TODO: Add your agent loop, evaluation, and CLI or API interface
    print("Penny ADK local runner initialized.")
    # Example: agent.run()

if __name__ == "__main__":
    main() 