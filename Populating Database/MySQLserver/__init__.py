from sqlalchemy import create_engine
import mysql.connector as connector

def InsertDataFrame(dataFrame, name):

    engine = create_engine("mysql://{user}:{pw}@localhost/{db}"
                        .format(user='root',
                                pw='gemyl',
                                db='george'))

    dataFrame.to_sql(name, con=engine, if_exists='append',chunksize=1000)