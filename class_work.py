import psycopg2


def get_course_id(cursor, name):
    cursor.execute("SELECT id FROM course WHERE name=%s;", (name,))
    return cursor.fetchone()[0]


def def_rename_id(cursor, id, name):
    cursor.execute("""
        UPDATE course 
        SET id=%s 
        WHERE name=%s;
    """, (id, name,))
    conn.commit()


conn = psycopg2.connect(
    dbname="netology_db", 
    user="postgres", 
    password="20145"
    )
with conn.cursor() as cur:
    cur.execute("""
        CREATE TABLE IF NOT EXISTS course (
            id serial PRIMARY KEY,
            name VARCHAR(40) UNIQUE
        );
    """)
    conn.commit()

    cur.execute("""
        INSERT INTO course (name) 
        VALUES ('Python'), ('Java'), ('C++')
        ON CONFLICT (name) DO NOTHING;
    """)
    conn.commit()

    cur.execute("SELECT id, name FROM course")
    records = cur.fetchall()
    record_list = [(id, name) for id, name in records]
    print(record_list)

    cur.execute("""
        INSERT INTO course (name)
        VALUES ('JavaScript')
        ON CONFLICT (name) DO NOTHING
        RETURNING id, name;
    """)
    conn.commit()
    result = cur.fetchone()
    if result:
        print(result)
    else:
        print("Not found")

    id_name = get_course_id(cur, 'Python')
    print(f"Python id: {id_name}", end="\n\n")

    # def_rename_id(cur, 4, 'JavaScript')

    cur.execute("SELECT * FROM course;")
    result = cur.fetchall()
    print(result)

conn.close() 