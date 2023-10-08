from unittest.mock import Mock, patch
import mysql.connector as connector
import re

MAX_COLUMN_SIZE = 5000
INITIAL_COLUMNS_SIZES = {
    "scopus_publications": {
        "DOI": 0,
        "Year": 0,
        "Title": 0,
        "Journal": 0,
        "Abstract": 0,
        "Keywords": 0,
        "Fields": 0,
        "Fields_Abbreviations": 0
    }, 
    "scopus_authors": {
        "First_Name": 0,
        "Last_Name": 0,
        "Fields_Of_Study": 0,
        "Affiliations": 0
    },
    "scopus_organizations": {
        "Name": 0,
        "Address": 0,
        "City": 0,
        "Country": 0
    }

}

# functions used
def get_db_mock_connection_and_cursor():
    connection = Mock()
    cursor = connection.cursor()

    return connection, cursor

def get_db_connection_and_cursor():
    connection = connector.connect(host='localhost',
                                port='3306',
                                user='root',
                                password='gemyl',
                                database="scopus",
                                auth_plugin='mysql_native_password')
    
    return connection, connection.cursor()

def get_column_size(column_name, table_name, cursor):
    try:
        query = f"SELECT MAX(LENGTH({column_name})) FROM {table_name};"
        cursor.execute(query)
        resultSet = cursor.fetchall()

        if resultSet[0][0] != None:
            return resultSet[0][0]
        else:
            return 100
        
    except:
        return 100
    
def get_all_columns_sizes(initial_sizes, cursor):
    for table in initial_sizes.keys():
        for column in initial_sizes[table]:
            initial_sizes[table][column] = get_column_size(column, table, cursor)
    
    return initial_sizes


# functions to test
def expand_column_size(new_length, table_name, column_name, connection, cursor):
    new_length_int = str(new_length)
    query = f"ALTER TABLE {table_name} MODIFY COLUMN {column_name} VARCHAR({new_length_int});"
    cursor.execute(query)
    connection.commit()


# tests
def test_expand_column_size_over_maximum():
    connection, cursor = get_db_connection_and_cursor()

    test_list = []
    for i in range(5001):
        test_list.append('x')

    test_string = ''.join(test_list)
    query = f"INSERT INTO scopus_publications VALUES ('-','-','-','-','-','{test_string}','-','-','-',0,0,0);"

    columns_sizes = {
        "Abstract": 5000
    }

    try:
        cursor.execute(query)
        connection.commit()

    except Exception as error:
        cursor.close()
        connection.close()
        mock_connection, mock_cursor = get_db_mock_connection_and_cursor()
        
        if "Data too long" in str(error):
            pattern = r'\'+(.*?)\''
            column_name = re.search(pattern, str(error), re.IGNORECASE).group(1)
                        
            with patch.object(mock_cursor, "execute") as mock_execute:
                expand_column_size(columns_sizes[column_name], 'scopus_publications', column_name, mock_connection, mock_cursor)
                expected_query = "ALTER TABLE scopus_publications MODIFY COLUMN Abstract VARCHAR(5000);"
                mock_execute.assert_called_once_with(expected_query)
                mock_connection.commit.assert_called_once()


def test_expand_column_size_under_maximum():
    connection, cursor = get_db_connection_and_cursor()

    test_list = []
    for i in range(1000):
        test_list.append('x')

    columns_sizes = {
        "Journal": 1000
    }

    test_string = ''.join(test_list)
    query = f"INSERT INTO scopus_publications VALUES ('-','-','-','-','{test_string}','-','-','-','-',0,0,0);"

    try:
        cursor.execute(query)
        connection.commit()

    except Exception as error:
        cursor.close()
        connection.close()
        mock_connection, mock_cursor = get_db_mock_connection_and_cursor()
        
        if "Data too long" in str(error):
            pattern = r'\'+(.*?)\''
            column_name = re.search(pattern, str(error), re.IGNORECASE).group(1)
            
            with patch.object(mock_cursor, "execute") as mock_execute:
                expand_column_size(columns_sizes[column_name], 'scopus_publications', column_name, mock_connection, mock_cursor)
                expected_query = "ALTER TABLE scopus_publications MODIFY COLUMN Journal VARCHAR(1000);"
                mock_execute.assert_called_once_with(expected_query)
                mock_connection.commit.assert_called_once()