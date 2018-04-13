# -*- coding: utf-8 -*-

from sqlalchemy import create_engine

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker
)

from pylons import config

def getSession():
    """
    Initialize the model for a Pyramid app.

    Activate this setup using ``config.include('wportal.models')``.

    """
    engine = create_engine("mysql+mysqlconnector://" + config['ilriextensions.mysql.user'] + ":" + config['ilriextensions.mysql.password'] + "@" + config['ilriextensions.mysql.host'] + "/" + config['ilriextensions.mysql.schema'],
                           pool_size=20, max_overflow=0, pool_recycle=2000)
    DBSession = scoped_session(sessionmaker())
    DBSession.configure(bind=engine)

    return DBSession

def closeSession(DBSession):
    try:
        DBSession.commit()
    except:
        try:
            DBSession.rollback()
        except:
            pass
    DBSession.close()