import asyncio
from src.orchestrator import Orchestrator

if __name__ == "__main__":
    # Example Input
    prompt = "Create a dark, futuristic presentation about AI Agents replacing traditional software. 3 slides."
    
    orchestrator = Orchestrator()
    asyncio.run(orchestrator.run_workflow(prompt))