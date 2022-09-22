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

from hostha import constants

VM_EVACUATION_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "host_evacuation": {
            "type": "integer"
        },
        "source_host": {
            "type": "string",
            "minLength": 1,
            "maxLength": 255
        },
        "result": {
            "type": "integer",
            "enum": [0, 1]
        },
        "start_time": {
            "type": "string",
            "minLength": 1,
            "maxLength": 255
        },
        "end_time": {
            "type": "string",
            "minLength": 1,
            "maxLength": 255
        },
        "marker": {
            "type": "string",
            "minLength": 1,
            "maxLength": 255
        },
        "limit": {
            "type": "integer",
            "minLength": 1,
            "maxLength": 255
        },
        "sort_key": {
            "type": "string",
            "minLength": 1,
            "maxLength": 255
        },
        "sort_dir": {
            "type": "string",
            "enum": [constants.ORDER_ASC, constants.ORDER_DESC]
        }
    }
}
