from peewee import (
    MySQLDatabase, Model,
    CharField, DateTimeField, IntegerField, UUIDField, BooleanField,
)
from playhouse.shortcuts import model_to_dict

__all__ = ['Alert', 'database', 'AwakeNotification']

database = MySQLDatabase(None)


class Alert(Model):
    text = CharField()
    timestamp = DateTimeField()
    level = IntegerField()
    uuid = UUIDField()
    title = CharField(null=True)
    category = CharField(null=True)
    check = CharField(null=True)
    acknowledged = BooleanField()

    class Meta:
        database = database

    def to_dict(self):
        d = model_to_dict(self)
        d['timestamp'] = str(d['timestamp'])
        d['uuid'] = str(d['uuid'])
        return d


class AwakeNotification(Model):
    username = CharField()
    last_awake_time = DateTimeField()

    class Meta:
        database = database
