from datetime import datetime, timezone

from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, Integer, Text

from database.base import Base

class Text(Base):
    __tablename__ = "text"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    word_count: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"Text(id={self.id!r}, text={self.text!r}, word_count={self.word_count!r}, created_at={self.created_at!r})"
