# -*- coding: utf-8 -*-

# BASE_API_OPTIONAL: database

from contextlib import contextmanager
from functools import wraps

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

orm: SQLAlchemy | None = None


def register_orm(web_app):
    global orm
    orm = SQLAlchemy(web_app)
    return orm


def register_migration(web_app):
    return Migrate(web_app, orm)


@contextmanager
def transaction():
    depth = orm.session.info.get('transaction_depth', 0)
    orm.session.info['transaction_depth'] = depth + 1
    try:
        yield orm.session
        if depth != 0:
            return
        orm.session.commit()
    except Exception:
        orm.session.rollback()
        raise
    finally:
        next_depth = orm.session.info.get('transaction_depth', 1) - 1
        if next_depth <= 0:
            orm.session.info.pop('transaction_depth', None)
        if next_depth > 0:
            orm.session.info['transaction_depth'] = next_depth


def atomic(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        with transaction():
            return func(*args, **kwargs)

    return wrapped
