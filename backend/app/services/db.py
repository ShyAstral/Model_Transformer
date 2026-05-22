from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import DeclarativeBase, Session

from database.text import Text
from database.metric import Metric
from database.base import Base

engine = create_engine("sqlite+pysqlite:///./database.db", echo=True)

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

def SelectText():
    stmt = select(Text.text)
    texts = []

    with Session(engine) as session:
        for row in session.execute(stmt):
            texts.append(row[0])

    return texts

def InsertMetric(tabCount, tipCount):
    with Session(engine) as session:
        reg = Metric(tab_count=tabCount, tip_count=tipCount)

        session.add(reg)
        session.commit()

        return {"id": reg.id, "tab_count": reg.tab_count, "tip_count": reg.tip_count}

def SelectMetric():
    stmt = select(func.sum(Metric.tab_count), func.sum(Metric.tip_count))

    with Session(engine) as session:
        totalTabs, totalTips =  session.execute(stmt).first()

        if not totalTabs:
            totalTabs = 0
        if not totalTips:
            totalTips = 0

    return {"total_tabs": totalTabs, "total_tips": totalTips}
