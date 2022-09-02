import sqlite3

#conn = sqlite3.connect('shows.db')

#name = 'overlord'

#c = conn.cursor()
#link = 'https://beta.crunchyroll.com/watch/GY8VMKPGY/the-terrifying-duo-meowban-brothers-vs-zoro'

#query = '''SELECT DISTINCT link FROM ''' + name + ''''''

#episodes = c.execute(query)

#showSet = set()

#query = '''SELECT EXISTS(SELECT 1 FROM ''' + name + ''' WHERE link = "''' + link + '''") '''

#result = c.execute(query).fetchone()
#print(result)
#if result[0] == 0:
#    print('not in database')
#else:
#    c = conn.cursor()
#    query = '''SELECT * FROM ''' + name + \
#        ''' WHERE link = "''' + link + '''"'''
#    print(c.execute(query).fetchall())

#for episode in episodes:
#    c = conn.cursor()
#    print(episode)
#    q2 = '''SELECT * FROM ''' + name + ''' WHERE link = "''' + episode[0] + '''"'''
#    print(c.execute(q2).fetchall())
#    input()
#season_title = 'Overlord IV'
#season_number = '4'
#episode_number = '9'
#episode_title = 'essssssesefaef'
#link = "https://beta.crunchyroll.com/watch/GWDU8WM44/countdown-to-extinction"
#language = "Japanese"


#query = '''UPDATE ''' + name + ''' SET season_title = ?, season_number = ?, episode_number =?, episode_title = ? , language = ? WHERE link = "''' + link + '''"'''
#c.execute(query,(season_title,season_number,episode_number,episode_title,language))

#query = '''SELECT EXISTS(SELECT 1 FROM "''' + name + '''" WHERE link = "''' + link + '''")'''
#print(c.execute(query).fetchone())

languages = set()

with sqlite3.connect('shows.db') as conn:
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    count = 0
    for tablerow in cursor.fetchall():
        count = count + 1
        table = tablerow[0]
        cursor.execute("SELECT * FROM {t}".format(t=table))
        for row in cursor:
            languages.add(row['language'])
            #if row['language'] == 'Arabic':
            #    print(tablerow[0])
            #if row['language'] == '2nd':
            #    print(tablerow[0])
            #if row['language'] == 'Uncensored':
            #    print(tablerow[0])
            #if row['language'] == 'Season':
            #    print(tablerow[0])
    print(count)
print(languages)
#commit the changes to db
conn.commit()
#close the connection
conn.close()
