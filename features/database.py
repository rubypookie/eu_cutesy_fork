# database code for storing user data
"""
Current arguments:
    - user_id: int

Current methods:
    - get_user_data
    - set_user_data
    - update_user_data
    - delete_user_data
"""

import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('database/database.db')
        self.cursor = self.conn.cursor()

    def get_user_data(self, user_id: int):
        self.cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        return self.cursor.fetchone()
    
    def set_user_data(self, user_id: int, data: str):
        self.cursor.execute('INSERT INTO users (user_id, data) VALUES (?, ?)', (user_id, data))
        self.conn.commit()

    def update_user_data(self, user_id: int, data: str):    
        self.cursor.execute('UPDATE users SET data = ? WHERE user_id = ?', (data, user_id))
        self.conn.commit()

    def delete_user_data(self, user_id: int):
        self.cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
        self.conn.commit()