def setupKeys():
    with open("Keys.py", "x") as f:
        f.write("disc_key = \"INSERT DISCORD KEY HERE\"" +
                "rdsEndPoint = \"INSERT RDS ENDPOINT HERE\"" +
                "rdsDBName = \"INSERT RDS DATABASENAME HERE\"" +
                "rdsUsername = \"INSERT RDS USERNAME HERE\"" +
                "rdsPassword = \"INSERT RDS PASSWORD HERE\"" +
                "rdsPort = INSERT RDS PORT # HERE (INT)")


def setupTable():
    import Keys
    import pymysql
    try:
        conn = pymysql.connect(host=Keys.rdsEndPoint,
                               user=Keys.rdsUsername,
                               passwd=Keys.rdsPassword,
                               db=Keys.rdsDBName,
                               connect_timeout=5)
        print("connection successful!")
    except pymysql.MySQLError as e:
        print("Error: Unexpected error connecting to RDS: " + str(e))
        exit()
    try:
        with conn.cursor() as cur:
            cur.execute("DROP DATABASE IF EXISTS Rust_Bot_Items;")
            cur.execute("CREATE DATABASE Rust_Bot_Items;")
            cur.execute("DROP TABLE IF EXISTS ITEMS;")
            cur.execute("CREATE TABLE ITEMS (ItemID int NOT NULL PRIMARY KEY,ItemName varchar(255) NOT NULL,ImageURL varchar(255));")
        conn.commit()
    except pymysql.MySQLError as e:
        print("Error: Unexpected error interfacing with RDS: " + str(e))
        exit()