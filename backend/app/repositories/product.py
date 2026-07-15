from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.product import Product, ProductImage, ProductKeyword, SourcingLink


class ProductRepository:
    def get_by_id(self, db: Session, product_id: int, workspace_id: int | None = None) -> Product | None:
        stmt = select(Product).where(Product.id == product_id)
        if workspace_id is not None:
            stmt = stmt.where(Product.workspace_id == workspace_id)
        return db.scalar(stmt)

    def get_by_source_url(self, db: Session, source_url: str, workspace_id: int | None = None) -> Product | None:
        stmt = select(Product).where(Product.source_url == source_url)
        if workspace_id is not None:
            stmt = stmt.where(Product.workspace_id == workspace_id)
        return db.scalar(stmt)

    def list(self, db: Session, search: str | None, skip: int, limit: int, workspace_id: int | None = None) -> tuple[list[Product], int]:
        stmt = select(Product).order_by(Product.created_at.desc())
        count_stmt = select(func.count(Product.id))
        if workspace_id is not None:
            stmt = stmt.where(Product.workspace_id == workspace_id)
            count_stmt = count_stmt.where(Product.workspace_id == workspace_id)

        if search:
            keyword = f"%{search}%"
            condition = or_(
                Product.title.ilike(keyword),
                Product.title_zh.ilike(keyword),
                Product.description_text.ilike(keyword),
            )
            stmt = stmt.where(condition)
            count_stmt = count_stmt.where(condition)

        items = list(db.scalars(stmt.offset(skip).limit(limit)))
        total = db.scalar(count_stmt) or 0
        return items, total

    def create(self, db: Session, **kwargs) -> Product:
        product = Product(**kwargs)
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    def save(self, db: Session, product: Product) -> Product:
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    def delete(self, db: Session, product: Product) -> None:
        db.delete(product)
        db.commit()

    def delete_many(self, db: Session, products: list[Product]) -> list[int]:
        deleted_ids = [product.id for product in products]
        for product in products:
            db.delete(product)
        db.commit()
        return deleted_ids

    def replace_images(self, db: Session, product: Product, image_urls: list[str]) -> None:
        for image in list(product.images):
            db.delete(image)
        db.flush()
        for index, image_url in enumerate(image_urls):
            db.add(
                ProductImage(
                    product_id=product.id,
                    image_url=image_url,
                    sort_order=index,
                    is_primary=index == 0,
                )
            )
        db.commit()
        db.refresh(product)

    def replace_keywords(self, db: Session, product: Product, analysis_id: int, grouped_keywords: dict[str, list[str]]) -> None:
        db.query(ProductKeyword).filter(ProductKeyword.product_id == product.id).delete()
        for keyword_type, values in grouped_keywords.items():
            for index, value in enumerate(values):
                db.add(
                    ProductKeyword(
                        product_id=product.id,
                        analysis_id=analysis_id,
                        keyword_type=keyword_type,
                        keyword_text=value,
                        sort_order=index,
                    )
                )
        db.commit()

    def replace_sourcing_links(self, db: Session, product: Product, analysis_id: int, links: list[dict]) -> None:
        db.query(SourcingLink).filter(SourcingLink.product_id == product.id).delete()
        for item in links:
            db.add(
                SourcingLink(
                    product_id=product.id,
                    analysis_id=analysis_id,
                    source_platform_id=item["source_platform_id"],
                    keyword_text=item["keyword_text"],
                    search_url=item["search_url"],
                )
            )
        db.commit()


product_repository = ProductRepository()
