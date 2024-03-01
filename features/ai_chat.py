# AI chat inference code

import memgpt
import threading
from memgpt.client.client import Client as MemGPT

class Infer:
    def __init__(self):
        self.instance = MemGPT(auto_save=True)
        self.agent = None
        self.response = None
        self.lock = threading.Lock()

    def chat_callback(self, agent, message):
        """
        Target function for the thread handling chat responses.
        """
        response = self.instance.user_message(agent.id, message)
        with self.lock:
            self.response = response

    def get_chat_response(self, agent, message):
        """
        Initiates a thread to get a chat response.
        """
        chat_thread = threading.Thread(target=self.chat_callback, args=(agent, message))
        chat_thread.start()
        chat_thread.join()  # Wait for the thread to complete
        return self.response

    def create_agent_callback(self):
        """
        Target function for the thread handling agent creation.
        """
        agent = self.instance.create_agent(agent_config={})
        with self.lock:
            self.agent = agent

    def create_agent(self):
        """
        Initiates a thread to create an agent.
        """
        create_thread = threading.Thread(target=self.create_agent_callback)
        create_thread.start()
        create_thread.join()  # Wait for the thread to complete
        return self.agent