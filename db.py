import logging
from typing import Any, Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String, create_engine
from sqlalchemy.exc import NoSuchModuleError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Query, scoped_session, sessionmaker
from sqlalchemy.pool import StaticPool

logger = logging.getLogger(__name__)

_DECL_BASE: Any = declarative_base()
_SQL_DOCS_URL = "https://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls"
_DB_URL = "sqlite:///documents.sqlite"


def init_db(db_url: str = _DB_URL) -> None:
    """
    :param db_url: Database to use
    :return: None
    """
    if db_url is None:
        db_url = _DB_URL

    kwargs = {}

    # Take care of thread ownership if in-memory db
    if db_url == "sqlite://":
        kwargs.update(
            {
                "connect_args": {"check_same_thread": False},
                "poolclass": StaticPool,
                "echo": False,
            }
        )

    try:
        engine = create_engine(db_url, **kwargs)
    except NoSuchModuleError as e:
        raise Exception from e

    # https://docs.sqlalchemy.org/en/13/orm/contextual.html#thread-local-scope
    # Scoped sessions proxy requests to the appropriate thread-local session.
    # We should use the scoped_session object - not a separately initialized version

    Listing._session = scoped_session(
        sessionmaker(bind=engine, autoflush=True, autocommit=True)
    )
    Listing.query = Listing._session.query_property()

    _DECL_BASE.metadata.create_all(engine)


class Listing(_DECL_BASE):
    """
    Listing database model.
    """

    __tablename__ = "items"

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    doc_name = Column(String, unique=True)
    scan_date = Column(DateTime, default=None, nullable=True)
    scanned = Column(Boolean, default=False, nullable=True)
    scan_results = Column(String, default=None, nullable=True)
    size_in_mb = Column(Integer, default=0, nullable=True)

    def to_json(self):
        return {i: k for i, k in vars(self).items() if not i.startswith("_")}

    @staticmethod
    def query_doc(
        doc_name: Optional[str] = None, scanned: Optional[bool] = None
    ) -> Query:

        filters = []
        if doc_name is not None:
            filters.append(Listing.doc_name == doc_name)
        if scanned is not None:
            filters.append(Listing.scanned == scanned)
        return Listing.query.filter(*filters)

    def __repr__(self) -> str:
        return str(self.to_json())


if __name__ == "__main__":
    init_db(_DB_URL)
    pass
