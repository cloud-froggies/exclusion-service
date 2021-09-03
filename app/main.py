from typing import Optional,List

from fastapi import FastAPI, HTTPException
from fastapi.logger import logger
from fastapi.param_functions import Query

import  pymysql
import os
import logging 

DB_ENDPOINT = os.environ.get('db_endpoint')
DB_ADMIN_USER = os.environ.get('db_admin_user')
DB_ADMIN_PASSWORD = os.environ.get('db_admin_password')
DB_NAME = os.environ.get('db_name')


app = FastAPI(title='Exclusion Service',version='0.1')
gunicorn_logger = logging.getLogger('gunicorn.error')
logger.handlers = gunicorn_logger.handlers
logger.setLevel(gunicorn_logger.level)

if __name__ != "main":
    logger.setLevel(gunicorn_logger.level)
else:
    logger.setLevel(logging.DEBUG)


def get_db_conn():
    try:
        conn = pymysql.connect(host=DB_ENDPOINT, user=DB_ADMIN_USER, passwd=DB_ADMIN_PASSWORD, db=DB_NAME, connect_timeout=5)
        return conn
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        raise



@app.get("/")
def read_root():
    return {"Service": "exclusion"}


@app.get("/exclusion")
def get_exclusion(advertiser_campaigns:str,publisher:int):
    campaigns = [int(i) for i in advertiser_campaigns.split(",")]
    conn = get_db_conn()
    logger.error(advertiser_campaigns,publisher)
    with conn.cursor(pymysql.cursors.DictCursor) as cursor:
        query = """SELECT c.id
        FROM publisher_exclusions e
        JOIN advertisers a ON e.advertiser_id = a.id
        JOIN advertiser_campaigns c ON a.id = c.advertiser_id
        WHERE e.publisher_id = %s
        AND c.id IN %s"""
        cursor.execute(query,(publisher,campaigns))

    if (results := cursor.fetchall()):
        return results
    else:
        raise HTTPException(status_code=404, detail= f'No se encontraron exclusiones para la el publisher {advertiser_campaigns}') 

     


