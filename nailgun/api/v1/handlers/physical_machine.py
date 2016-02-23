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
import re


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
   
   errormsg=""
   listdata=[]
   def POST(self):
      try:
          #self.checked_physicalmachine_data({})
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
          
          self.listdata=[] #使用类变量要注意清空,否则会循环累加
          for i in range(nrows):
              if(i>3):
                   data=self.create_data(table,i)
                   self.listdata.append(data)
          #过滤文件的前四行
          if nrows>4:  #小于4等于空文件
             for i in range(nrows):
                 if(i>3):
                   data=self.create_data(table,i)
                   self.checked_physicalmachine_data(data)
                   if self.errormsg =="":
                      objects.PhysicalMachineInfoObject.create(data)
                   else:
                     return self.showImportErrmsg(self.errormsg) 

             return self.call_success_back()           
          else: 
             self.errormsg="导入内容不能为空!"
             return self.showImportErrmsg(self.errormsg)
          #return json.dumps({'result':'1'})
      except: #匹配try语句.
        return """<script>if(window.parent.document)
                  { var pwindow=window.parent.document;
                    pwindow.getElementById('msgfail').style.display='';
                   }else{
                     window.document.getElementById('msgfail').style.display='block';
                   }</script>""" 

   def create_data(self,table,i):
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
        return data

   def call_success_back(self):
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

   def checked_physicalmachine_data(self,data):
       physicalmachineCollection=objects.PhysicalMachineInfoCollection.all()
       physicalmachineList=[]
       for physicalmachine in physicalmachineCollection:
           physicalmachineList.append(physicalmachine)
       physicalmachineList.extend(self.listdata) #合并数据库中所有记录和excel记录
       physicalmachineList.remove(data) #删除当前需要添加的data,和其他所有记录比较
       
       regexname="[~#^$@%&!、\s\\\/*]" 
       regexip="^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
       regexmac="^([0-9a-fA-F]{2}:){5}([0-9a-fA-F]{2})$"
       for physicalmachine in physicalmachineList:
           if re.search(regexname,data['name']) or len(str(data['name']).strip())<=0:
              self.errormsg="主机名({0})不能为空或者包含特殊字符,导入终止!".format(data['name'])
              break
           elif str(physicalmachine.get('name'))==str(data['name']):
              self.errormsg="主机名({0})重复,导入终止!".format(data['name'])
              break
           elif re.match(regexip,data['ip'])==None or len(str(data['ip']).strip())<=0:
              self.errormsg="ip地址({0})不能为空或者格式错误,导入终止!".format(data['ip'])
              break
           elif str(physicalmachine.get('ip'))==str(data['ip']):
              self.errormsg="IP({0})重复,导入终止!".format(data['ip'])
              break
           elif re.match(regexip,data['mp_ip'])==None or len(str(data['mp_ip']).strip())<=0:
              self.errormsg="管理口IP地址({0})不能为空或者格式错误,导入终止!".format(data['mp_ip'])
              break
           elif str(physicalmachine.get('mp_ip'))==str(data['mp_ip']):
              self.errormsg="管理口IP({0})重复,导入终止!".format(data['mp_ip'])
              break
           elif re.match(regexmac,data['mac'])==None or len(str(data['mac']).strip())<=0:
              self.errormsg="MAC地址({0})不能为空或者格式错误,导入终止!".format(data['mac'])
              break
           elif str(physicalmachine.get('mac'))==str(data['mac']):
              self.errormsg="MAC({0})重复,导入终止!".format(data['mac'])
              break
          

   def showImportErrmsg(self,errormsg):
        return """<script>if(window.parent.document){
                      var pwindow=window.parent.document.getElementById('msgfail');
                      var fireOnThis=window.parent.document.getElementById('btn_render');
                      pwindow.innerHTML='"""+self.errormsg+"""';
                      pwindow.style.color='red';
                      pwindow.style.display='';
                    }else{
                      pwindow=window.document.getElementById('msgfail');
                      var fireOnThis=window.document.getElementById('btn_render');
                      pwindow.innerHTML='"""+self.errormsg+"""';
                      pwindow.style.color='red';
                      pwindow.style.display='block';
                    }</script>"""


#查询列表和添加一条数据post请求
class PhymachineCollectionHandler(CollectionHandler):
 
 
  collection =objects.PhysicalMachineInfoCollection
  validator = physicalmachineValidator

  @content_json
  def GET(self):
        """:returns: Collection of JSONized REST objects.
        :http: * 200 (OK)
        """
        x=web.input(currentpage='1',pagesize='10',ordername='id',ordertype='desc')
        #x就是一个字典,判断是否包含pagesize键
        #web.py接收的参数默认都是字符串,即使看起来像数字

        return self.collection.getPagingData(x.currentpage,x.pagesize,x.ordername,x.ordertype)


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

     instances_ids=str(x.NodeIds[0])
     idlist=instances_ids.split(',')
     
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


class PhymachineCheckNameHandler(BaseHandler):

  def GET(self):
    x=web.input(name='',id='')
    pid=int(x.id)
    if pid<=0:
       query=objects.PhysicalMachineInfoCollection.all()
       pcount=query.filter_by(name = x.name).count()
       return json.dumps({'count':pcount})
    else:
       query = objects.PhysicalMachineInfoCollection.filter_by_not(None, id=pid)
       pcount= objects.PhysicalMachineInfoCollection.filter_by(query,name = x.name).count()
       return json.dumps({'count':pcount})


class PhymachineCheckIpHandler(BaseHandler):

  def GET(self):
    x=web.input(ip='',id='')
    pid=int(x.id)
    if pid<=0:
       query=objects.PhysicalMachineInfoCollection.all()
       pcount=query.filter_by(ip = x.ip).count()
       return json.dumps({'count':pcount})
    else:
       query = objects.PhysicalMachineInfoCollection.filter_by_not(None, id=pid)
       pcount= objects.PhysicalMachineInfoCollection.filter_by(query,ip = x.ip).count()
       return json.dumps({'count':pcount})


class PhymachineCheckMipHandler(BaseHandler):

  def GET(self):
    x=web.input(mip='',id='')
    pid=int(x.id)
    if pid<=0:
       query=objects.PhysicalMachineInfoCollection.all()
       pcount=query.filter_by(mp_ip = x.mip).count()
       return json.dumps({'count':pcount})
    else:
       query = objects.PhysicalMachineInfoCollection.filter_by_not(None, id=pid)
       pcount= objects.PhysicalMachineInfoCollection.filter_by(query,mp_ip = x.mip).count()
       return json.dumps({'count':pcount})

class PhymachineCheckMacHandler(BaseHandler):

  def GET(self):
    x=web.input(mac='',id='')
    pid=int(x.id)
    if pid<=0:
       query=objects.PhysicalMachineInfoCollection.all()
       pcount=query.filter_by(mac = x.mac).count()
       return json.dumps({'count':pcount})
    else:
       query = objects.PhysicalMachineInfoCollection.filter_by_not(None, id=pid)
       pcount= objects.PhysicalMachineInfoCollection.filter_by(query,mac = x.mac).count()
       return json.dumps({'count':pcount})







   
   





   


