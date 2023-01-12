import datetime
from src.data.repository.LogRepository import LogRepository


class Log:
    @classmethod
    def save(cls, message: str) -> bool:
        try:
            datetime_now = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            LogRepository.insert(datetime=datetime_now, message=message)
            return True
        except Exception:
            return False
