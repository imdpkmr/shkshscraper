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

    # def insert_lists_files(self, connection, orig, inputname):
    #     for org, ip in zip(orig, inputname):
    #         stmt = f"INSERT INTO {TABLE_NAME}(Original_File_Name,Input_File_Name) VALUES('{org}', '{ip}')"
    #         try:
    #             cursor=connection.cursor()
    #             cursor.execute(stmt)
    #             print(f"{ip} inserted")
    #         except Error as e:
    #             print('Error inserting file name', e)
    #         finally:
    #             cursor.close()

    # def insert_file_names(self, connection, orgFileName, inputFileName):
    #     stmt = f"INSERT INTO {TABLE_NAME}(Original_File_Name,Input_File_Name) VALUES('{orgFileName}', '{inputFileName}')"
    #     try:
    #         cursor = connection.cursor()
    #         cursor.execute(stmt)
    #         print('file names inserted')
    #     except Error as e:
    #         print('Error inserting file names',e)
    #     finally:
    #         cursor.close()

    # def update_status(self, connection, inputFileName, outputFileName, status, ssName=""):
    #     """update_status() method take DB reference, testID, outputFile Name, status of test cse, and screenshot name and updates the record """
    #     stmt = f"UPDATE {TABLE_NAME} SET Run_Time= CURRENT_TIMESTAMP() ,Output_File_Name='{outputFileName}',Test_Status='{status}', Error_Screenshot='{ssName}' WHERE Input_File_Name LIKE '{inputFileName}' "
    #     try:
    #         cursor = connection.cursor()
    #         cursor.execute(stmt)
    #         print('test status updated')
    #     except Error as e:
    #         print('Error updating status', e)
    #     finally:
    #         cursor.close()


    # def todays_report_csv(self,connection, query_date=None):
    #     """take date as arg, default = Today, and return a list of lists containing all the records
    #         input file names have date in the format of yyyy-mm-dd in the query"""
    #     report = list()
    #     if query_date is None:
    #         query_date = date.today()
    #     query_date = str(query_date)
    #     stmt=f"SELECT * FROM `{TABLE_NAME}` WHERE Input_File_Name LIKE '%{query_date}%'"
    #     try:
    #         cursor = connection.cursor()
    #         cursor.execute(stmt)
    #         results = cursor.fetchall()
    #         for result in results:
    #             result = list(result)
    #             if result[5] == 1:
    #                 result[5] = "pass"
    #             else:
    #                 result[5] = "fail"
    #             report.append(result)
    #     except Error as e:
    #         print('error generating csv report of today\'s test runs')
    #     finally:
    #         if cursor:
    #             cursor.close()
    #         print(report)
    #         return report



if __name__ == '__main__':
    database = DBQueries() #create object of class to call it's methods
    conx = database.connect() #get connector of the database for inserting and updating the records
    # database._create_table(conx)
    # list1=['a','b','c']
    # list2=['a11','b11','c11']
    # database.insert_file_names(connection=conx, orgFileName="testfile1", inputFileName="inputtestfile212020-03-13")
    # database.update_status(connection=conx, inputFileName="inputfile2020-03-17", outputFileName="testoutput112020-03-17", status=0, ssName="testss11")
    # database.todays_report_csv(connection=conx,query_date='2020-03-13')
    conx.commit()


