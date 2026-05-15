from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session

from database.text import Text
from database.base import Base

engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

def CreateTables():
    # Import tables so their metadata is registered on Base before create_all
    import database

    Base.metadata.create_all(bind=engine)

def InsertText(text, wordCount):
    with Session(engine) as session:
        reg = Text(text=text, word_count=wordCount)

        session.add(reg)
        session.commit()

        return {"id": reg.id, "text": reg.text, "word_count": reg.word_count}
