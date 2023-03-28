import sqlite3

conn = sqlite3.connect('UniversityDatabase.db')

cursor = conn.cursor()

table = """CREATE TABLE certificates
        (Student_ID VARCHAR(25) PRIMARY KEY NOT NULL,
        Sign_digest VARCHAR(255) NOT NULL,
        Signed_file_name VARCHAR(255) NOT NULL);"""

cursor.execute(table)

conn.close()