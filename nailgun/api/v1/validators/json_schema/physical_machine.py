# -*- coding: utf-8 -*-

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

from nailgun import consts


# TODO(@ikalnitsky): add `required` properties to all needed objects
single_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "Physicalmachine",
    "description": "Serialized Physicalmachine object",
    "type": "object",
    "properties": {
        "id": {"type": ["number","null"]},
        "name": {"type": "string"},
        "ip": {"type": "string"},
        "mp_ip": {"type": "string"},
        "mp_username": {"type": "string"},
        "mp_passwd": {"type": "string"},
        "cabinet": {"type": "string"},
        "gene_room": {"type": "string"},
        "power_status": {"type": "number"},
        "operation_status": {"type": "number"},
        "mac": {"type": "string"},
        "operation_status": {"type": "number"}
    }
}

collection_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "Physicalmachine collection",
    "description": "Serialized Physicalmachine collection",
    "type": "object",
    "items": single_schema["properties"]
}
