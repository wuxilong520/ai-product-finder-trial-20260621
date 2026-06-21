from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    platform_id: Mapped[int | None] = mapped_column(ForeignKey("platforms.id", ondelete="SET NULL"), nullable=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String(255))
    path_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    external_category_id: Mapped[str | None] = mapped_column(String(128), nullable=True)

    parent = relationship("Category", remote_side=[id])
    products = relationship("Product", back_populates="category")
