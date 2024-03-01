# AI chat inference code

import memgpt
from memgpt.client.client import Client as MemGPT

class Infer:
    def __init__(self):
        self.instance = MemGPT(auto_save=True)

    def chat(self, agent, message):
        response = self.instance.user_message(agent.id, message)
        return response

    def create(self):
        agent = self.instance.create_agent(agent_config={})
        return agent