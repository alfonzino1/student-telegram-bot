import sqlite3

connection = sqlite3.connect("studymate.db")

try:
    cursor = connection.cursor()

    columns = [
        row[1]
        for row in cursor.execute(
            "PRAGMA table_info(modules)"
        ).fetchall()
    ]

    if "parent_id" not in columns:
        cursor.execute("""
            ALTER TABLE modules
            ADD COLUMN parent_id INTEGER
            REFERENCES modules(id)
        """)
        print("Столбец parent_id успешно добавлен.")
    else:
        print("Столбец parent_id уже существует.")

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS ix_modules_parent_id
        ON modules(parent_id)
    """)

    connection.commit()
    print("Обновление базы завершено.")

finally:
    connection.close()