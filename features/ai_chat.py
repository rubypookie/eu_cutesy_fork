# AI chat inference code

import memgpt
from memgpt.client.client import Client as MemGPT

class Infer:
    def __init__(self):
        self.instance = MemGPT()

    def chat(self, agent, message):
        pass

    def create(self):
        agent = self.instance.create_agent(agent_config={})
        return agent