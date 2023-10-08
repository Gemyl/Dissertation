import mysql.connector as connector

def get_db_connection_and_cursor():
    connection = connector.connect(host='localhost',
                                port='3306',
                                user='root',
                                password='gemyl',
                                database="scopus",
                                auth_plugin='mysql_native_password')
    
    return connection, connection.cursor()
        
def expand_column_size(new_length, table_name, column_name, connection, cursor):
    new_length_int = str(new_length)
    new_table_name = f"scopus_{table_name}"

    query = f"ALTER TABLE {new_table_name} MODIFY COLUMN {column_name} VARCHAR({new_length_int});"
    cursor.execute(query)
    connection.commit()