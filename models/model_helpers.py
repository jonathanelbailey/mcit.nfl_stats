import pandas as pd
import logging
import pyodbc

pyodbc.pooling = False
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s-%(name)s:%(levelname)s:%(message)s')
db_debug = True if logger.getEffectiveLevel() is logging.DEBUG else False


def gather_data(con, season):
    season_msg = f'Season {season}: '
    logger.info(f'{season_msg} Querying Database...')
    sql_query = f'''
    SELECT
           *,
    --     determine the winner
           IIF(home_score > away_score, home_team, IIF(home_score < away_score, away_team, 'TIE')) AS Winner
    FROM
         pbp_data
    WHERE
    --    filter by regular season
          season_type = 'REG' AND
          season = {season}
    '''
    return pd.read_sql_query(sql_query, con)


def get_game_ids(df):
    return df['game_id'].unique().tolist()


def filter_by_game_id(df, game_id):
    return df[df['game_id'] == game_id].sort_values('play_id')


def get_scoring_plays(df):
    return df[(df['sp'] == 1) & (df['play_type'] != 'no_play')]


def determine_who_scored(i, idx, row, df, scoring_plays_df, score_a, score_b):
    play_id_msg = f'Play ID {idx} (it {i}): '
    if row['posteam'] == scoring_plays_df.iloc[i + 1]['posteam']:
        logger.debug(f'{play_id_msg} Score is {score_a}')
        df.at[idx, 'Next_Score_Half'] = score_a
    else:
        logger.debug(f'{play_id_msg} Score is {score_b}')
        df.at[idx, 'Next_Score_Half'] = score_b


def determine_next_score_half(i, idx, row, df, scoring_plays_df):
    play_id_msg = f'Play ID {idx} (it {i}): '
    logger.debug(f'{play_id_msg} Determining score type...')
    if scoring_plays_df.iloc[i + 1]['touchdown'] == 1 and \
            scoring_plays_df.iloc[i + 1]['td_team'] != scoring_plays_df.iloc[i + 1]['posteam']:
        logger.debug(f'{play_id_msg} Next score is a touchdown...')
        determine_who_scored(i, idx, row, df, scoring_plays_df, 'Opp_Touchdown', 'Touchdown')
    elif scoring_plays_df.iloc[i + 1]['field_goal_result'] == 'made':
        logger.debug(f'{play_id_msg} Next score is a Field Goal...')
        determine_who_scored(i, idx, row, df, scoring_plays_df, 'Field_Goal', 'Opp_Field_Goal')
    elif scoring_plays_df.iloc[i + 1]['touchdown'] == 1:
        logger.debug(f'{play_id_msg} Next score is a Touchdown...')
        determine_who_scored(i, idx, row, df, scoring_plays_df, 'Touchdown', 'Opp_Touchdown')
    elif scoring_plays_df.iloc[i + 1]['extra_point_result'] == 'good':
        logger.debug(f'{play_id_msg} Next score is an extra point...')
        determine_who_scored(i, idx, row, df, scoring_plays_df, 'Extra_Point', 'Opp_Extra_Point')
    elif scoring_plays_df.iloc[i + 1]['two_point_conv_result'] == 'success':
        logger.debug(f'{play_id_msg} Next score is a two point conversion...')
        determine_who_scored(i, idx, row, df, scoring_plays_df, 'Two_Point_Conversion', 'Opp_Two_Point_Conversion')
    elif scoring_plays_df.iloc[i + 1]['defensive_two_point_conv'] == 1:
        logger.debug(f'{play_id_msg} Next score is a defensive two point conversion...')
        determine_who_scored(i, idx, row, df, scoring_plays_df, 'Opp_Defensive_Two_Point', 'Defensive_Two_Point')
    else:
        logger.debug(f'{play_id_msg} Next play is not a score...')
        logger.debug(f'{play_id_msg} Setting Next_Score_Half to NA')
        df.at[idx, 'Next_Score_Half'] = pd.NA


def next_score_half(df):
    game_ids = get_game_ids(df)
    for game_id in game_ids:
        game_id_msg = f'Game ID {game_id}:'
        game_df = filter_by_game_id(df, game_id)
        logger.debug(f'{game_id_msg} Game Dataframe head output: {game_df.head()}')
        scoring_plays_df = get_scoring_plays(game_df)
        logger.debug(f'{game_id_msg} Scoring Plays Dataframe head output: {scoring_plays_df.head()}')
        for idx, row in scoring_plays_df.iterrows():
            i = scoring_plays_df.index.tolist().index(idx)
            play_id_msg = f'{game_id_msg} Play ID {idx} (it {i}): '

            logger.debug(f'{play_id_msg} beginning index...')
            if i == len(scoring_plays_df.index) - 1:
                logger.debug(f'{play_id_msg} End of index...')
                logger.debug(f'{play_id_msg} Setting Next_Score_Half to NA')
                df.at[idx, 'Next_Score_Half'] = pd.NA
                logger.debug(f'{play_id_msg} Setting Drive_Score_Half to {row["drive"]}')
                df.at[idx, 'Drive_Score_Half'] = row['drive']
            else:
                logger.debug(f'{play_id_msg} Checking if the next play is a score...')
                if ((row['qtr'] in list(range(1, 6, 1)))
                        or (row['qtr'] in [1, 2] and scoring_plays_df.iloc[i + 1]['qtr'] in [3, 4, 5])
                        or (row['qtr'] in [3, 4] and scoring_plays_df.iloc[i + 1]['qtr'] == 5)):
                    logger.debug(f'{play_id_msg} Next play is not a score.')
                    logger.debug(f'{play_id_msg} Setting Next_Score_Half to No_Score')
                    df.at[idx, 'Next_Score_Half'] = 'No_Score'
                    logger.debug(f'{play_id_msg} Setting Drive_Score_Half to {row["drive"]}')
                    df.at[idx, 'Drive_Score_Half'] = row['drive']
                else:
                    logger.debug(f'{play_id_msg} Next play scores.  Setting Drive_Score_Half to {scoring_plays_df.iloc[i + 1]["drive"]}')
                    df.at[idx, 'Drive_Score_Half'] = scoring_plays_df.iloc[i + 1]['drive']

                determine_next_score_half(i, idx, row, df, scoring_plays_df)
            i += 1


def create_cal_data_df(df):
    logger.info(f'Filtering dataframe...')
    logger.debug(f'Next_Score_Half values: {df["Next_Score_Half"].unique()}')
    logger.debug(f'play_type values: {df["play_type"].unique()}')
    logger.debug(f'two_point_conv_result values: {df["two_point_conv_result"].unique()}')
    logger.debug(f'extra_point_result values: {df["extra_point_result"].unique()}')
    logger.debug(f'down values: {df["down"].unique()}')
    logger.debug(f'game_seconds_remaining values: {df["game_seconds_remaining"].unique()}')
    cal_data = df[(df.Next_Score_Half.notnull()) &
              (df.play_type.isin(["field_goal", "no_play", "pass", "punt", "run", "qb_spike"])) &
              (df.two_point_conv_result.isna()) &
              (df.extra_point_result.isna()) &
              (df.down.notnull()) &
              (df.game_seconds_remaining.notnull())]
    return cal_data[[
                'game_id',
                'Next_Score_Half',
                'Drive_Score_Half',
                'play_type',
                'game_seconds_remaining',
                'half_seconds_remaining',
                'yardline_100',
                'roof',
                'posteam',
                'defteam',
                'home_team',
                'ydstogo',
                'season',
                'qtr',
                'down',
                'week',
                'drive',
                'ep',
                'score_differential',
                'posteam_timeouts_remaining',
                'defteam_timeouts_remaining',
                'desc',
                'receiver_player_name',
                'pass_location',
                'air_yards',
                'yards_after_catch',
                'complete_pass', 'incomplete_pass', 'interception',
                'qb_hit',
                'extra_point_result',
                'field_goal_result',
                'sp',
                'Winner',
                'spread_line',
                'total_line']]


def create_cal_data_table(engine):
    for season in list(range(1999, 2022, 1)):
        season_msg = f'Season {season}: '
        logger.info(f'{season_msg} Connecting DB engine...')
        conn = engine.connect()
        data = gather_data(conn, season)
        logger.info(f'{season_msg} Closing DB Connection...')
        conn.close()
        logger.debug(f'{season_msg} Dataframe head output: {data.head()}')
        next_score_half(data)
        logger.debug(f'{season_msg} Updated Dataframe head output: {data.head()}')
        logger.info(f'{season_msg} Creating Calibration Data...')
        cal_data = create_cal_data_df(data)
        logger.debug(f'{season_msg} Calibration Dataframe head output: {cal_data.head()}')
        logger.info(f'{season_msg} Shipping calibration data to database...')
        try:
            with engine.begin() as conn:
                if season == 1999:
                    logger.info(f'{season_msg} Dropping cal_data table...')
                    conn.exec_driver_sql(f'DROP TABLE IF EXISTS cal_data')
                cal_data.to_sql('cal_data', conn, if_exists='append', index=False)
        except Exception as e:
            logger.exception(f'{season_msg} Something went wrong, rolling back update to cal_data.')
            raise e
        logger.info(f'{season_msg} Import to database complete.')
