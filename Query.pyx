import pyximport
pyximport.install()
import Database

database = Database.DatabaseItem()
# database.change2()
query_text = "Contending 'gainst obedience, as they would make"
database.query(query_text)
print('=========')
database.query5(query_text)


def aaa():
    # database2 = Database.DatabaseItem()
    database.query5(query_text)
