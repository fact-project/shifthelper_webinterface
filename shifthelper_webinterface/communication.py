import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import urlencode


def create_mysql_engine(user, password, host, database):
    return create_engine(
        'mysql+pymysql://{user}:{password}@{host}/{database}'.format(
            user=user, password=password, host=host, database=database
        )
    )


def get_telegram_id(username, database):
    telephone_query = (
        'SELECT fid9 AS telegram_id'
        ' FROM users'
        ' JOIN userfields'
        ' ON users.uid = userfields.ufid'
        ' WHERE username = "{username}"'
        ' ;'
    ).format(username=username)

    return pd.read_sql_query(telephone_query, database).iloc[0]['telegram_id']


def get_phonenumber(username, database):
    telephone_query = (
        'SELECT fid5 AS phonenumber'
        ' FROM users'
        ' JOIN userfields'
        ' ON users.uid = userfields.ufid'
        ' WHERE username = "{username}"'
        ' ;'
    ).format(username=username)

    return pd.read_sql_query(telephone_query, database).iloc[0]['phonenumber']


def build_message_url(message):
    message_url = 'http://twimlets.com/message'
    return message_url + '?' + urlencode({'message': message})


def place_call(phonenumber, client, from_):
    client.calls.create(
        url=build_message_url('Hello, your test call was successful!'),
        to=phonenumber,
        from_=from_,
        timeout=30,
    )
