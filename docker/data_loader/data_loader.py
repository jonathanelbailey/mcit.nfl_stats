import nfl_data_py as nfl
import sqlalchemy
import pyodbc
import urllib
import sys
from os import getenv
import logging

pyodbc.pooling = False

table_map = {
    'pbp_data': nfl.import_pbp_data,
    'weekly_data': nfl.import_weekly_data,
    'seasonal_data': nfl.import_seasonal_data,
    'win_totals': nfl.import_win_totals,
    'sc_lines': nfl.import_sc_lines,
    'draft_picks': nfl.import_draft_picks,
    'schedules': nfl.import_schedules,
    'combine_data': nfl.import_combine_data,
    'ngs_data_receiving': nfl.import_ngs_data,
    'ngs_data_passing': nfl.import_ngs_data,
    'ngs_data_rushing': nfl.import_ngs_data,
    'depth_charts': nfl.import_depth_charts,
    'injuries': nfl.import_injuries,
    'qbr': nfl.import_qbr,
    'pfr_passing': nfl.import_pfr_passing,
    'snap_counts': nfl.import_snap_counts,
    'rosters': nfl.import_rosters,
    'officials': nfl.import_officials,
    'draft_values': nfl.import_draft_values,
    'team_desc': nfl.import_team_desc,
    'ids': nfl.import_ids
}


def import_table_to_df(year=None, extra_params=None):
    if table_to_update in ['team_desc', 'draft_values', 'ids']:
        return table_map[table_to_update]()
    if extra_params != 'None':
        params = {'years': [int(year)], 'stat_type': extra_params}
        return table_map[table_to_update](**params)
    else:
        return table_map[table_to_update]([int(year)])


def connect_to_db(server, database, user, password):
    engine = sqlalchemy.create_engine(
        "mssql+pyodbc:///?odbc_connect={}".format(
            urllib.parse.quote_plus(
                "DSN={0};DATABASE={1};UID={2};PWD={3}".format(
                    server,
                    database,
                    user,
                    password
                )
            )
        ),
        echo=True,
        fast_executemany=True
    )
    return engine.begin()


def import_table_to_db(conn, df, table):
    df.to_sql(table, conn, if_exists='append', index=False)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(threadName)s -  %(levelname)s - %(message)s')
    table_to_update = sys.argv[1]
    year = sys.argv[2]
    update_method = sys.argv[3]
    extra_params = sys.argv[4]
    server = getenv('DB_SERVER')
    database = getenv('DB_NAME')
    user = getenv('DB_USER')
    password = getenv('DB_PW')

    logging.info(f"PARAMETERS RECEIVED")
    logging.info(f"Database: {database}")
    logging.info(f"Table to be updated: {table_to_update}")
    logging.info(f"Season: {year}")
    logging.info(f"Update Type: {update_method}")
    logging.info(f"Extra Params: {extra_params}")

    if update_method == 'append':
        logging.info(f'beginning {table_to_update} import for season {year}')
        imported_df = import_table_to_df(year, extra_params)
    if update_method == 'replace':
        logging.warning(f'Dropping {table_to_update} from {database}')
        try:
            logging.info(f'beginning {table_to_update} {update_method} of {table_to_update}')
            logging.info(f'Connecting to {database} on {server}')
            with connect_to_db(server, database, user, password) as conn:
                logging.info(f'Connected to {database} on {server}')
                logging.info(f'Connected')
                conn.exec_driver_sql(f'DROP TABLE IF EXISTS {table_to_update}')
        except Exception as e:
            logging.error(f'Something went wrong, rolling back change...')
            raise logging.error(e)
        logging.info(f'{table_to_update} dropped successfully')
        exit(0)
    else:
        logging.info(f'{update_method} of {table_to_update} on {database}: adding season {year} data')
        try:
            logging.info(f'beginning {table_to_update} {update_method} of {table_to_update}')
            logging.info(f'Connecting to {database} on {server}')
            with connect_to_db(server, database, user, password) as conn:
                logging.info(f'Connected to {database} on {server}')
                logging.info(f'Connected')
                import_table_to_db(conn, imported_df, table_to_update)
        except Exception as e:
            logging.error(f'Something went wrong, rolling back season {year} {update_method} to {table_to_update}')
            raise logging.error(e)
        logging.info(f'Completed {table_to_update} import to database {database} for {year}')

