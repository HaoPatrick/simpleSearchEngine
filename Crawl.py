from bs4 import BeautifulSoup
from StopWords import stop_words
import nltk
import requests
from nltk.stem.porter import PorterStemmer
import Database
from urllib.parse import urljoin


class OnePage:
    def __init__(self, url='', base_url='http://shakespeare.mit.edu/'):
        self._url = url
        self._raw_html = None
        self.soup = None
        self.base_url = base_url
        if url:
            self.get_raw_html()

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        self._url = value

    def get_raw_html(self):
        if not self._url:
            return
        response = requests.get(self._url)
        self._raw_html = response.content.decode('utf-8')
        self.soup = BeautifulSoup(self._raw_html, 'html.parser')

    @property
    def all_links(self):
        if hasattr(self, '_links'):
            return self._links
        self._get_links()
        return self._links

    def _get_links(self):
        self._links = []
        try:
            self._links.extend(
                map(lambda x: urljoin(self.url, x.get('href')),
                    filter(lambda url: 'http' not in url.get('href'), self.soup.find_all('a'))))
        except TypeError:
            self._links = []

    @property
    def tokens(self):
        if hasattr(self, '_tokens'):
            return self._tokens
        self._get_tokens()
        return self._tokens

    @property
    def title(self):
        if hasattr(self, '_title'):
            return self._title
        self._get_title()
        return self._title

    def _get_title(self):
        self._title = self.soup.title.string[:-1]

    def _get_tokens(self):
        if not hasattr(self, '_plain_text'):
            self._get_plain_text()
        self._tokens = nltk.word_tokenize(self._plain_text)
        self._tokens = list(map(PorterStemmer().stem, self._tokens))
        self._tokens = zip(self._tokens, range(len(self._tokens)))
        self._tokens = list(filter(lambda x: x[0].lower() not in stop_words, self._tokens))
        self._tokens = list(filter(lambda x: len(x[0]) > 1, self._tokens))
        # self._tokens = list(map(lambda value: {value[0]: value[1]}, self._tokens))

    @property
    def database_items(self):
        if hasattr(self, '_database_items'):
            return self._database_items
        self._get_database_item()
        return self._database_items

    def _get_database_item(self):
        self._database_items = list(map(lambda x: x + (self.title,) + (self.url,), self.tokens))

    @property
    def plain_text(self):
        if hasattr(self, '_plain_text'):
            return self._plain_text
        self._get_plain_text()
        return self._plain_text

    def _get_plain_text(self):
        self._plain_text = self.soup.get_text()

    def commit(self):
        Database.DatabaseItem().add_item(self.database_items)
        print('Done')


# nltk.download()
global_link_pool = ['http://shakespeare.mit.edu/Poetry/sonnet.I.html']
while global_link_pool:
    try:
        one_page = OnePage(global_link_pool[0])
        one_page.commit()
        global_link_pool.extend(filter(lambda x: x not in global_link_pool, one_page.all_links))
    except Exception as e:
        print(e)
    finally:
        global_link_pool = global_link_pool[1:]
# test_page = OnePage(BASE_URL)
# global_link_pool.extend(test_page.all_links)
# print(test_page.database_items)
# test_page.commit()
