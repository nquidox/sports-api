import sqlite3


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

    db.close()
