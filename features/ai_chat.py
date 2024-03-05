# AI chat inference code

from memgpt import create_client
import uuid

class Infer:
    def __init__(self):
        self.client = create_client()
        # self.client.auto_save = True

    def get_chat_response(self, agent, message):
        """
        Initiates a thread to get a chat response.
        """
        response = self.client.user_message(uuid.UUID(agent), message)
        print(response)
        return response

    def create_agent(self, persona: str = "sam_pov"):
        """
        Initiates a thread to create an agent.
        """
        agent = self.client.create_agent(persona=persona, human="cs_phd")
        print(agent.id)
        return agent.id
    
    def save_agent(self):
        """
        Initiates a thread to save an agent.
        """
        self.client.save()
        return
    
    # def delete_agent(self, agent):
    #     """
    #     Initiates a thread to delete an agent.
    #     """
    #     self.client.delete_agent(agent)
    #     return