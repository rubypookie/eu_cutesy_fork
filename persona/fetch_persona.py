import os
import discord

class Persona:
    def __init__(self):
        pass

    def get_persona(self, persona: str):
        file_path = os.path.join(os.path.dirname(__file__), f"{persona}.txt")
        with open(file_path, "r") as file:
            persona_data = file.read()
        return persona_data.strip()
    
    def add_persona(self, name: str, data: str):
        if os.path.exists(os.path.join(os.path.dirname(__file__), f"{name}.txt")):
            return False
        
        file_path = os.path.join(os.path.dirname(__file__), f"{name}.txt")
        with open(file_path, "w") as file:
            file.write(data)
        return True
    
    def delete_persona(self, name: str):
        if os.path.exists(os.path.join(os.path.dirname(__file__), f"{name}.txt")):
            os.remove(os.path.join(os.path.dirname(__file__), f"{name}.txt"))
            return True
        return False
    
    def get_persona_list(self):
        return [file[:-4] for file in os.listdir(os.path.dirname(__file__)) if file.endswith(".txt")]
    
    def get_persona_contents(self, name: str):
        file_path = os.path.join(os.path.dirname(__file__), f"{name}.txt")
        with open(file_path, "r") as file:
            persona_data = file.read()
        return persona_data.strip()