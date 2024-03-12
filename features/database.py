# database code for storing user data
"""
UserDatabase class:
Current arguments:
    - user_id: int
    - agent_id: str
    - persona: str

Current methods:
    - get_user_data
    - set_user_data
    - update_user_data
    - delete_user_data
"""

"""
AgentDatabase class:
Current arguments:
    - persona: str
    - avatar_url: str

Current methods:
    - get_agent_data
    - set_agent_data
    - update_agent_data
    - delete_agent_data
"""

import sqlite3
import os

class UserDatabase:
    def __init__(self):
        if not os.path.exists('database'):
            os.makedirs('database')

        self.conn = sqlite3.connect('database/database.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_user_data (
                user_id INTEGER PRIMARY KEY,
                agent_id TEXT,
                persona TEXT
            )
        ''')
        self.conn.commit()
        
    def get_user_data(self, user_id: int):
        self.cursor.execute('SELECT * FROM agent_user_data WHERE user_id = ?', (user_id,))
        return self.cursor.fetchone()
    
    def set_user_data(self, user_id: int, agent_id: str, persona: str):
        self.cursor.execute('INSERT INTO agent_user_data (user_id, agent_id, persona) VALUES (?, ?, ?)', (user_id, agent_id, persona))
        self.conn.commit()

    def update_user_data(self, user_id: int, agent_id: str, persona: str):
        self.cursor.execute('UPDATE agent_user_data SET agent_id = ?, persona = ? WHERE user_id = ?', (agent_id, persona, user_id))
        self.conn.commit()

    def delete_user_data(self, user_id: int):
        self.cursor.execute('DELETE FROM agent_user_data WHERE user_id = ?', (user_id,))
        self.conn.commit()

class AgentDatabase:
    def __init__(self):
        if not os.path.exists('database'):
            os.makedirs('database')

        self.conn = sqlite3.connect('database/database.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_data (
                persona TEXT PRIMARY KEY,
                avatar_url TEXT
            )
        ''')
        self.conn.commit()
        
    def get_agent_data(self, persona: str):
        self.cursor.execute('SELECT * FROM agent_data WHERE persona = ?', (persona,))
        return self.cursor.fetchone()
    
    def set_agent_data(self, persona: str, avatar_url: str):
        self.cursor.execute('INSERT INTO agent_data (persona, avatar_url) VALUES (?, ?)', (persona, avatar_url))
        self.conn.commit()

    def update_agent_data(self, persona: str, avatar_url: str):
        self.cursor.execute('UPDATE agent_data SET avatar_url = ? WHERE persona = ?', (avatar_url, persona))
        self.conn.commit()

    def delete_agent_data(self, persona: str):
        self.cursor.execute('DELETE FROM agent_data WHERE persona = ?', (persona,))
        self.conn.commit()