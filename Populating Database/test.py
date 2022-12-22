from MySQLserver import FindAuthorsNum
import getpass

tableName = input('Table Name: ')
password = getpass.getpass('Password: ')

numAuthors = FindAuthorsNum(tableName, password)
print(numAuthors)