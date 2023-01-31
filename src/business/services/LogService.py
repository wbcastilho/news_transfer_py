import datetime
from src.data.repository.LogRepository import LogRepository


class LogService:
    @staticmethod
    def save(type_log: str, message: str):
        try:
            datetime_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            LogRepository.insert(data=datetime_now, type_log=type_log, message=message)
        except Exception:
            pass

    @classmethod
    def save_info(cls, message: str):
        cls.save("info", message)

    @classmethod
    def save_warning(cls, message: str):
        cls.save("warning", message)

    @classmethod
    def save_error(cls, message: str):
        cls.save("error", message)
