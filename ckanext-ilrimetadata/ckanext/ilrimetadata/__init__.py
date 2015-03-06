# this is a namespace package

import json

from sqlalchemy import create_engine

from .config import loadConfigVar

from .dbmodels import (
     DBSession,
    Base,
)

try:

    #Creates an SQLAlchemy engine with the confguration parameters
    engine = create_engine("mysql://" + loadConfigVar("user") + ":" + loadConfigVar("password") + "@" + loadConfigVar("host") + "/" + loadConfigVar("schema"),
                           pool_size=20, max_overflow=0, pool_recycle=3600)

    #Sets the engine to the session and the Base model class
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    import pkg_resources
    pkg_resources.declare_namespace(__name__)
except ImportError:
    import pkgutil
    __path__ = pkgutil.extend_path(__path__, __name__)
