from sqlalchemy import create_engine

def PushDataFrame(user, password, database, dataFrame):

    engine = create_engine("mysql://{user}:{pw}@localhost/{db}"
                        .format(user=user,
                                pw=password,
                                db=database))

    dataFrame.to_sql('demo1', con=engine, if_exists='append',chunksize=1000)