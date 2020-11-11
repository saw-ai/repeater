import sqlite3
from pandas import DataFrame
import pandas as pd
import psycopg2

class Storage:
    def __init__(self):
        self.conn = psycopg2.connect(dbname='repeater', user='saw_ai', password='12345', host='localhost')
        self.cursor = self.conn.cursor()

        #cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='WORDS';")
        #if not cursor.fetchall():
        #    cursor.execute('CREATE TABLE WORDS (word text, frequency number)')
        #    conn.commit()
        #    df = pd.read_csv('unigram_freq.csv').set_index('word')
        #    df.to_sql('WORDS', conn, if_exists='replace')

        self.cursor.execute("SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'words';")
        self.users = set(list(map(lambda x : x[0][1:], self.cursor.fetchall()))[3:])

        self.cursor.execute('SELECT word from words')
        self.words = set(map(lambda x : x[0].strip(), self.cursor.fetchall()))


    def add_user(self, user_id):
        if str(user_id) not in self.users:
            self.cursor.execute(f"ALTER TABLE WORDS ADD COLUMN _{user_id} NUMBER default 0;")
            self.conn.commit()
            self.users.add(user_id)

    def get_words(self, user_id, count, top=500, label=0):
        self.add_user(user_id)
        self.cursor.execute(f"SELECT * from (SELECT word FROM WORDS WHERE _{user_id}={label} ORDER BY index LIMIT {top}) AS x ORDER BY RANDOM() LIMIT {count};")
        return list(map(lambda x : x[0].strip(), self.cursor.fetchall()))


    def change_status(self, user_id, words, label):
        self.add_user(user_id)
        self.add_words(user_id, set(words) - self.words)
        words_list = "'" + "', '".join(words) + "'"
        query = f"""
            UPDATE words 
            SET _{user_id} = {label}
            WHERE word in ({words_list});"""
        self.cursor.execute(query)
        self.conn.commit()

    def get_values(self, user_id):
        self.add_user(user_id)
        self.cursor.execute(f"SELECT _{user_id} FROM words;")
        return list(map(lambda x : x[0], self.cursor.fetchall()))

    def get_count(self, user_id, label=None):
        self.add_user(user_id)
        if label is None:
            self.cursor.execute(f"SELECT count(*) FROM words;")
        else:
            self.cursor.execute(f"SELECT count(*) FROM words WHERE _{user_id}={label};")
        return self.cursor.fetchall()[0][0]

    def add_words(self, user_id, words):
        if words:
            for word in words:
                self.cursor.execute(f"INSERT INTO words (word) VALUES ('{word}')")
                self.words.add(word)
            self.conn.commit()

