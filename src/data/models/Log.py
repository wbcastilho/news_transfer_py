from src.data.models.BaseModel import BaseModel
from peewee import TextField, DateTimeField, AutoField


class Log(BaseModel):
    id = AutoField()
    datetime = DateTimeField()
    type_log = TextField()
    message = TextField()
