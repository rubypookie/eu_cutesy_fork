# AI chat inference code

from memgpt import create_client

        # self.instance = MemGPT(auto_save=True)

class Infer:
    def __init__(self):
        self.client = create_client()

    def get_chat_response(self, agent, message):
        """
        Initiates a thread to get a chat response.
        """
        response = self.client.user_message(agent, message)
        return response

    def create_agent(self, persona: str = "sam_pov"):
        """
        Initiates a thread to create an agent.
        """
        agent = self.client.create_agent(persona=persona)
        return agent.id