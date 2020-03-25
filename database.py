"""Module to create MYSQL database connection and execute the queries based on the arguments received from the callee.
Create datbase in mysql database and store it's name in locals.py in DB_NAME execute this file only for initial setup."""

import mysql.connector
from mysql.connector import Error

DB_HOST="localhost"
DB_USER="root"
DB_PASSWORD="root"
DB_NAME="Institute"



class DBQueries:

    """Store MYSQL database credentials in locals.py file"""
    def connect(self):
        conn=None
        try:
            # check_database(DB_NAME)
            conn = mysql.connector.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
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




if __name__ == '__main__':
    database = DBQueries()
    conx = database.connect()
    queries = [
        f"CREATE TABLE IF NOT EXISTS institute_institute(name VARCHAR(100), id INT AUTO_INCREMENT PRIMARY KEY, short_name VARCHAR(50), estalished_year VARCHAR(5), institute_type VARCHAR(22), country_id VARCHAR(22), state_id VARCHAR(22), state_id VARCHAR(22), city_id VARCHAR(22), brochure VARCHAR(22) )",
        f"CREATE TABLE IF NOT EXISTS institutes_institutecontactdetail(website VARCHAR(50), phone_nos VARCHAR(15), fax VARCHAR(15), email_address VARCHAR(50), main_address VARCHAR(200), latitude VARCHAR(50), longitude VARCHAR(50))",
        f"CREATE TABLE IF NOT EXISTS institutes_institutedetail(number_of_programs VARCHAR(20), campus_size VARCHAR(20), no_of_international_students VARCHAR(20), intnl_students_percent VARCHAR(20), on_campus_hostel VARCHAR(20), hostel_fee VARCHAR(20), hostel_fee_currency_id VARCHAR(20), gender_ratio VARCHAR(20), student_faculty_ratio VARCHAR(20), bachelors_masters_ratio VARCHAR(20))",
        f"CREATE TABLE IF NOT EXISTS institutes_instituteranking(ranking_authority_id VARCHAR(20), ranking_type_id VARCHAR(20), rank VARCHAR(20))",
        f"CREATE TABLE IF NOT EXISTS institute_coursefee(min_fee VARCHAR(20), max_fee VARCHAR(20), currency_id VARCHAR(20))"
        f"CREATE TABLE IF NOT EXISTS institutes_institute_intake(intake_id VARCHAR(20))"
    ]
    # database._create_table(conx)
    conx.commit()


"""
create_table = f""

"""