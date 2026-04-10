import sqlite3
import os

class DatabaseManager:
    """
    数据库管理类，负责 SQLite 数据库的初始化和 CRUD 操作。
    """
    
    DB_NAME = "passwords.db"

    def __init__(self):
        self.conn = sqlite3.connect(self.DB_NAME)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        
        # 存储主密码盐值
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value BLOB
            )
        ''')
        
        # 存储分类
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        
        # 存储加密后的密码项
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site TEXT NOT NULL,
                username TEXT NOT NULL,
                password_encrypted TEXT NOT NULL,
                notes_encrypted TEXT,
                category_id INTEGER,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')
        
        # 初始化默认分类
        default_categories = ["社交", "工作", "银行"]
        for cat in default_categories:
            cursor.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (cat,))
            
        self.conn.commit()

    def get_salt(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT value FROM config WHERE key = "salt"')
        row = cursor.fetchone()
        return row[0] if row else None

    def set_salt(self, salt: bytes):
        cursor = self.conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO config (key, value) VALUES ("salt", ?)', (salt,))
        self.conn.commit()

    def add_entry(self, site, username, password_enc, notes_enc, category_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO entries (site, username, password_encrypted, notes_encrypted, category_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (site, username, password_enc, notes_enc, category_id))
        self.conn.commit()
        return cursor.lastrowid

    def update_entry(self, entry_id, site, username, password_enc, notes_enc, category_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE entries 
            SET site=?, username=?, password_encrypted=?, notes_encrypted=?, category_id=?
            WHERE id=?
        ''', (site, username, password_enc, notes_enc, category_id, entry_id))
        self.conn.commit()

    def delete_entry(self, entry_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM entries WHERE id=?', (entry_id,))
        self.conn.commit()

    def get_entries(self, search_term=None):
        cursor = self.conn.cursor()
        if search_term:
            query = '''
                SELECT e.*, c.name as category_name 
                FROM entries e 
                LEFT JOIN categories c ON e.category_id = c.id
                WHERE e.site LIKE ? OR e.username LIKE ?
            '''
            cursor.execute(query, (f'%{search_term}%', f'%{search_term}%'))
        else:
            query = '''
                SELECT e.*, c.name as category_name 
                FROM entries e 
                LEFT JOIN categories c ON e.category_id = c.id
            '''
            cursor.execute(query)
        return cursor.fetchall()

    def get_categories(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM categories')
        return cursor.fetchall()

    def add_category(self, name):
        cursor = self.conn.cursor()
        try:
            cursor.execute('INSERT INTO categories (name) VALUES (?)', (name,))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def close(self):
        self.conn.close()
