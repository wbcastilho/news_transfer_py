import datetime
from src.data.repository.LogRepository import LogRepository


class LogService:
    @staticmethod
    def save(message: str):
        try:
            datetime_now = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            LogRepository.insert(data=datetime_now, message=message)
        except Exception:
            pass
