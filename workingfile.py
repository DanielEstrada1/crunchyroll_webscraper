import sqlite3

conn = sqlite3.connect('mysqlite.db')
c = conn.cursor()

name = 'test_Table'

query = '''CREATE TABLE IF NOT EXISTS ''' + name + ''' (rollno real, name text, class real)'''

print(query)

#get the count of tables with the name
c.execute(query)

#commit the changes to db
conn.commit()
#close the connection
conn.close()
