from src.data.models.Log import Log
from datetime import date, datetime, timedelta


class LogRepository:
    @staticmethod
    def create_table():
        Log.create_table()

    @staticmethod
    def insert(data, type_log, message):
        Log.create(datetime=data, type_log=type_log, message=message)

    @staticmethod
    def all():
        return Log.select().order_by(Log.id.desc())

    @staticmethod
    def find(str_date):
        data_selecionada = datetime.strptime(str_date, '%d/%m/%Y').date()
        um_dia = timedelta(1)
        str_data_selecionada = data_selecionada.strftime('%Y-%m-%d')
        str_proxima_data = (data_selecionada + um_dia).strftime('%Y-%m-%d')

        return Log.select().where((Log.datetime >= str_data_selecionada) & (Log.datetime < str_proxima_data))\
            .order_by(Log.id.desc())
