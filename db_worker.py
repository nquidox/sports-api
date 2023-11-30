import os
import sqlite3

DB_NAME = 'sports_api.db'
DB_PATH = os.path.dirname(os.path.abspath(__file__))


def db_worker(op: str, sql: str, values: tuple = None):
    db = sqlite3.connect(database="sports_api.db")
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    match op:
        case 'ins' | 'del' | 'upd':
            cursor.execute(sql, values)
            db.commit()
            cursor.close()

        case 'fo':
            if values is not None:
                cursor.execute(sql, values)

            elif values is None:
                cursor.execute(sql)

            result = dict(cursor.fetchone())
            cursor.close()
            return result

        case 'fa':
            if values is not None:
                cursor.execute(sql, values)

            elif values is None:
                cursor.execute(sql)

            result = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            return result

        case 'init':
            cursor.execute(sql)
            cursor.close()

    db.close()


def init_db():
    if not os.path.exists(os.path.join(DB_PATH, DB_NAME)):
        db_worker('init', '''CREATE TABLE IF NOT EXISTS users(
            "id" INTEGER,
            "username" TEXT UNIQUE,
            "first_name" TEXT,
            "last_name" TEXT,
            "birthday" REAL,
            "gender" TEXT,
            "disabled" INTEGER,
            "hashed_password" TEXT,
            "is_superuser" INTEGER,
            "cookie_secret"	TEXT,
            PRIMARY KEY ("id" AUTOINCREMENT)
            )''')

        db_worker('init', '''CREATE TABLE IF NOT EXISTS activities(
            "id" INTEGER,
            "user_id" INTEGER,
            "title" TEXT,
            "description" TEXT,
            "activity_type" TEXT,
            "laps" INTEGER,
            "distance" INTEGER,
            "date" REAL,
            "time_start" REAL,
            "time_end" REAL,
            "published" INTEGER,
            "visibility" INTEGER,
            PRIMARY KEY ("id" AUTOINCREMENT)
        )''')

        db_worker('init', '''CREATE TABLE IF NOT EXISTS sessions(
            "id" INTEGER,
            "user_id" INTEGER,
            "token"	TEXT,
            "client_info" TEXT,
            "expires" INTEGER,
            PRIMARY KEY("id" AUTOINCREMENT)
        )''')
