# import pyximport
# pyximport.install(pyimport=True)
import Database
import time

database = Database.DatabaseItem()
# database.change2()
query_text = "Contending 'gainst obedience, as they would make"
database.query(query_text)
print('==========')
start_time = time.time()
database.query5(query_text)
end_time = time.time()

print(end_time-start_time)


def aaa():
    # database2 = Database.DatabaseItem()
    database.query5(query_text)
