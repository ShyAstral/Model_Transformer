from datetime import datetime, timezone

from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, Integer

from database.base import Base

class Metric(Base):
    __tablename__ = "metric"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    tab_count: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    tip_count: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"Metric(id={self.id!r}, tab_count={self.tab_count!r}, tip_count={self.tip_count!r}, created_at={self.created_at!r})"
