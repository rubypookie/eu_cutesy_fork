# database code for storing user data
"""
Current arguments:
    - user_id: int
    - agent_id: str

Current methods:
    - get_user_data
    - set_user_data
    - update_user_data
    - delete_user_data
"""

import sqlite3

class AgentDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('database/database.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_user_data (
                user_id INTEGER PRIMARY KEY,
                agent_id TEXT
            )
        ''')
        self.conn.commit()

    def get_user_data(self, user_id):
        self.cursor.execute('SELECT * FROM agent_user_data WHERE user_id=?', (user_id,))
        return self.cursor.fetchone()

    def set_user_data(self, user_id, agent_id):
        self.cursor.execute('INSERT INTO agent_user_data (user_id, agent_id) VALUES (?, ?)', (user_id, agent_id))
        self.conn.commit()

    def update_user_data(self, user_id, agent_id):
        self.cursor.execute('UPDATE agent_user_data SET agent_id=? WHERE user_id=?', (agent_id, user_id))
        self.conn.commit()

    def delete_user_data(self, user_id):
        self.cursor.execute('DELETE FROM agent_user_data WHERE user_id=?', (user_id,))
        self.conn.commit()