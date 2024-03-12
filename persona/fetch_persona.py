import os
import discord
from features.database import AgentDatabase

class Persona:
    def __init__(self):
        self.agent_db = AgentDatabase()

    def get_persona(self, persona: str):
        file_path = os.path.join(os.path.dirname(__file__), f"contents/{persona}.txt")
        with open(file_path, "r") as file:
            persona_data = file.read()
        return persona_data.strip()
    
    def add_persona(self, name: str, data: str):
        if os.path.exists(os.path.join(os.path.dirname(__file__), f"contents/{name}.txt")):
            return False
        
        file_path = os.path.join(os.path.dirname(__file__), f"contents/{name}.txt")
        with open(file_path, "w") as file:
            file.write(data)
        return True
    
    def delete_persona(self, name: str):
        if os.path.exists(os.path.join(os.path.dirname(__file__), f"contents/{name}.txt")):
            os.remove(os.path.join(os.path.dirname(__file__), f"contents/{name}.txt"))
            return True
        return False
    
    def get_persona_list(self):
        return [file[:-4] for file in os.listdir(os.path.dirname(__file__) + "/contents/") if file.endswith(".txt") and self.agent_db.get_agent_data(file[:-4])]
    
    def get_redundant_persona_list(self):
        return [file[:-4] for file in os.listdir(os.path.dirname(__file__) + "/contents/") if file.endswith(".txt") and self.agent_db.get_agent_data(file[:-4]) is None]

    # Redundant method????
    # def get_persona_contents(self, name: str):
    #     file_path = os.path.join(os.path.dirname(__file__), f"contents/{name}.txt")
    #     with open(file_path, "r") as file:
    #         persona_data = file.read()
    #     return persona_data.strip()