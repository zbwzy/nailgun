# -*- coding: utf-8 -*-

from nailgun.db import db
from nailgun.db.sqlalchemy.models.release import Release


def getRelease():
	release=db().query(Release).filter_by(id=1).first()
	return release
    