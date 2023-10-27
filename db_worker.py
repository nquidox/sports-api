import os
import sqlite3

DB_NAME = 'sports_api.db'
DB_PATH = os.path.dirname(os.path.abspath(__file__))


def db_worker(op: str, sql: str, values: tuple = None):
    db = sqlite3.connect(database="sports_api.db")
    cursor = db.cursor()

    match op:
        case 'ins' | 'del' | 'upd':
            cursor.execute(sql, values)
            db.commit()
            cursor.close()

        case 'fo':
            cursor.execute(sql, values)
            row = cursor.fetchone()
            cursor.close()
            return row

        case 'fa':
            cursor.execute(sql, values)
            rows = cursor.fetchall()
            cursor.close()
            return rows

        case 'init':
            cursor.execute(sql)
            cursor.close()

    db.close()


def init_db():
    if not os.path.exists(os.path.join(DB_PATH, DB_NAME)):
        db_worker('init', '''CREATE TABLE IF NOT EXISTS users(
            "id" INTEGER,
            "username" TEXT,
            "first_name" TEXT,
            "last_name" TEXT,
            "birthday" REAL,
            "gender" TEXT,
            PRIMARY KEY ("id" AUTOINCREMENT)
            )''')
