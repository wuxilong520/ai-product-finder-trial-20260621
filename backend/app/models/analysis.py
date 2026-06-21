from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import JSON

from app.core.database import Base


json_field = JSON().with_variant(JSONB, "postgresql")


class AIAnalysisResult(Base):
    __tablename__ = "ai_analysis_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
    model_name: Mapped[str] = mapped_column(String(100))
    prompt_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    title_zh: Mapped[str | None] = mapped_column(Text, nullable=True)
    core_keywords: Mapped[list | None] = mapped_column(json_field, nullable=True)
    selling_points: Mapped[list | None] = mapped_column(json_field, nullable=True)
    sourcing_keywords: Mapped[list | None] = mapped_column(json_field, nullable=True)
    raw_response: Mapped[dict] = mapped_column(json_field)

    product = relationship("Product", back_populates="analysis_results")
    keywords = relationship("ProductKeyword", back_populates="analysis")
    sourcing_links = relationship("SourcingLink", back_populates="analysis")
