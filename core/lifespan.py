from sqlalchemy import text
from db.session import SessionLocal


class LifespanManager:
    @classmethod
    def startup(cls):
        cls._check_db_connection()

    def _check_db_connection():
        try:
            db = SessionLocal()
            db.execute(text("SELECT 1"))
        except Exception as e:
            raise e
