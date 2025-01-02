import sqlite3

conn = sqlite3.connect("aria.db")
cursor = conn.cursor()

query = "CREATE TABLE IF NOT EXISTS sys_command(id integer primary key, name VARCHAR(100), path VARCHAR(1000))"
cursor.execute(query)

# query = "INSERT INTO sys_command VALUES (null, 'discord', 'C:\\Users\\mihai\\AppData\\Local\\Discord\\Update.exe --processStart Discord.exe')"
# cursor.execute(query)
# conn.commit()

query = "CREATE TABLE IF NOT EXISTS web_command(id integer primary key, name VARCHAR(100), path VARCHAR(1000))"
cursor.execute(query)

# query = "INSERT INTO web_command VALUES (null, 'youtube', 'https://www.youtube.com/')"
# cursor.execute(query)
# conn.commit()

query = "CREATE TABLE IF NOT EXISTS contacts (id integer primary key, name VARCHAR(200), mobile_nr VARCHAR(255), email VARCHAR(255) NULL)"
cursor.execute(query)

# query = "INSERT INTO contacts VALUES (null, 'name', '00000000', 'null)"
# cursor.execute(query)
# conn.commit()

conn.commit()
conn.close()