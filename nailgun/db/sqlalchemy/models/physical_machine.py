# -*- coding: utf-8 -*-

#    Copyright 2013 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy import Unicode

from nailgun import consts

from nailgun.db import db
from nailgun.db.sqlalchemy.models.base import Base
from nailgun.db.sqlalchemy.models.fields import JSON


class PhysicalMachineInfo(Base):
    __tablename__ = 'physical_machine_info'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(20), nullable=False)
    ip=Column(Unicode(20), nullable=False)
    mp_ip = Column(Unicode(20), nullable=False)
    mp_username = Column(Unicode(20), nullable=False)
    mp_passwd = Column(Unicode(15), nullable=False)

    cabinet = Column(Unicode(30), nullable=False)
    gene_room = Column(Unicode(30), nullable=False)
    power_status = Column(Integer, nullable=False)
    operation_status = Column(Integer, nullable=False)

    mac = Column(Unicode(30), nullable=False)
    use_type = Column(Integer, nullable=False)
    additional_info = Column(JSON,default={})