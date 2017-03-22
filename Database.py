import sqlite3
from nltk.stem.porter import PorterStemmer
from nltk import FreqDist
import nltk
# import typing
# import cython
import data_utl
import StopWords
import functools
import math


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

    def change3(self):
        self.c.execute('SELECT DISTINCT * FROM tokens GROUP BY book_id')
        all_result = self.c.fetchall()
        for item in all_result:
            self.c.execute('SELECT * FROM tokens WHERE token_value=?', (item[0]))

    @staticmethod
    def handle_tokens(query_text: str):
        tokens = nltk.word_tokenize(query_text)
        tokens = filter(lambda x: x not in StopWords.stop_words, tokens)
        tokens = map(PorterStemmer().stem, tokens)
        return tokens

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

    def query2(self, query_text: str):
        tokens = list(self.handle_tokens(query_text))
        self.c.execute('SELECT * FROM books')
        all_books = self.c.fetchall()
        all_books = list(filter(lambda x: x[-1] > 0, all_books))
        all_token_occur = []
        for token in tokens:
            self.c.execute('SELECT count(*) FROM tokens WHERE token_value=?', (token,))
            all_token_occur.append(self.c.fetchone()[0])
        for index, book in enumerate(all_books):
            freq = 0.0
            for index2, token in enumerate(tokens):
                self.c.execute('SELECT count(*) FROM tokens WHERE book_id=? AND token_value=?', (book[0], token))
                token_book_occurrence = self.c.fetchone()[0]
                if token_book_occurrence > 0:
                    token_all_occurrence = all_token_occur[index2]
                    freq += (token_book_occurrence / book[-1]) / token_all_occurrence
            all_books[index] = (book + (freq,))
            # book += (freq,)
        all_books.sort(key=lambda tup: tup[-1], reverse=True)
        list(map(print, all_books[:10]))
        # print(all_books[:10])

    def query3(self, query_text: str):
        tokens = list(self.handle_tokens(query_text))
        self.c.execute('SELECT * FROM books')
        all_books = self.c.fetchall()
        all_books = list(filter(lambda x: x[-1] > 0, all_books))
        all_token_occur = []
        for token in tokens:
            self.c.execute('SELECT count(*) FROM tokens WHERE token_value=?', (token,))
            all_token_occur.append(self.c.fetchone()[0])
        for index, book in enumerate(all_books):
            freq = 0.0
            self.c.execute('SELECT token_value FROM tokens WHERE book_id=?', (book[0],))
            tokens_in_the_book = self.c.fetchall()
            tokens_in_the_book = list(map(lambda x: x[0], tokens_in_the_book))
            for index2, token in enumerate(tokens):
                token_book_occurrence = tokens_in_the_book.count(token)
                if token_book_occurrence > 0:
                    token_all_occurrence = all_token_occur[index2]
                    freq += math.log(1 + token_book_occurrence / book[-1]) / token_all_occurrence
            all_books[index] = (book + (freq,))
            # book += (freq,)
        all_books.sort(key=lambda tup: tup[-1], reverse=True)
        list(map(print, all_books[:10]))
        # print(all_books[:10])

    def query4(self, query_text: str):
        tokens = list(self.handle_tokens(query_text))
        self.c.execute('SELECT * FROM books')
        all_books = self.c.fetchall()
        all_books = list(filter(lambda x: x[-1] > 0, all_books))

        self.c.execute('SELECT * FROM tokens')
        all_tokens = self.c.fetchall()
        bare_tokens = list(map(lambda x: x[0], all_tokens))
        all_token_occur = list(map(lambda x: bare_tokens.count(x), tokens))

        for index, book in enumerate(all_books):
            freq = 0.0
            tokens_in_the_book = list(map(lambda x: x[0], filter(lambda x: x[2] == book[0], all_tokens)))
            for index2, token in enumerate(tokens):
                token_book_occurrence = tokens_in_the_book.count(token)
                if token_book_occurrence > 0:
                    token_all_occurrence = all_token_occur[index2]
                    freq += (token_book_occurrence / book[-1]) / token_all_occurrence
            all_books[index] = (book + (freq,))
        # book += (freq,)
        all_books.sort(key=lambda tup: tup[-1], reverse=True)
        list(map(print, all_books[:10]))

    def query5(self, query_text: str):
        tokens = list(self.handle_tokens(query_text))
        self.c.execute('SELECT * FROM books')
        all_books = self.c.fetchall()
        all_books = list(filter(lambda x: x[-1] > 0, all_books))
        all_token_occur = []
        for token in tokens:
            self.c.execute('SELECT book_id FROM tokens WHERE token_value=?',
                           (token,))
            all_token_occur.append(data_utl.handle_from_database(self.c.fetchall()))
        data_utl.handle_books(all_books, all_token_occur)
        all_books.sort(key=lambda tup: tup[-1], reverse=True)
        list(map(print, all_books[:10]))
        # print(all_books[:10])
