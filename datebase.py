def create_table(conn):
    with conn.cursor() as cur:
        cur.execute("""CREATE TABLE IF NOT EXISTS users(
                       id_user INTEGER PRIMARY KEY,
                       user_name VARCHAR(60));
                     """)
        conn.commit()
        cur.execute("""CREATE TABLE IF NOT EXISTS words(
                       id_word SERIAL PRIMARY KEY,
                       english VARCHAR(150) NOT NULL UNIQUE,
                       russian VARCHAR(60) NOT NULL);
                     """)
        conn.commit()
        cur.execute("""CREATE TABLE IF NOT EXISTS user_words(
                               id_user INTEGER NOT NULL REFERENCES users(id_user),
                               id_word INTEGER NOT NULL REFERENCES words(id_word));
                    """)
        conn.commit()


def insert_word(conn, english, russian):
    query = """INSERT INTO words(english, russian)
              VALUES(%s, %s)"""
    record = (english, russian,)
    with conn.cursor() as cur:
        cur.execute(query, record)
        conn.commit()


def insert_user(conn, id, user_name):
    query = """INSERT INTO users(id_user, user_name)
               VALUES(%s, %s)"""
    record = (id, user_name,)
    with conn.cursor() as cur:
        cur.execute(query, record)
        conn.commit()


def insert_users_words_start(conn, id_user):
    with conn.cursor() as cur:
        for i in range(1, 11):
            query = """INSERT INTO user_words(id_user, id_word)
                       VALUES(%s, %s)"""
            record = (id_user, i,)
            cur.execute(query, record)
            conn.commit()


def insert_id_user_id_word(conn, id_user, word):
    with conn.cursor() as cur:
        query = """SELECT id_word FROM words WHERE english = %s"""
        record = (word,)
        cur.execute(query, record)
        id_word = cur.fetchone()[0]
        query = """INSERT INTO user_words(id_user, id_word)
                    VALUES(%s, %s)"""
        record = (id_user, id_word,)
        cur.execute(query, record)
        conn.commit()


def check_id_user(conn, id_user):
    with conn.cursor() as cur:
        query = """SELECT id_user FROM users WHERE id_user = %s"""
        record = (id_user,)
        cur.execute(query, record)
        data = cur.fetchone()
    if data is None:
        return True


def select_random_word_for_user(conn, id_user):
    with conn.cursor() as cur:
        query = """SELECT w.english FROM words AS w INNER JOIN user_words AS uw ON w.id_word=uw.id_word
                   WHERE uw.id_user = %s;
                """
        record = (id_user,)
        cur.execute(query, record)
        records = cur.fetchall()
        list_english = []
        for row in records:
            list_english.append(row[0])

        return list_english


def translate_word(conn, english_word):
    with conn.cursor() as cur:
        query = """SELECT russian FROM words 
                   WHERE english = %s;
                   """
        record = (english_word,)
        cur.execute(query, record)
        return cur.fetchone()[0]


def delete_word(conn, id_user, word):
    with conn.cursor() as cur:
        query = """SELECT id_word FROM words WHERE english = %s;"""
        data = (word,)
        cur.execute(query, data)
        id_word = cur.fetchone()[0]
        query = """DELETE FROM user_words WHERE id_user = %s AND id_word = %s;"""
        record = (id_user, id_word,)
        cur.execute(query, record)
        conn.commit()


def check_word(conn, english_word, id_user):
    with conn.cursor() as cur:
        record = (english_word,)
        query = """SELECT id_word, english FROM words WHERE english = %s"""
        cur.execute(query, record)
        data = cur.fetchone()
        if data is None:
            return 1
        else:
            id_word = data[0]
            record = (id_user, id_word,)
            query = """SELECT * FROM user_words WHERE id_user = %s AND id_word = %s"""
            cur.execute(query, record)
            data = cur.fetchone()
            if data is None:
                return 2
            else:
                return 3


def count_word(conn, id_user):
    with conn.cursor() as cur:
        record = (id_user,)
        query = """SELECT COUNT(id_word) FROM user_words GROUP BY id_user HAVING id_user = %s"""
        cur.execute(query, record)
        data = cur.fetchone()[0]
        return data


# conn = psycopg2.connect(database='english_russian', user='postgres', password='postgres')
# create_table(conn)
# with open("data_file.json", "r") as read_file:
#     data_json = json.load(read_file)
# for data in data_json:
#     insert_word(conn, data[0], data[1])

