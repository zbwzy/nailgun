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
import xlrd
import json
import os
import time


from nailgun import objects
from nailgun.db import db
from nailgun.db.sqlalchemy.models import PhysicalMachineInfo

from nailgun.api.v1.handlers.base import BaseHandler
from nailgun.api.v1.handlers.base import SingleHandler
from nailgun.api.v1.handlers.base import CollectionHandler
from nailgun.api.v1.handlers.base import content_json

from nailgun.api.v1.validators.physical_machine import physicalmachineValidator

from nailgun.logger import logger

from nailgun.task.manager import InstallosTaskManager



#导入excel数据
class ReadCsvHandler(BaseHandler):

   def POST(self):
        try:
          x = web.input(myfile = {})   #myfile相当于excel里面的内容
          filepath = x.myfile.filename.replace('\\','/')
          filename = filepath.split('/')[-1]
          project_path = os.path.dirname(__file__)
          filedir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), '..')
            )
          fout = open(filedir +'/'+ filename,'wb') 
          fout.write(x.myfile.file.read()) 
          fout.close()
          #上传完毕，下一步开始读取excel文件
          data = xlrd.open_workbook(filedir +'/'+ filename)
          table = data.sheets()[0]
          nrows = table.nrows
          
          #过滤文件的前四行
          for i in range(nrows):
            if(i>3):
              data={}
              data['name']=table.row(i)[0].value
              data['ip']=table.row(i)[1].value
              data['mp_ip']=table.row(i)[2].value
              data['mp_username']=table.row(i)[3].value
              data['mp_passwd']=table.row(i)[4].value
              data['cabinet']=table.row(i)[5].value
              data['gene_room']=table.row(i)[6].value
              data['power_status']=table.row(i)[7].value
              data['operation_status']=table.row(i)[8].value
              data['mac']=table.row(i)[9].value.lower()
              data['use_type']=table.row(i)[10].value
              #data['additional_info']=self._get_reserve_info()
              #logger.info(data)
              objects.PhysicalMachineInfoObject.create(data)
          return '''<script>if(window.parent.document)
                     {
                       var pwindow=window.parent.document;
                       pwindow.getElementById('msgsucess').style.display='';
                       var fireOnThis=pwindow.getElementById('btn_callback');
                         if(pwindow.createEvent)
                         { 
                           var evObj = pwindow.createEvent('MouseEvents');
                               evObj.initEvent('click',true, false);
                               fireOnThis.dispatchEvent(evObj);
                         }
                        else if(pwindow.createEventObject)
                        {  
                           fireOnThis.fireEvent('click');
                        }
                      }else{
                       window.document.getElementById('msgsucess').style.display='block';
                       var fireOnThis=window.document.getElementById('btn_callback');
                       if(window.document.createEvent)
                         {
                           var evObj = window.document.createEvent('MouseEvents');
                               evObj.initEvent('click',true, false);
                              fireOnThis.dispatchEvent(evObj);
                         }
                     else if(window.document.createEventObject)
                        {
                          fireOnThis.fireEvent('click');
                        }
                }</script>'''  
          #return json.dumps({'result':'1'})
        except:
          return "<script>if(window.parent.document){var pwindow=window.parent.document;pwindow.getElementById('msgfail').style.display='';}else{window.document.getElementById('msgfail').style.display='block';}</script>"   


#查询列表和添加一条数据post请求
class PhymachineCollectionHandler(CollectionHandler):
 
 
  collection =objects.PhysicalMachineInfoCollection
  validator = physicalmachineValidator

  @content_json
  def GET(self):
        """:returns: Collection of JSONized REST objects.
        :http: * 200 (OK)
        """
        x=web.input(currentpage='1',pagesize='10')
        #x就是一个字典,判断是否包含pagesize键
        #web.py接收的参数默认都是字符串,即使看起来像数字
      
        return self.collection.getPagingData(x.currentpage,x.pagesize)


  @content_json
  def POST(self):
        """:returns: JSONized REST object.
        :http: * 201 (object successfully created)
               * 400 (invalid object data specified)
               * 409 (object with such parameters already exists)
        """
        #如果mac地址有大写字母就改成小写
        data = self.checked_data()
        try:
            if data.get('mac'):
               data['mac']=data['mac'].lower()
            new_obj = self.collection.create(data)
        except errors.CannotCreate as exc:
            raise self.http(400, exc.message)

        raise self.http(201, self.collection.single.to_json(new_obj))



 
#修改和删除
class PhymachineHandler(SingleHandler):
   single = objects.PhysicalMachineInfoObject
   validator = physicalmachineValidator

 
  


#安装操作系统,向rabbitmq发送消息
class PhymachineInstallosHandler(BaseHandler):
   collection =objects.NodeCollection

   @content_json
   def GET(self):
     logger.info(u"开始调用安装操作系统handler")
     x=web.input(NodeIds=[],Osid='1',osName="CentOS 6.5")

     #[u'6,7'] 从前台接收到的参数是这种形式
     #这个list的长度是1,不是2
     #[6,7] 需要传递的参数是这种形式,要注意区分下
     
     installosId=x.Osid; #以后需要传递的安装操作系统id
     query=self.collection.all()

     #logger.info(type(x.NodeIds))
     #logger.info(len(x.NodeIds))
     #logger.info(instances_ids)
     #logger.info(type(str(instances_ids)))

     instances_ids=str(x.NodeIds[0])
     idlist=instances_ids.split(',')
     
     # for element in idlist:
     #     logger.info(element)
     #logger.info(len(idlist))
     nodes_to_provision=objects.NodeCollection.filter_by_list(query, 'id', idlist)
     nodes_to_provision_add=[]
     for node in nodes_to_provision:
         objects.Node.update(node,{"os_platform":x.osName})
         node.release=installosId
         nodes_to_provision_add.append(node)
     task_manager = InstallosTaskManager()
     task_manager.execute(nodes_to_provision_add)
     return json.dumps({"result":"sucess"})


class PhymachinePoweronHandler(BaseHandler):

  def POST(self):
    x=web.input(id='0',mp_ip='',mp_user='',mp_pass='')
    poweroncmd="ipmitool -I lanplus -H %s -U %s -P %s chassis power on" %(x.mp_ip,x.mp_user,x.mp_pass)
    powerstatuscmd="ipmitool -I lanplus -H %s -U %s -P %s chassis power status" %(x.mp_ip,x.mp_user,x.mp_pass)
    cmd=os.popen(poweroncmd)
    cmd=os.popen(powerstatuscmd).read()
    if cmd:
        phymachine=objects.PhysicalMachineInfoObject.get_by_uid(x.id)
        PhysicalMachineInfo.update(phymachine,{'power_status':1})
    return json.dumps({'result':cmd})


class PhymachinePoweroffHandler(BaseHandler):

  def POST(self):
    x=web.input(id='0',mp_ip='',mp_user='',mp_pass='')
    poweroffcmd="ipmitool -I lanplus -H %s -U %s -P %s chassis power off" %(x.mp_ip,x.mp_user,x.mp_pass)
    powerstatuscmd="ipmitool -I lanplus -H %s-U %s -P %s chassis power status" %(x.mp_ip,x.mp_user,x.mp_pass)
    cmd=os.popen(poweroffcmd)
    time.sleep(2)
    phymachine=objects.PhysicalMachineInfoObject.get_by_uid(x.id)
    PhysicalMachineInfo.update(phymachine,{'power_status':0})
    return json.dumps({'result':"sucess"})



   
   





   


