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

import webob
from keystonemiddleware import auth_token
from webob import exc
from oslo_utils import uuidutils
from oslo_log import log
from hostha.i18n import _LE


LOG = log.getLogger(__name__)


class Auth(auth_token.AuthProtocol):

    def process_request(self, request):
        try:
            return super(Auth, self).process_request(request)
        except exc.HTTPServiceUnavailable:
            message = "[keystone_tokenauth] configuration error"
        except Exception as ex:
            LOG.exception("[keystone_tokenauth] configuration error")
            message = str(ex)
        e = {
            "error_name": "KeystonemiddlewareConfigError",
            "error_message": message,
            "error_id": uuidutils.generate_uuid(),
            "error_code": "KEYSTONEMIDDLEWARE_CONFIG_ERROR"
        }
        LOG.error(_LE('Internal error: '
                      'error_id=%(error_id)s, '
                      'error_code=%(error_code)s, '
                      'error_message=%(error_message)s, '
                      'error_name=%(error_name)s' % e))
        return webob.Response(status_code=500, json_body=e)


def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def auth_filter(app):
        return Auth(app, conf)
    return auth_filter
