import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import urlencode
from flask_login import current_user


def create_mysql_engine(user, password, host, database):
    return create_engine(
        'mysql+pymysql://{user}:{password}@{host}/{database}'.format(
            user=user, password=password, host=host, database=database
        ),
        pool_recycle=3600,  # get rid of old connections
        connect_args={'ssl': {'ssl-mode': 'preferred'}},
    )


def get_telegram_id(username, database):
    telegram_query = (
        'SELECT fid9 AS telegram_id'
        ' FROM users'
        ' JOIN userfields'
        ' ON users.uid = userfields.ufid'
        ' WHERE username = "{username}"'
        ' ;'
    ).format(username=username)

    with database.connect() as conn:
        return pd.read_sql_query(telegram_query, conn).iloc[0]['telegram_id']


def get_phonenumber(username, database):
    telephone_query = (
        'SELECT fid5 AS phonenumber'
        ' FROM users'
        ' JOIN userfields'
        ' ON users.uid = userfields.ufid'
        ' WHERE username = "{username}"'
        ' ;'
    ).format(username=username)

    with database.connect() as conn:
        return pd.read_sql_query(telephone_query, conn).iloc[0]['phonenumber']


def build_message_url(message):
    message_url = 'http://twimlets.com/message'
    return message_url + '?' + urlencode({'message': message})


def place_call(client, from_, database):
    phonenumber = get_phonenumber(current_user.username, database)
    if phonenumber:
        client.calls.create(
            url=build_message_url('Hello, your test call was successful!'),
            to=phonenumber,
            from_=from_,
            timeout=30,
        )
    else:
        raise ValueError('Shifter has no phone number')


def send_message(bot, database):
    telegram_id = get_telegram_id(current_user.username, database)
    if telegram_id:
        bot.sendMessage(telegram_id, 'Hello, {}!'.format(current_user.username))
    else:
        raise ValueError('Shifter has no telegram id')
