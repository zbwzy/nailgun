/*
 * Copyright 2013 Mirantis, Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may
 * not use this file except in compliance with the License. You may obtain
 * a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
**/
define(
[
    'jquery',
    'underscore',
    'utils',
    'models',
    'views/common',
    'backbone',
    'views/cluster_page',
    'jsx!views/dialogs',
    'text!templates/cluster/clustercustom_setting.html',
],
function($, _, utils, models, commonViews, Backbone, clusterPageviews, dialogs, CloudSettingsTemplate) {
    'use strict';
    var CloudSettingsTab;

    CloudSettingsTab = commonViews.Tab.extend({
        className: 'openstack-settings wrapper',
        template: _.template(CloudSettingsTemplate),
        initialize: function(options) {
            _.defaults(this, options);
        },
         events:{
            'click #btnloadDefault':'loadDefaults',
            'click #btn_save':'SaveSetting',
            'blur input':"validate"
        },
        loadDefaults:function(){  
          Backbone.history.loadUrl();
        },
        onDeployRequest:function() {
            var cluster=app.page.model;
            utils.showDialog(dialogs.DeployChangesDialog, {cluster: cluster});
        },
        SaveSetting:function(){
           var cluster_settings={};

           var mysql={};
               mysql["mysql_vip"]=this.$('#txt_mysql_vip').val();
               mysql["mysql_vip_interface"]=this.$('#txt_mysql_vipinterface').val();
               mysql["root_password"]=this.$('#txt_root_password').val();
               mysql["action"]="config"; //此参数需要程序动态修改,不能被用户修改。

           var rabbitmq={};
               rabbitmq["rabbit_userid"]=this.$('#txt_rabbitmq_userid').val();
               rabbitmq["rabbit_password"]=this.$('#txt_rabbitmq_password').val();
               rabbitmq["rabbit_vip"]=this.$('#txt_rabbitmq_vip').val();
               rabbitmq["rabbit_vip_interface"]=this.$('#txt_rabbitmq_vipinterface').val();
               rabbitmq["action"]="config";

          var mongodb={};
              mongodb["mongo_user"]=this.$('#txt_mongodb_userid').val();
              mongodb["mongo_password"]=this.$('#txt_mongodb_password').val();
              mongodb["mongodb_vip"]=this.$('#txt_mongodb_vip').val();
              mongodb["mongodb_vip_interface"]=this.$('#txt_mongodb_vipinterface').val();

           var keystone={};
               keystone["keystone_mysql_user"]=this.$('#txt_keystone_mysqluser').val();
               keystone["keystone_mysql_password"]=this.$('#txt_keystone_mysqlpassword').val();
               keystone["keystone_vip"]=this.$('#txt_keystone_vip').val();
               keystone["keystone_vip_interface"]=this.$('#txt_keystone_vipinterface').val();

           var glance={};
               glance["glance_vip"]=this.$('#txt_glance_vip').val();
               glance["glance_vip_interface"]=this.$('#txt_glance_vipinterface').val();
               glance["glance_mysql_user"]=this.$('#txt_glance_mysqluser').val();
               glance["glance_mysql_password"]=this.$('#txt_glance_mysqlpassword').val();

           var nova={};
               nova["nova_vip"]=this.$('#txt_nova_vip').val();
               nova["nova_vip_interface"]=this.$('#txt_nova_vipinterface').val();
               nova["nova_mysql_user"]=this.$('#txt_nova_mysqluser').val();
               nova["nova_mysql_password"]=this.$('#txt_nova_mysqlpassword').val();

           var novacompute={};
               novacompute["virt_type"]=this.$("input[name='hypervisor']:checked").val();
              
           var neutronserver={};
               neutronserver["neutron_vip"]=this.$('#txt_neutron_vip').val();
               neutronserver["neutron_vip_interface"]=this.$('#txt_neutron_vipinterface').val();
               neutronserver["neutron_mysql_user"]=this.$('#txt_neutron_mysqluser').val();
               neutronserver["neutron_mysql_password"]=this.$('#txt_neutron_mysqlpassword').val();
               neutronserver["neutron_network_mode"]=this.$("input[name='neutronmode']:checked").val();

           var neutronagent={};
               neutronagent["neutron_network_mode"]=this.$("input[name='neutronmode2']:checked").val();
           
           var horizon={};
               horizon['dashboard_vip']=this.$('#txt_horizon_vip').val();
               horizon['dashboard_vip_interface']=this.$('#txt_horizon_vipinterface').val();

           var cinder={};
               cinder['cinder_vip']=this.$('#txt_cinder_vip').val();
               cinder['cinder_vip_interface']=this.$('#txt_cinder_vipinterface').val();
               cinder['cinder_mysql_user']=this.$('#txt_cinder_mysqluser').val();
               cinder['cinder_mysql_password']=this.$('#txt_cinder_mysqlpassword').val();

           var cinderstorage={};
               cinderstorage['cinder_mysql_user']=this.$('#txt_cinderstorage_mysqluser').val();
               cinderstorage['cinder_mysql_password']=this.$('#txt_cinderstorage_mysqlpassword').val();

           var ceilometer={};
               ceilometer['ceilometer_vip']=this.$('#txt_ceilometer_vip').val();
               ceilometer['ceilometer_vip_interface']=this.$('#txt_ceilometer_vipinterface').val();
               ceilometer['ceilometer_mongo_user']=this.$('#txt_ceilometer_mongouser').val();
               ceilometer['ceilometer_mongo_password']=this.$('#txt_ceilometer_mongopassword').val();

           var heat={};
               heat['heat_vip']=this.$('#txt_heat_vip').val();
               heat['heat_vip_interface']=this.$('#txt_heat_vipinterface').val();
               heat['heat_mysql_user']=this.$('#txt_heat_mysqluser').val();
               heat['heat_mysql_password']=this.$('#txt_heat_mysqlpassword').val();


           cluster_settings["mysql"]=mysql;
           cluster_settings["rabbitmq"]=rabbitmq;
           cluster_settings["mongodb"]=mongodb;
           cluster_settings["keystone"]=keystone;
           cluster_settings["glance"]=glance;
           cluster_settings["nova-api"]=nova;
           cluster_settings["nova-compute"]=novacompute;
           cluster_settings["neutron-server"]=neutronserver;
           cluster_settings["neutron-agent"]=neutronagent;
           cluster_settings["horizon"]=horizon;
           cluster_settings["cinder-api"]=cinder;
           cluster_settings["cinder-storage"]=cinderstorage;
           cluster_settings["ceilometer"]=ceilometer;
           cluster_settings["heat"]=heat;

           var errorslength=this.$('input.error').length;
           var vipisnull=this.checkvip(mysql["mysql_vip"],keystone["keystone_vip"],glance["glance_vip"],nova["nova_api_vip"],neutronserver["neutron_server_vip"],cinder['cinder_api_vip'],horizon['dashboard_vip'],ceilometer['ceilometer_vip']);
           if(errorslength>0)
           {
             alert("输入有误,不能保存!");
             return;
           }
           else if(vipisnull)
           {
             alert("有VIP输入项为空,不能保存!");
             return;
           }
           else
           {
             var cluster_id=this.page.model.id;
             $.ajax({
                  type: "POST",
                  url: "/api/clusterseting/save/",
                  data: "cluster_id="+cluster_id+"&content="+JSON.stringify(cluster_settings),
                  success: _.bind(function(msg){
                      var cluster=this.page.model;
                      var nodes = cluster.get('nodes');
                      var msgflag=cluster.get('release').get('state')!='available' || (!cluster.hasChanges() && !cluster.needsRedeployment()) || nodes.every({status: 'ready', pending_deletion: false});
                      if(msgflag==false)
                      { 
                         //不支持ie
                        $(".deploy-btn").attr("disabled",false);
                        $(".deploy-btn").click(this.onDeployRequest);
                        $("#showsetmsg").attr("display","none");
                        cluster.set({cluster_setting: cluster_settings});
                      }
                     alert('保存成功!');
                    },this),
                 error:function(msg)
                  {
                      alert('保存失败!');
                   }
               });
            }
        },
        checkvip:function()
        {
         var re=false;
         for(var t=0;t<arguments.length;t++) 
         {
           if(arguments[t]=="")
           {
            re=true;
            break;
           }
           else
           {
            continue;
           }
         }
         return re;
        },
        validate:function(e)
        {
           var ele=this.$(e.currentTarget);
           var datatype=ele.attr("data-type");
           var data=ele.val();
           if(_.isEmpty(data))
           {
             this.handlerrormsg(ele,'不能为空');
           }
           else
           {
             if(datatype)
             {
               this.checkdataformat(ele,data,datatype);
             }
             else
             {
              this.handlerrormsg(ele);
             }
           }
        },
        checkdataformat:function(ele,data,datatype)
         {
          if(datatype=="num")
             {
               if(!data.match(utils.regexes.number))
               {
                 this.handlerrormsg(ele,'格式必须为整数');
               }
               else
               {
                 this.handlerrormsg(ele);
               }
             }
          else if(datatype=="ip")
             {
                if(!data.match(utils.regexes.ip))
                {
                  this.handlerrormsg(ele,'格式必须为ip');
                }
                else
                {
                 this.handlerrormsg(ele);
                }
             }
         },
         handlerrormsg:function(obj,msg){
           var title=obj.prev().children().html();
           var discontrol=obj.parent().next();
           if(msg){
              obj.addClass('error');
              discontrol.addClass('error');
              discontrol.html("<font color='#b94a48'>"+title+msg+"</font>");
            }
          else
           {
             obj.removeClass('error');
             discontrol.html("");
           }
        },
        bindradiovale:function(cluster_setting)
        {
          //因为是异步调用,当从后台取到数据的时候dom还没有加载完成
          //所以在这里获取不到dom下面的节点数据,操作无效
          //console.log(cluster_setting['nova-compute']);
          if(cluster_setting['nova-compute'])
          {
             var virt_type=cluster_setting['nova-compute'].virt_type;
             //alert(virt_type);
             //this.$("input[name=hypervisor][value='qemu']").attr("checked",true);
             //this.$("input[name='hypervisor']").eq(0).checked;
             //console.log(this.$("input:radio[name='hypervisor']"));
          }
          else
          {
            this.$("input[name=hypervisor]:eq(0)").attr("checked",'checked');
          }
        },
        render: function() {
         /* if(app.selectedRoles){*/
          var cluster_id=this.page.model.id;
          $.ajax({
                type: "GET",
                url: "/api/clusterseting/save/",
                data: "cluster_id="+cluster_id,
                success: _.bind(function(msg){
                  var result={};
                  if(msg.cluster_setting)
                  {
                    result=JSON.parse(msg.cluster_setting)
                    this.bindradiovale(result);
                  }
                  else
                  {
                    result=msg;
                  }
                  this.$el.html(this.template({data:result}));
                },this),
                error:function(msg)
                {
                   alert('获取设置信息失败!');
                }
            });
            app.selectedRoles=null;
            return this;
         /* }
          else
          {
            alert('请先选择需要安装的角色信息');
            return;
          }*/
        }
    });
    return CloudSettingsTab;
});
