from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Platform(Base):
    __tablename__ = "platforms"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    platform_type: Mapped[str] = mapped_column(String(30))
    homepage_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    products = relationship("Product", back_populates="platform")
