import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG


def get_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Ошибка подключения к БД: {e}")
        return None


def fetch_one(query, params=None):
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result
    except Error as e:
        print(f"Ошибка выполнения запроса: {e}")
        return None
    finally:
        if conn.is_connected():
            conn.close()


def fetch_all(query, params=None):
    conn = get_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except Error as e:
        print(f"Ошибка выполнения запроса: {e}")
        return []
    finally:
        if conn.is_connected():
            conn.close()