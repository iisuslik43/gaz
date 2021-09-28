import numpy as np
import pandas as pd
import sqlite3


def read_data(data_file):
    connection = sqlite3.connect(data_file)
    df = pd.read_sql('SELECT * FROM Chart_data JOIN Trading_session '
                     'ON Trading_session.id=Chart_data.session_id', connection)
    df['datetime'] = pd.to_datetime(df.time + ' ' + df.date, format='%H:%M:%S %Y-%m-%d')
    df['just_time'] = pd.to_datetime(df.time, format='%H:%M:%S')
    df['month'] = df['datetime'].apply(lambda x: x.month)
    df['year'] = df['datetime'].apply(lambda x: x.year)
    return df.drop(['date', 'time', 'id'], axis=1)


def with_big_monthly_sessions(df):
    sessions = df[df.trading_type == 'monthly'].session_id.value_counts().to_dict()
    big_sessions = {session: count for session, count in sessions.items() if count > 20}
    df_filtered = df[df.session_id.apply(lambda x: x in big_sessions)]
    return df_filtered


def collect_sessions_data(df, minutes_delta=5):
    start_time = pd.to_datetime('11:00:00', format='%H:%M:%S')
    data = {session: [None] for session in df.session_id.unique()}
    for i in range(2 * 60 // minutes_delta):
        left, right = start_time + pd.Timedelta(minutes=i * minutes_delta), start_time + pd.Timedelta(minutes=(i + 1) * minutes_delta)
        df_in_range = df[df.just_time.apply(lambda x: left <= x <= right)]
        for session, values in data.items():
            df_for_session = df_in_range[df_in_range.session_id == session]
            if len(df_for_session) == 0:
                values.append(values[-1])
            else:
                values.append((df_for_session.price * df_for_session.lot_size).sum() / df_for_session.lot_size.sum())
    for session, values in data.items():
        for i in range(len(values) - 1, 0, -1):
            if values[i] is None:
                values[i] = values[i + 1]
        data[session] = np.array(values[1:])
    return data
