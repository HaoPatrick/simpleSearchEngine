import sqlite3
from nltk.stem.porter import PorterStemmer
from nltk import FreqDist
import nltk
import StopWords


class DatabaseItem:
    def __init__(self):
        self.conn = sqlite3.connect('token.db')
        self.c = self.conn.cursor()

    def add_item(self, token: list):
        self.c.execute(r"SELECT * FROM tokens WHERE url=?", (token[0][-1],))
        exist = self.c.fetchone()
        if not exist:
            print('hit')
            self.c.executemany('INSERT INTO tokens VALUES (?,?,?,?)', token)
        self.conn.commit()

    def change(self):
        self.c.execute('SELECT * FROM tokens')
        all_result = self.c.fetchall()
        for item in all_result:
            self.c.execute('SELECT * FROM books WHERE url=?', (item[3],))
            exist = self.c.fetchone()
            if not exist:
                self.c.execute('INSERT INTO books(title,url) VALUES (?,?)', (item[2], item[3]))
                self.c.execute('SELECT * FROM books WHERE url=?', (item[3],))
                exist = self.c.fetchone()
                self.c.execute('UPDATE tokens SET book_id=? WHERE title=?', (exist[0], item[2]))
                print((exist[0], item[2]))
                self.conn.commit()

    def change2(self):
        self.c.execute('SELECT * FROM books')
        all_result = self.c.fetchall()
        for item in all_result:
            self.c.execute('SELECT count(*) FROM tokens WHERE book_id=?', (item[0],))
            book_count = self.c.fetchone()
            self.c.execute('UPDATE books SET count=? WHERE id=?', (book_count[0], item[0]))
            self.conn.commit()

    def query(self, query_text: str):
        tokens = nltk.word_tokenize(query_text)
        tokens = filter(lambda x: x not in StopWords.stop_words, tokens)
        tokens = map(PorterStemmer().stem, tokens)
        result_list = []
        for token in tokens:
            self.c.execute('SELECT DISTINCT book_id FROM tokens WHERE token_value=?', (token,))
            tem_set = self.c.fetchall()
            result_list.extend(tem_set)
        freq_dist = FreqDist(result_list)
        result_list = freq_dist.most_common(10)
        result_list = map(lambda x: x[0], result_list)
        for book in result_list:
            self.c.execute('SELECT title,url FROM books WHERE id=?', (int(book[0]),))
            print(self.c.fetchone())
            # print(result_list)
