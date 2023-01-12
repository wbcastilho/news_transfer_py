from src.data.models.Log import Log


class LogRepository:
    @staticmethod
    def create_table():
        Log.create_table()

    @staticmethod
    def insert(datetime, message):
        Log.create(datetime=datetime, message=message)

    @staticmethod
    def all():
        return Log.select().order_by(Log.id.desc())
