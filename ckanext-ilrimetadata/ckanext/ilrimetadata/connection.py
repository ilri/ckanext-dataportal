# -*- coding: utf-8 -*-

from sqlalchemy import create_engine

from sqlalchemy.orm import scoped_session, sessionmaker

from pylons import config


def getSession():
    """
    Initialize the model for a Pyramid app.

    Activate this setup using ``config.include('wportal.models')``.

    """
    mysqlUser = config['ilriextensions.mysql.user']
    mysqlPassword = config['ilriextensions.mysql.password']
    mysqlHost = config['ilriextensions.mysql.host']
    mysqlPort = config['ilriextensions.mysql.port']
    mysqlSchema = config['ilriextensions.mysql.schema']

    engine = create_engine(
        "mysql+mysqlconnector://"
        + mysqlUser
        + ":"
        + mysqlPassword
        + "@"
        + mysqlHost
        + ":"
        + mysqlPort
        + "/"
        + mysqlSchema,
        pool_size=20,
        max_overflow=0,
        pool_recycle=2000,
    )
    DBSession = scoped_session(sessionmaker())
    DBSession.configure(bind=engine)

    return DBSession


def closeSession(DBSession):
    try:
        DBSession.commit()
    except Exception as e:
        print "*************************666"
        print e
        print "*************************666"
        try:
            DBSession.rollback()
        except:
            pass
    DBSession.close()
