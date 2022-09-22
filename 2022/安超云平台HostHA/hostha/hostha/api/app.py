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

import flask
import six
from oslo_config import cfg
from oslo_log import log
from oslo_utils import uuidutils
from werkzeug import exceptions as werkzeug_exceptions

from hostha import context
from hostha.i18n import _LE
from hostha.api import v1 as api_v1
from hostha.common.utils import api as api_utils

CONF = cfg.CONF
VERSIONS = [{"id": "v1.0", "status": "CURRENT"}]
LOG = log.getLogger(__name__)

# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2013 Mirantis Inc.


def build_app(version_response=None):
    """App builder (wsgi).

    Entry point for Sahara REST API server
    """
    app = flask.Flask('hostha.api')

    version_response = (version_response or {"versions": VERSIONS})

    @app.route('/', methods=['GET'])
    def version_list():
        context.set_ctx(None)
        return api_utils.render(version_response)

    @app.teardown_request
    def teardown_request(_ex=None):
        context.set_ctx(None)

    @app.after_request
    def log_request(response):
        LOG.info("%s %s %s" % (flask.request.method,
                               flask.request.url,
                               str(response.status_code)))
        return response

    api_v1.register_blueprints(app, url_prefix='')

    def make_json_error(ex):
        status_code = (ex.code
                       if isinstance(ex, werkzeug_exceptions.HTTPException)
                       else 500)
        description = (ex.description
                       if isinstance(ex, werkzeug_exceptions.HTTPException)
                       else str(ex))

        error = {'error_id': uuidutils.generate_uuid(),
                 'error_code': status_code,
                 'error_name': 'INTERNAL_ERROR',
                 'error_message': description}

        LOG.error(_LE('Internal error: '
                      'error_id=%(error_id)s, '
                      'error_code=%(error_code)s, '
                      'error_message=%(error_message)s, '
                      'error_name=%(error_name)s' % error))

        return api_utils.render(error, status=status_code)

    for code in six.iterkeys(werkzeug_exceptions.default_exceptions):
        app.error_handler_spec[None][code] = make_json_error

    return app


class Router(object):
    def __call__(self, environ, response):
        return self.app(environ, response)

    @classmethod
    def factory(cls, global_config, **local_config):
        cls.app = build_app()
        return cls(**local_config)
