from sqlalchemy.orm import Session

from app.models.crawl_run import CrawlRun


class CrawlRunRepository:
    def create(self, db: Session, **kwargs) -> CrawlRun:
        record = CrawlRun(**kwargs)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record


crawl_run_repository = CrawlRunRepository()
