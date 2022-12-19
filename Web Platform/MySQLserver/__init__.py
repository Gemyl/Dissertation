from sqlalchemy import create_engine

def PushDataFrame(dataFrame):

    engine = create_engine("mysql://{user}:{pw}@localhost/{db}"
                        .format(user='root',
                                pw='gemyl',
                                db='george'))

    dataFrame.to_sql('CorrelationTable', con=engine, if_exists='append',chunksize=1000)