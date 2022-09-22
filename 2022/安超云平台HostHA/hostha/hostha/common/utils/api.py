# Copyright (c) 2016 ChinaC Inc.

import traceback

import flask
from oslo_utils import uuidutils
from oslo_serialization import jsonutils
from oslo_log import log as logging
from oslo_middleware import request_id as oslo_req_id
from werkzeug import datastructures

from hostha import context
from hostha import exceptions as ex
from hostha.common.utils import types
from hostha.common.utils import wsgi
from hostha.i18n import _
from hostha.i18n import _LE

LOG = logging.getLogger(__name__)


# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2013 Mirantis Inc.

class Rest(flask.Blueprint):
    def get(self, rule, status_code=200):
        return self._mroute('GET', rule, status_code)

    def post(self, rule, status_code=202):
        return self._mroute('POST', rule, status_code)

    def post_file(self, rule, status_code=202):
        return self._mroute('POST', rule, status_code, file_upload=True)

    def put(self, rule, status_code=202):
        return self._mroute('PUT', rule, status_code)

    def put_file(self, rule, status_code=202):
        return self._mroute('PUT', rule, status_code, file_upload=True)

    def delete(self, rule, status_code=204):
        return self._mroute('DELETE', rule, status_code)

    def patch(self, rule, status_code=202):
        return self._mroute('PATCH', rule, status_code)

    def _mroute(self, methods, rule, status_code=None, **kw):
        if type(methods) is str:
            methods = [methods]
        return self.route(rule, methods=methods, status_code=status_code, **kw)

    def route(self, rule, **options):
        status = options.pop('status_code', None)
        file_upload = options.pop('file_upload', False)

        def decorator(func):
            endpoint = options.pop('endpoint', func.__name__)

            def handler(**kwargs):
                context.set_ctx(None)

                LOG.debug("Rest.route.decorator.handler, kwargs={kwargs}"
                          .format(kwargs=kwargs))

                _init_resp_type(file_upload)

                # update status code
                if status:
                    flask.request.status_code = status

                kwargs.pop("tenant_id")
                req_id = flask.request.environ.get(oslo_req_id.ENV_REQUEST_ID)
                auth_plugin = flask.request.environ.get('keystone.token_auth')
                ctx = context.Context(
                    flask.request.headers['X-User-Id'],
                    flask.request.headers['X-Tenant-Id'],
                    flask.request.headers['X-Auth-Token'],
                    jsonutils.loads(
                        flask.request.headers['X-Service-Catalog']),
                    flask.request.headers['X-User-Name'],
                    flask.request.headers['X-Tenant-Name'],
                    flask.request.headers['X-Roles'].split(','),
                    auth_plugin=auth_plugin,
                    request_id=req_id)
                context.set_ctx(ctx)
                if flask.request.method in ['POST', 'PUT', 'PATCH']:
                    kwargs['data'] = request_data()

                try:
                    return func(**kwargs)
                except ex.Forbidden as e:
                    return access_denied(e)
                except ex.NotFoundError as e:
                    return not_found(e)
                except ex.BadRequestError as e:
                    return bad_request(e)
                except ex.CloudultraError as e:
                    return cloudultra_error(e)
                except Exception as e:
                    return internal_error(500, 'Internal Server Error', e)

            f_rule = "/<tenant_id>" + rule
            self.add_url_rule(f_rule, endpoint, handler, **options)
            self.add_url_rule(f_rule + '.json', endpoint, handler, **options)

            return func

        return decorator


class RestV2(Rest):
    def route(self, rule, **options):
        status = options.pop('status_code', None)
        file_upload = options.pop('file_upload', False)

        def decorator(func):
            endpoint = options.pop('endpoint', func.__name__)

            def handler(**kwargs):
                context.set_ctx(None)

                LOG.debug("Rest.route.decorator.handler, kwargs={kwargs}"
                          .format(kwargs=kwargs))

                _init_resp_type(file_upload)

                # update status code
                if status:
                    flask.request.status_code = status

                req_id = flask.request.environ.get(oslo_req_id.ENV_REQUEST_ID)
                auth_plugin = flask.request.environ.get('keystone.token_auth')
                ctx = context.Context(
                    user_id=flask.request.headers['X-User-Id'],
                    username=flask.request.headers['X-User-Name'],
                    tenant_id=flask.request.headers['X-Tenant-Id'],
                    tenant_name=flask.request.headers['X-Tenant-Name'],
                    auth_token=flask.request.headers['X-Auth-Token'],
                    service_catalog=flask.request.headers['X-Service-Catalog'],
                    roles=flask.request.headers['X-Roles'].split(','),
                    auth_plugin=auth_plugin,
                    request_id=req_id)
                context.set_ctx(ctx)
                if flask.request.method in ['POST', 'PUT', 'PATCH', 'GET']:
                    kwargs['data'] = request_data()

                try:
                    return func(**kwargs)
                except ex.Forbidden as e:
                    return access_denied(e)
                except ex.NotFoundError as e:
                    return not_found(e)
                except ex.BadRequestError as e:
                    return bad_request(e)
                except ex.CloudultraError as e:
                    return cloudultra_error(e)
                except Exception as e:
                    return internal_error(500, 'Internal Server Error', e)

            self.add_url_rule(rule, endpoint, handler, **options)
            self.add_url_rule(rule + '.json', endpoint, handler, **options)

            return func

        return decorator


class RestV3(Rest):
    def route(self, rule, **options):
        status = options.pop('status_code', None)
        file_upload = options.pop('file_upload', False)

        def decorator(func):
            endpoint = options.pop('endpoint', func.__name__)

            def handler(**kwargs):
                context.set_ctx(None)

                LOG.debug("Rest.route.decorator.handler, kwargs={kwargs}"
                          .format(kwargs=kwargs))

                _init_resp_type(file_upload)

                # update status code
                if status:
                    flask.request.status_code = status

                req_id = flask.request.environ.get(oslo_req_id.ENV_REQUEST_ID)
                auth_plugin = flask.request.environ.get('keystone.token_auth')
                ctx = context.Context(
                    user_id=flask.request.headers.get('X-User-Id', ''),
                    username=flask.request.headers.get('X-User-Name', ''),
                    tenant_id=flask.request.headers.get('X-Tenant-Id', ''),
                    tenant_name=flask.request.headers.get('X-Tenant-Name', ''),
                    auth_token=flask.request.headers.get('X-Auth-Token', ''),
                    service_catalog=flask.request.headers.get(
                        'X-Service-Catalog', ''),
                    roles=flask.request.headers.get('X-Roles', '').split(','),
                    auth_plugin=auth_plugin,
                    request_id=req_id,
                    with_db_session=False)
                context.set_ctx(ctx)
                if flask.request.method in ['POST', 'PUT', 'PATCH', 'GET']:
                    kwargs['data'] = request_data()

                try:
                    return func(**kwargs)
                except ex.Forbidden as e:
                    return access_denied(e)
                except ex.NotFoundError as e:
                    return not_found(e)
                except ex.BadRequestError as e:
                    return bad_request(e)
                except ex.CloudultraError as e:
                    return cloudultra_error(e)
                except Exception as e:
                    return internal_error(500, 'Internal Server Error', e)

            self.add_url_rule(rule, endpoint, handler, **options)
            self.add_url_rule(rule + '.json', endpoint, handler, **options)

            return func

        return decorator


RT_JSON = datastructures.MIMEAccept([("application/json", 1)])


def _init_resp_type(file_upload):
    """Extracts response content type."""

    # get content type from Accept header
    resp_type = flask.request.accept_mimetypes

    # url /foo.json
    if flask.request.path.endswith('.json'):
        resp_type = RT_JSON

    flask.request.resp_type = resp_type

    # set file upload flag
    flask.request.file_upload = file_upload


def render(res=None, resp_type=None, status=None, name=None,
           total_count=None, **kwargs):
    if not res and type(res) is not types.Page:
        res = {}
    if type(res) is dict:
        res.update(kwargs)

    elif type(res) is types.Page:
        result = {name: res}
        result.update(kwargs)
        if res.prev or res.next or ('marker' in get_request_args()):
            result["markers"] = {"prev": res.prev, "next": res.next}
        res = result
    elif kwargs:
        # can't merge kwargs into the non-dict res
        abort_and_log(500,
                      _("Non-dict and non-empty kwargs passed to render"))

    status_code = getattr(flask.request, 'status_code', None)
    if status:
        status_code = status
    if not status_code:
        status_code = 200

    if not resp_type:
        resp_type = getattr(flask.request, 'resp_type', RT_JSON)

    if not resp_type:
        resp_type = RT_JSON

    serializer = None
    if "application/json" in resp_type:
        resp_type = RT_JSON
        serializer = wsgi.JSONDictSerializer()
    else:
        abort_and_log(400, _("Content type '%s' isn't supported") % resp_type)

    if 'alarms' in res or 'alarm_history_items' in res:
        res['total_count'] = total_count

    body = serializer.serialize(res)
    resp_type = str(resp_type)

    return flask.Response(response=body, status=status_code,
                          mimetype=resp_type)


def request_data():
    if hasattr(flask.request, 'parsed_data'):
        return flask.request.parsed_data

    if not flask.request.content_length > 0:
        LOG.debug("Empty body provided in request")
        return dict()

    if flask.request.file_upload:
        return flask.request.data

    deserializer = None
    content_type = flask.request.mimetype
    if not content_type or content_type in RT_JSON:
        deserializer = wsgi.JSONDeserializer()
    else:
        abort_and_log(400,
                      _("Content type '%s' isn't supported") % content_type)

    # parsed request data to avoid unwanted re-parsings
    parsed_data = deserializer.deserialize(flask.request.data)['body']
    flask.request.parsed_data = parsed_data

    return flask.request.parsed_data


def get_request_args():
    return flask.request.args


def abort_and_log(status_code, descr, exc=None):
    LOG.error(_LE("Request aborted with status code {code} and "
                  "message '{message}'").format(code=status_code,
                                                message=descr))

    if exc is not None:
        LOG.error(traceback.format_exc())

    flask.abort(status_code, description=descr)


def render_error_message(error_code, error_message, error_name, error_id=""):
    message = {
        "error_code": error_code,
        "error_message": error_message,
        "error_name": error_name
    }

    if error_id:
        message["error_id"] = error_id

    resp = render(message)
    resp.status_code = error_code

    return resp


def internal_error(status_code, descr, exc=None):
    error_id = uuidutils.generate_uuid()
    LOG.error(_LE('Request aborted: '
                  'error id = {error_id}, '
                  'status code = {code},'
                  'message = "{message}"').format(error_id=error_id,
                                                  code=status_code,
                                                  message=descr))
    if exc is not None:
        LOG.error(traceback.format_exc())

    error_code = "INTERNAL_SERVER_ERROR"
    if status_code == 501:
        error_code = "NOT_IMPLEMENTED_ERROR"

    return render_error_message(status_code, descr, error_code, error_id)


def cloudultra_error(error):
    error_code = 500

    LOG.error(_LE('Internal error: '
                  'error_id={id}, '
                  'error_code={code}, '
                  'error_message={message}, '
                  'error_name={name}').format(id=error.uuid,
                                              code=error_code,
                                              message=error.message,
                                              name=error.code))

    return render_error_message(error_code,
                                error.message,
                                error.code,
                                error.uuid)


def bad_request(error):
    error_code = 400

    LOG.error(_LE('Bad request: '
                  'error_id={id}, '
                  'error_code={code}, '
                  'error_message={message}, '
                  'error_name={name}').format(id=error.uuid,
                                              code=error_code,
                                              message=error.message,
                                              name=error.code))

    return render_error_message(error_code,
                                error.message,
                                error.code,
                                error.uuid)


def access_denied(error):
    error_code = 403

    LOG.error(_LE('Access Denied: '
                  'error_id={id}, '
                  'error_code={code}, '
                  'error_message={message}, '
                  'error_name={name}').format(id=error.uuid,
                                              code=error_code,
                                              message=error.message,
                                              name=error.code))

    return render_error_message(error_code,
                                error.message,
                                error.code,
                                error.uuid)


def not_found(error):
    error_code = 404

    LOG.error(_LE('Not Found exception occurred: '
                  'error_id={id}, '
                  'error_code={code}, '
                  'error_message={message}, '
                  'error_name={name}').format(id=error.uuid,
                                              code=error_code,
                                              message=error.message,
                                              name=error.code))

    return render_error_message(error_code,
                                error.message,
                                error.code,
                                error.uuid)


def to_wrapped_dict(func, id, *args, **kwargs):
    obj = func(id, *args, **kwargs)
    if obj is None:
        e = ex.NotFoundError(
            {'id': id}, _('Object with %s not found'))

        return not_found(e)
    return render(obj.to_wrapped_dict())
