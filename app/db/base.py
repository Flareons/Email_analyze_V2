import os
import urllib.parse

from typing import Annotated
from fastapi import Depends
from sqlmodel import Field, Session, SQLModel, create_engine
from dotenv import load_dotenv
from typing import Optional
from sqlalchemy import Column, Text

load_dotenv()

# Base Model cho bảng của DBS
class Email_Table(SQLModel, table=True):
    Id: Optional[int] = Field(default=None, primary_key=True)
    Timestamp: str = Field(index=True)
    sumarize: str | None = Field(default=None, sa_column=Column(Text))
    attachments_analyze: str | None = Field(default=None, sa_column=Column(Text))
    intent: str | None = Field(default=None, index=True)
    prompt_token: int | None = Field(default=None, index=True)
    generate_token: int | None = Field(default=None, index=True)
    thought_token: int | None = Field(default=None, index=True)
    total_token: int | None = Field(default=None, index=True)

# Các thông tin url cho kết nối DB
USERNAME = os.getenv("DB_USERNAME")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
DATABASE_NAME = os.getenv("DB_NAME")
PASSWORD_ENCODED = urllib.parse.quote_plus(PASSWORD)

# Url để kết nối MySQL
mysql_url = f"mysql+pymysql://{USERNAME}:{PASSWORD_ENCODED}@{HOST}:{PORT}/{DATABASE_NAME}"

# Tạo engine kết nối DB
engine = create_engine(
    mysql_url,
    echo=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    )

# Hàm tạo bảng trong DB
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Hàm lấy session kết nối DB
def get_session():
    with Session(engine) as session:
        yield session

# Session annotation để sử dụng trong các route
SessionDep = Annotated[Session, Depends(get_session)]