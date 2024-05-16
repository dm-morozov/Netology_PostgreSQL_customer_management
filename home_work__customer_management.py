import psycopg2

DB_NAME = 'customer_management'
DB_USER = 'postgres'
DB_PASSWORD = '20145'

# Функция, создающая структуру БД (таблицы).
def create_table(conn):
    """
    Создает таблицы clients и phone в базе данных.

    Параметры:
    conn (psycopg2.connection): Соединение с базой данных.
    """
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients(
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(40),
                last_name VARCHAR(40),
                email VARCHAR(50) UNIQUE
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS phone(
                id_phone SERIAL PRIMARY KEY,
                phone VARCHAR(20),
                client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE
            );
        """)

        conn.commit()


# Функция, позволяющая добавить нового клиента.
def add_client(conn, first_name, last_name, email):
    """
    Добавляет нового клиента в таблицу clients.

    Параметры:
    conn (psycopg2.connection): Соединение с базой данных.
    first_name (str): Имя клиента.
    last_name (str): Фамилия клиента.
    email (str): Email клиента.

    Возвращает:
    int: ID нового клиента.
    """
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO clients(first_name, last_name, email)
            VALUES (%s, %s, %s) RETURNING id;
        """, (first_name, last_name, email))
        client_id = cursor.fetchone()[0]
        return client_id


# Функция, позволяющая добавить телефон для существующего клиента.
def add_phone(conn, client_id, phone):
    """
    Добавляет телефон для существующего клиента в таблицу phone.

    Параметры:
    conn (psycopg2.connection): Соединение с базой данных.
    client_id (int): ID клиента.
    phone (str): Номер телефона.

    Возвращает:
    int: ID добавленного телефона.
    """
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO phone(client_id, phone)
            VALUES (%s, %s) RETURNING id_phone;
        """, (client_id, phone))
        phone_id = cursor.fetchone()[0]
        return phone_id


# Функция, позволяющая изменить данные о клиенте.
def update_client(conn, client_id, first_name=None, last_name=None, email=None):
    """
    Обновляет данные о клиенте в таблице clients.

    Параметры:
    conn (psycopg2.connection): Соединение с базой данных.
    client_id (int): ID клиента.
    first_name (str, optional): Новое имя клиента.
    last_name (str, optional): Новая фамилия клиента.
    email (str, optional): Новый email клиента.

    Возвращает:
    str: Сообщение о том, какие данные были заменены.
    """
    with conn.cursor() as cursor:
        update_client_list = []
        if first_name:
            cursor.execute("""
                UPDATE clients
                SET first_name = %s
                WHERE id = %s
                RETURNING first_name;
            """, (first_name, client_id))
            update_client_list.append(first_name)
        if last_name:
            cursor.execute("""
                UPDATE clients
                SET last_name = %s
                WHERE id = %s
                RETURNING last_name;
            """, (last_name, client_id))
            update_client_list.append(last_name)
        if email:
            cursor.execute("""
                UPDATE clients
                SET email = %s
                WHERE id = %s
                RETURNING email;
            """, (email, client_id))
            update_client_list.append(email)
        conn.commit()
        return f"Данные, которые были заменены: {update_client_list}"


# Функция, позволяющая удалить телефон для существующего клиента.
def delete_phone(conn, client_id, phone_=None):
    """
    Удаляет телефон для существующего клиента из таблицы phone.

    Параметры:
    conn (psycopg2.connection): Соединение с базой данных.
    client_id (int): ID клиента.
    phone_ (str, optional): Номер телефона для удаления. Если не указан,
        удаляются все телефоны для клиента.

    Выводит сообщение о том, какие телефоны были удалены.
    """
    if not phone_:
        with conn.cursor() as cursor:
            cursor.execute("""
                DELETE FROM phone
                WHERE client_id = %s
                RETURNING phone;
            """, (client_id,))
            phones = cursor.fetchall()
            conn.commit()
        print(f"У пользователя id-{client_id} удалены номера: {[phone[0] for phone in phones]}")
    else:
        with conn.cursor() as cursor:
            cursor.execute("""
                DELETE FROM phone
                WHERE client_id = %s and phone = %s
                RETURNING phone;
            """, (client_id, phone_,))
            result = cursor.fetchall()
            conn.commit()
            if result:
                phone = result[0]
                print(f"У польщователя id-{client_id} удален телефон: {phone}")
            else:
                print(f"Телефон {phone_} не найден у пользователя id-{client_id}")


# Функция, позволяющая удалить существующего клиента.
def delete_client_for_email(conn, email):
    """
    Удаляет клиента из таблицы clients по его email.

    Параметры:
    conn (psycopg2.connection): Соединение с базой данных.
    email (str): Email клиента.

    Возвращает:
    str: Сообщение об удалении клиента или о том, что клиент не найден.
    """
    with conn.cursor() as cursor:
        cursor.execute("""
            DELETE FROM clients
            WHERE email = %s
            RETURNING first_name, email;
        """, (email,))
        first_name, email = cursor.fetchone()

    if email:
        return f"Удален: клиент {first_name}, с email адресом {email}"
    else:
        return "Клиент с таким email не найден."


# Функция, позволяющая найти клиента по его данным: имени, фамилии, email или телефону.
def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    """
    Находит клиента в таблицах clients и phone по одному или нескольким критериям.

    Параметры:
    conn (psycopg2.connection): Соединение с базой данных.
    first_name (str, optional): Имя клиента.
    last_name (str, optional): Фамилия клиента.
    email (str, optional): Email клиента.
    phone (str, optional): Номер телефона клиента.

    Возвращает:
    list: Список кортежей с данными клиентов, соответствующих заданным критериям.
          Каждый кортеж содержит id, first_name, last_name, email, phone клиента.
          Если клиент не найден, возвращает строку "По заданным условиям клиент не найден".
    str: Если не передано ни одного критерия поиска, возвращает строку "Нет данных для поиска".
    """
    request = """
        SELECT clients.id, clients.first_name, clients.last_name, clients.email, phone.phone
        FROM clients
        LEFT JOIN phone ON clients.id = phone.client_id
        WHERE
    """

    conditions = []  # условия поиска
    parameters = []  # параметры поиска

    if first_name:
        conditions.append("clients.first_name = %s")
        parameters.append(first_name)

    if last_name:
        conditions.append("clients.last_name = %s")
        parameters.append(last_name)

    if email:
        conditions.append("clients.email = %s")
        parameters.append(email)

    if phone:
        conditions.append("phone.phone = %s")
        parameters.append(phone)

    if not conditions:
        return "Нет данных для поиска"

    request += " AND ".join(conditions)
    with conn.cursor() as cursor:
        cursor.execute(request, (tuple(parameters)))
        result = cursor.fetchall()

        if result:
            return result
        else:
            return "По заданным условиям клиент не найден"

    
with psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD) as conn:
    # create_table(conn)
    client_id = add_client(conn, 'Дмитрий', 'Морозов', 'dem.morozov@gmail.com')
    print(client_id)
    phone_id = add_phone(conn, client_id, '+79033922229')
    print(phone_id, end="\n\n")
    update_client_list = update_client(conn, client_id, 'Dmitriy', 'Morozov')
    print(update_client_list, end="\n\n")

    # Ишем клиента по его данным: имени, фамилии, email или телефону.
    my_first_name = 'Dmitriy'
    my_last_name = 'Morozov'
    my_email = 'dem.morozov@gmail.com'

    results = find_client(conn, first_name=my_first_name)
    print(f"Результат поиска по имени {my_first_name}:\n\t {results}\n")

    results = find_client(conn, last_name=my_last_name, email=my_email)
    print(f"Результат поиска по фамилии {my_last_name} и по email {my_email}:\n\t {results}\n")
    
    results = find_client(conn, phone="890454646")
    print(f"Нарочно промахнемся в телефоне, и нам вернется:\n\t {results}\n")
    
    results = find_client(conn)
    print(f"Если вообще не передать параметры, то нам вернется:\n\t {results}\n")

    del_phone = delete_phone(conn, client_id, '+79033922229')
    
    print(delete_client_for_email(conn, 'dem.morozov@gmail.com'))

