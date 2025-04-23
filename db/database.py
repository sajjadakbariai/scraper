from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from configs.settings import settings
import contextlib

DATABASE_URL = settings.database_url

# ایجاد ارتباط با پایگاه داده
engine = create_engine(DATABASE_URL)

# ساخت SessionLocal برای مدیریت اتصالات به پایگاه داده
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ایجاد Base برای مدل‌ها
Base = declarative_base()

# تابع برای گرفتن اتصال پایگاه داده
@contextlib.contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    # آزمایش اتصال پایگاه داده
    print(f"Database URL: {DATABASE_URL}")
    print("Testing database connection...")
    try:
        engine.connect()
        print("Database connection successful!")
    except Exception as e:
        print(f"Database connection failed: {e}")
