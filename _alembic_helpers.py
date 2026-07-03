from alembic import op  # type: ignore[attr-defined]
from sqlalchemy import inspect


def table_exists(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def column_exists(table: str, column: str) -> bool:
    return column in [c["name"] for c in inspect(op.get_bind()).get_columns(table)]


def index_exists(table: str, index: str) -> bool:
    return index in [i["name"] for i in inspect(op.get_bind()).get_indexes(table)]
