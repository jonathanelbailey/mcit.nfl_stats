import nfl_data_py as nfl
import sqlalchemy
import pyodbc
import urllib
import sys
from os import getenv

table_to_update = sys.argv[1]
server = getenv('DB_SERVER')
database = getenv('DB_NAME')
user = getenv('DB_USER')
password = getenv('DB_PW')

pyodbc.pooling = False


def import_table_to_db(table_name, df, type_of_update, server, database, user, password):
    print(df.head())

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
        fast_executemany=True
    )
    conn = engine.connect()
    df.to_sql(table_name, conn, if_exists=type_of_update, index=False)


def import_yearly_table(method, year, extra_params):
    years = list(year)
    data = method(years, *extra_params)
    import_table_to_db(table_to_update, data, type_of_update, server, database, user, password)


yearly_data = ['pbp_data', 'schedules', 'weekly', 'seasonal', 'rosters', 'scoring_lines', 'officials', 'injuries']

if table_to_update in yearly_data:
    input_data = getenv('INPUT')
    with open(input_data, 'r', encoding='utf-8') as f:
        year = int(f.read())
    is_first_run = int(getenv('JOB_COMPLETION_INDEX', default='0'))
    if is_first_run == 0:
        type_of_update = 'replace'
    else:
        type_of_update = 'append'

table_type = [
    nfl.import_pbp_data,
    nfl.import_weekly_data,
    nfl.import_seasonal_data,
    nfl.import_schedules,
    nfl.import_win_totals,
    nfl.import_officials,
    nfl.import_rosters,
    nfl.import_injuries,
    nfl.import_qbr,
    nfl.import_pfr_passing,
    nfl.import_combine_data,
    nfl.import_depth_charts,
    nfl.import_sc_lines,
]

# list(map(import_yearly_table, table_type, year))
# import_yearly_table(nfl.import_ngs_data, year, extra_params={'stat_type': 'passing'})
# import_yearly_table(nfl.import_ngs_data, year, extra_params={'stat_type': 'rushing'})
# import_yearly_table(nfl.import_ngs_data, year, extra_params={'stat_type': 'receiving'})


if table_to_update == 'team_desc':
    data = nfl.import_team_desc()
    import_table_to_db(table_to_update, data, type_of_update, server, database, user, password)

if table_to_update == 'ids':
    data = nfl.import_ids()
    import_table_to_db(table_to_update, data, type_of_update, server, database, user, password)