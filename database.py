"""Module to create MYSQL database connection and execute the queries based on the arguments received from the callee.
Create datbase in mysql database and store it's name in locals.py in DB_NAME execute this file only for initial setup."""

import mysql.connector
from mysql.connector import Error

DB_HOST="localhost"
DB_USER="root"
DB_PASSWORD="root"



class DBQueries:

    """Store MYSQL database credentials in locals.py file"""
    def connect(self, db_name):
        conn=None
        try:
            # check_database(DB_NAME)
            conn = mysql.connector.connect(host=DB_HOST, database=db_name, user=DB_USER, password=DB_PASSWORD)
            if conn.is_connected():
                pass
                print('Connected to MySQL database')
            else:
                print('connection failed')
        except Error as error:
            print(error)
        finally:
            if conn is not None and conn.is_connected():
                return conn

    def _create_table(self, connection, query):
        cursor = None
        try:
            cursor = connection.cursor(buffered=True)
            cursor.execute(query)
            print('table created successfully')
        except Error as e:
            print('Error creating table', e)
        finally:
            if cursor:
                cursor.close()

    def insert_record(self, connection, query):
        # stmt = f"INSERT INTO {TABLE_NAME}(Original_File_Name,Input_File_Name) VALUES('{orgFileName}', '{inputFileName}')"
        try:
            cursor = connection.cursor()
            cursor.execute(query)
            print('record inserted')
        except Error as e:
            print('Error inserting record names', e)
            print(query)
        finally:
            cursor.close()


if __name__ == '__main__':
    database = DBQueries()
    conx = database.connect()

    conx.commit()


"""
create_table = f""

"""