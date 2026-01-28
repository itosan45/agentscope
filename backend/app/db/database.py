"""
Database connection and session management
"""
from sqlmodel import SQLModel, create_engine, Session
from contextlib import contextmanager
import os

# データベースURL（環境変数から取得、デフォルトはSQLite）
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./agentscope.db")

# SQLite用の接続引数
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


def create_db_and_tables():
    """データベースとテーブルを作成"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI依存性注入用のセッション取得"""
    with Session(engine) as session:
        yield session


@contextmanager
def get_session_context():
    """コンテキストマネージャ版セッション取得"""
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
