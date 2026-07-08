import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
load_dotenv()
host = os.getenv("DBHOST")
psw = os.getenv("SENHA")
dataBase = os.getenv("BASEDEDADOS")
rootUser = os.getenv("ADMIN")
port = os.getenv("PORT")
def sqlSelect(query,params):#**`sqlSelect` retorna apenas primeira linha**
    try:
        with mysql.connector.connect(
        host=host,
        user=rootUser,
        port=port,
        password=psw,
        database="clickpartiturasdb",
        charset="utf8mb4"
        ) as conn:
            with conn.cursor() as cursor:
                    cursor.execute(query,params)
                    return cursor.fetchall()
    except mysql.connector.Error as err:
        raise mysql.connector.Error("Erro Interno no Bd:",err)

def sqlQuery(query,params):
    try:
        with mysql.connector.connect(
        host=host,
        user=rootUser,
        port=port,
        password=psw,
        database="clickpartiturasdb",
        charset="utf8mb4"
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query,params)
                conn.commit()
                return cursor.rowcount
    except mysql.connector.Error as err:
        raise mysql.connector.Error("Erro Interno no Bd:",err)
