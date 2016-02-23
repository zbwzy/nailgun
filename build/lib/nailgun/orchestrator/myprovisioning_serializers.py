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
#    新加的安装操作系统序列化

"""Provisioning serializers for orchestrator"""

from itertools import groupby

from nailgun import consts
from nailgun import objects
import netaddr

from nailgun.logger import logger
from nailgun.settings import settings


class MyProvisioningSerializer(object):
    """Provisioning serializer"""

    @classmethod
    def serialize(cls, nodes):
        """Serialize cluster for provisioning."""

        serialized_nodes = cls.serialize_nodes(nodes)
        serialized_info=cls.serialize_cobbler_info()
        serialized_info['nodes'] = serialized_nodes
        return serialized_info


    @classmethod
    def serialize_cobbler_info(cls):
        return {
            'engine': {
                'url': settings.COBBLER_URL,
                'username': settings.COBBLER_USER,
                'password': settings.COBBLER_PASSWORD,
                'master_ip': settings.MASTER_IP
            }}

    @classmethod
    def serialize_nodes(cls, nodes):
        """Serialize nodes."""
        serialized_nodes = []
        for node in nodes:
            serialized_nodes.append(cls.serialize_node(node))
        return serialized_nodes

    @classmethod
    def serialize_node(cls, node):
        """Serialize a single node."""
        serialized_node = {
            'uid': node.uid,
            'power_address': node.ip,
            'name': objects.Node.make_slave_name(node),
            # right now it duplicates to avoid possible issues
            'slave_name': objects.Node.make_slave_name(node),
            'hostname': node.fqdn,
            'power_pass': cls.get_ssh_key_path(node),
            'profile': node.release.profilename,
            'power_type': 'ssh',
            'power_user': 'root',
            'name_servers': '\"%s\"' % settings.DNS_SERVERS,
            'name_servers_search': '\"%s\"' % settings.DNS_SEARCH,
            'netboot_enabled': '1',
            # For provisioning phase
            'kernel_options': {
                'netcfg/choose_interface': node.admin_interface.mac,
                'udevrules': cls.interfaces_mapping_for_udev(node)},
            'ks_meta': {
                'pm_data': {
                    'ks_spaces': node.attributes.volumes,
                    'kernel_params': objects.Node.get_kernel_params(node)},
                'fuel_version': '6.0',
                'puppet_auto_setup': 1,
                'puppet_master': settings.PUPPET_MASTER_HOST,
                'puppet_enable': 0,
                'mco_auto_setup': 1,
                'install_log_2_syslog': 1,
                'mco_pskey': settings.MCO_PSKEY,
                'mco_vhost': settings.MCO_VHOST,
                'mco_host': settings.MCO_HOST,
                'mco_user': settings.MCO_USER,
                'mco_password': settings.MCO_PASSWORD,
                'mco_connector': settings.MCO_CONNECTOR,
                'mco_enable': 1,
                #'auth_key': "\"%s\"" % cluster_attrs.get('auth_key', ''),
                "auth_key": "\"\"",
                'master_ip': settings.MASTER_IP
            }}

        # provision_data = cluster_attrs.get('provision')
        # if provision_data:
        #     if provision_data['method'] == consts.PROVISION_METHODS.image:
        #         serialized_node['ks_meta']['image_data'] = \
        #             provision_data['image_data']
        
        orchestrator_data = objects.Release.get_orchestrator_data_dict(
            node.release)
        #这个地方现在默认设置为2,以后要接收页面上传递的数据
        #这个要去数据库修改对应的列的内容
        if orchestrator_data:
            serialized_node['ks_meta']['repo_metadata'] = \
            orchestrator_data['repo_metadata']

        #orchestrator_data['repo_metadata']
        # vlan_splinters = cluster_attrs.get('vlan_splinters', {})
        # if vlan_splinters.get('vswitch') == 'kernel_lt':
        #     serialized_node['ks_meta']['kernel_lt'] = 1

        # mellanox_data = cluster_attrs.get('neutron_mellanox')
        # if mellanox_data:
        #     serialized_node['ks_meta'].update({
        #         'mlnx_vf_num': mellanox_data['vf_num'],
        #         'mlnx_plugin_mode': mellanox_data['plugin'],
        #         'mlnx_iser_enabled': cluster_attrs['storage']['iser'],
        #     })

            # Add relevant kernel parameter when using Mellanox SR-IOV
            # and/or iSER (which works on top of a probed virtual function)
            # unless it was explicitly added by the user
            pm_data = serialized_node['ks_meta']['pm_data']

            # if ((mellanox_data['plugin'] == 'ethernet' or
            #         cluster_attrs['storage']['iser'] is True) and
            #         'intel_iommu=' not in pm_data['kernel_params']):
            #             pm_data['kernel_params'] += ' intel_iommu=on'

        net_manager = objects.Node.get_network_manager(node)
        gw = net_manager.get_default_gateway(node.id)

        # serialized_node['ks_meta'].update({'gw': gw})
        # serialized_node['ks_meta'].update(
        #     {'admin_net': net_manager.get_admin_network_group(node.id).cidr}
        # )

        serialized_node.update(cls.serialize_interfaces(node))

        return serialized_node

    @classmethod
    def serialize_interfaces(cls, node):
        interfaces = {}
        interfaces_extra = {}
        net_manager = objects.Node.get_network_manager(node)
        admin_ip = net_manager.get_admin_ip_for_node(node.id)
        admin_netmask = str(netaddr.IPNetwork(
            net_manager.get_admin_network_group(node.id).cidr
        ).netmask)

        for interface in node.nic_interfaces:
            name = interface.name

            interfaces[name] = {
                'mac_address': interface.mac,
                'static': '0'}

            # interfaces_extra field in cobbler ks_meta
            # means some extra data for network interfaces
            # configuration. It is used by cobbler snippet.
            # For example, cobbler interface model does not
            # have 'peerdns' field, but we need this field
            # to be configured. So we use interfaces_extra
            # branch in order to set this unsupported field.
            interfaces_extra[name] = {
                'peerdns': 'no',
                'onboot': 'no'}

            # We want node to be able to PXE boot via any of its
            # interfaces. That is why we add all discovered
            # interfaces into cobbler system. But we want
            # assignted fqdn to be resolved into one IP address
            # because we don't completely support multiinterface
            # configuration yet.
            if interface.mac == node.mac:
                interfaces[name]['dns_name'] = node.fqdn
                interfaces[name]['netmask'] = admin_netmask
                interfaces[name]['ip_address'] = node.ip
                interfaces_extra[name]['onboot'] = 'yes'

        return {
            'interfaces': interfaces,
            'interfaces_extra': interfaces_extra}

    @classmethod
    def interfaces_mapping_for_udev(cls, node):
        """Serialize interfaces mapping for cobbler
        :param node: node model
        :returns: returns string, example:
                  00:02:03:04:04_eth0,00:02:03:04:05_eth1
        """
        return ','.join((
            '{0}_{1}'.format(i.mac, i.name) for i in node.nic_interfaces))

    @classmethod
    def get_ssh_key_path(cls, node):
        """Assign power pass depend on node state."""
        if node.status == "discover":
            logger.info(
                u'Node %s seems booted with bootstrap image', node.full_name)
            return settings.PATH_TO_BOOTSTRAP_SSH_KEY

        logger.info(u'Node %s seems booted with real system', node.full_name)
        return settings.PATH_TO_SSH_KEY


def serialize(nodes):
    """Serialize cluster for provisioning."""
    #objects.NodeCollection.prepare_for_provisioning(nodes)

    return MyProvisioningSerializer.serialize(nodes)
