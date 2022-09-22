# Copyright (c) 2021 Archeros Inc.
# hostha is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the
# Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#          http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

HOST_HA_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "hostname": {
            "type": "string",
            "minLength": 1,
            "maxLength": 255
        },
        "host_ha_enabled": {
            "type": "integer",
        },
        "ipmi_ip": {
            "type": "string",
            "minLength": 0,
            "maxLength": 255
        },
        "ipmi_user": {
            "type": "string",
            "minLength": 0,
            "maxLength": 255
        },
        "ipmi_password": {
            "type": "string",
            "minLength": 0,
            "maxLength": 255
        }
    }
}
