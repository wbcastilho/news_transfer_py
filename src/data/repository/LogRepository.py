from src.data.models.Log import Log
from datetime import date, datetime, timedelta


class LogRepository:
    @staticmethod
    def create_table():
        Log.create_table()

    @staticmethod
    def insert(data, message):
        Log.create(datetime=data, message=message)

    @staticmethod
    def all():
        return Log.select().order_by(Log.id.desc())

    @staticmethod
    def find(str_date):
        data_selecionada = datetime.strptime(str_date, '%d/%m/%Y').date()
        um_dia = timedelta(1)
        str_data_selecionada = data_selecionada.strftime('%d/%m/%Y')
        str_proxima_data = (data_selecionada + um_dia).strftime('%d/%m/%Y')

        return Log.select().where((Log.datetime >= str_data_selecionada) & (Log.datetime < str_proxima_data))\
            .order_by(Log.id.desc())
