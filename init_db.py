import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO contacts (firstname, lastname, emails) VALUES (?, ?, ?)",
            ('Natnael', 'Desta', '["abcd@gmail.com", "efgh@gmail.com"]')
            )

connection.commit()
connection.close()