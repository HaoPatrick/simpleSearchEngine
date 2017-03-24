cimport cython

def handle_books(list all_books, list all_token_occur):
    for index, book in enumerate(all_books):
        freq = 0.0
        _book_id = book[0]
        for token_index, token in enumerate(all_token_occur):
            if not len(token):
                continue
            # tokens_in_the_book = len(list(filter(lambda x: x == book[0], token)))
            tokens_in_the_book = sum(x == _book_id for x in token)
            freq += tokens_in_the_book / book[-1] / len(token)
        all_books[index] = (book + (freq,))
    return all_books.sort(key=lambda x: x[-1], reverse=True)

def handle_from_database(list in_list):
    return list(map(lambda x: int(x[0]), in_list))
