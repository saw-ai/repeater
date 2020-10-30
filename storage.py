import sqlite3
from pandas import DataFrame
import pandas as pd

class Storage:
    def __init__(self, DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='WORDS';")
        if not cursor.fetchall():
            cursor.execute('CREATE TABLE WORDS (word text, frequency number)')
            conn.commit()
            df = pd.read_csv('unigram_freq.csv').set_index('word')
            df.to_sql('WORDS', conn, if_exists='replace')


        cursor.execute("PRAGMA table_info(WORDS);")
        self.users = set(list(map(lambda x : x[1], cursor.fetchall()))[2:])
        self.conn = conn

    def add_user(self, user_id):
        if str(user_id) not in self.users:
            cursor = self.conn.cursor()
            cursor.execute(f"ALTER TABLE WORDS ADD COLUMN `{user_id}` NUMBER default 0;")
            self.conn.commit()
            self.users.add(user_id)

    def get_words(self, user_id, count, top=500, label=0):
        self.add_user(user_id)
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * from (SELECT word FROM WORDS WHERE `{user_id}`={label} LIMIT {top}) ORDER BY RANDOM() LIMIT {count};")
        return list(map(lambda x : x[0], cursor.fetchall()))


    def change_status(self, user_id, words, label):
        self.add_user(user_id)
        cursor = self.conn.cursor()
        words_list = "'" + "', '".join(words) + "'"
        query = f"""
            UPDATE words 
            SET `{user_id}` = {label}
            WHERE word in ({words_list});"""
        cursor.execute(query)
        self.conn.commit()

    def get_values(self, user_id):
        self.add_user(user_id)
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT `{user_id}` FROM words;")
        return list(map(lambda x : x[0], cursor.fetchall()))

    def get_count(self, user_id, label=None):
        self.add_user(user_id)
        cursor = self.conn.cursor()
        if label is None:
            cursor.execute(f"SELECT count(*) FROM words;")
        else:
            cursor.execute(f"SELECT count(*) FROM words WHERE `{user_id}`={label};")
        return cursor.fetchall()[0][0]


#storage.change_status(user, ['of', 'and'], 1)
#print (storage.get_words(user, 5))
#storage = Storage()
#print(storage.users)
print (Storage('storage.db').get_words('id12345', 30, top=30, label=1))