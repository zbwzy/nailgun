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


import web
import json


from nailgun import objects
from nailgun.db import db
from nailgun.db.sqlalchemy.models import ClusterSetting

from nailgun.api.v1.handlers.base import BaseHandler
from nailgun.api.v1.handlers.base import SingleHandler
from nailgun.api.v1.handlers.base import CollectionHandler
from nailgun.api.v1.handlers.base import content_json

from nailgun.logger import logger


class ClusterSettingHandler(SingleHandler):

  single = objects.ClusterSettingObject
  
  @content_json
  def POST(self):
      data={}
      x=web.input(cluster_id='0',content={})
      data['cluster_id']=x.cluster_id
      data['cluster_setting']=x.content
      clusterSetting=db().query(ClusterSetting).filter_by(cluster_id=x.cluster_id).first()
      if clusterSetting:
      	 objects.ClusterSettingObject.update(clusterSetting,{'cluster_setting':x.content})
      else:
          objects.ClusterSettingObject.create(data)
      return json.dumps({'result':'1'})

  @content_json
  def GET(self):
    x=web.input(cluster_id='0')
    clusterSetting=db().query(ClusterSetting).filter_by(cluster_id=x.cluster_id).first()
    if clusterSetting:
      return self.single.to_json(clusterSetting)
    else:
      return json.dumps({'':''})




class ClusterSettingCollectionHandler(CollectionHandler):

  collection =objects.ClusterSettingCollection
		