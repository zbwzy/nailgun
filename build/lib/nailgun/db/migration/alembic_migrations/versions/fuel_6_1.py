#    Copyright 2014 Mirantis, Inc.
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

"""Fuel 6.1 migration

Revision ID: 37608259013
Revises: 1b1d4016375d
Create Date: 2014-12-16 11:35:19.872214

"""

# revision identifiers, used by Alembic.
revision = '37608259013'
down_revision = '1b1d4016375d'

from alembic import op
import sqlalchemy as sa

from nailgun.db.sqlalchemy.models import fields


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'clusters',
        sa.Column('deployment_tasks', fields.JSON(), nullable=True))
    op.add_column(
        'releases',
        sa.Column('deployment_tasks', fields.JSON(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('clusters', 'deployment_tasks')
    op.drop_column('releases', 'deployment_tasks')
    ### end Alembic commands ###
