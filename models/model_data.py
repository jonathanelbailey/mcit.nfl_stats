from os import getenv
from db_utils import DBConnect
import pyodbc
from model_helpers import create_cal_data_table, create_cal_data_df, gather_data, next_score_half
import logging


pyodbc.pooling = False
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(threadName)s -  %(levelname)s - %(message)s')
db_debug = True if logger.getEffectiveLevel() is logging.DEBUG else False

server = getenv('DB_SERVER')
database = getenv('DB_NAME')
user = getenv('DB_USER')
password = getenv('DB_PW')

logging.info(f'Connecting to {server}/{database}...')
engine = DBConnect(user, password, server, database, db_debug).engine

create_cal_data_table(engine)