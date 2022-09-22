import json
import urlparse

from eventlet.green import httplib
from oslo_serialization import jsonutils
from oslo_config import cfg
from oslo_log import log

from hostha import context
from hostha import constants
from hostha import exceptions


LOG = log.getLogger(__name__)
CONF = cfg.CONF

# NOTE(zcq): Reuse configuration in group keystone_authtoken
# Some of these options are registered by Auth Middleware
# Plugin and can not be imported.

OPTS = [
    cfg.Opt('project-domain-name', default=None,
            type=type(str()), dest='project_domain_name',
            help='Domain name containing project'),
    cfg.Opt('project-name', default=None, type=type(str()),
            help='Project name to scope to',
            deprecated_opts=[cfg.DeprecatedOpt('tenant-name')]),
    cfg.Opt('username', default=None, type=type(str()),
            deprecated_opts=[cfg.DeprecatedOpt('user-name')],
            help='Username'),
    cfg.Opt('password', default=None, secret=True,
            type=type(str()), help="User's password"),
    cfg.StrOpt('auth_uri', default=None,
               help='Complete public Identity API endpoint.')
]

CONF.register_cli_opts(OPTS, group='keystone_authtoken')


_KEYSTONE_HOST = None
_KEYSTONE_PORT = None


def _get_keystone_host_and_port():
    global _KEYSTONE_HOST, _KEYSTONE_PORT
    if _KEYSTONE_HOST is None or _KEYSTONE_PORT is None:
        u = urlparse.urlparse(CONF.keystone_authtoken.auth_uri)
        _KEYSTONE_HOST = u.hostname
        _KEYSTONE_PORT = u.port
    return _KEYSTONE_HOST, _KEYSTONE_PORT


class KeystoneError(exceptions.CloudultraError):
    code = "KEYSTONE_ERROR"
    message = "Error when accessing OpenStack Keystone"


class KeystoneAuthError(exceptions.CloudultraError):
    code = "KEYSTONE_AUTH_FAIL"
    message = "Keystone authentication failure"


def request(ctx, method, url, data=None):
    if ctx.auth_token is not None:
        headers = {"X-Auth-Token": ctx.auth_token}
    else:
        headers = dict()
    headers['Content-Type'] = 'application/json'

    host, port = _get_keystone_host_and_port()
    conn = httplib.HTTPConnection(host, port, timeout=10)

    try:
        if data is None:
            conn.request(method, url, headers=headers)
        else:
            conn.request(method, url, headers=headers, body=json.dumps(data))
        response = conn.getresponse()
    except Exception:
        LOG.exception("Access Keystone failed")
        raise KeystoneError()

    return {"status": response.status,
            "text": response.read().strip(),
            "token": response.getheader("X-Subject-Token")}


def populate_auth_token(ctx):
    url = "/v3/auth/tokens"
    data = {
        "auth": {
             "identity": {
                  "methods": ["password"],
                  "password": {
                      "user": {
                          "name": ctx.username,
                          "domain": {
                              "name": ctx.domain_name
                          },
                          "password": ctx.password
                      }
                  }
             },
             "scope": {
                 "project": {
                     "name": ctx.tenant_name,
                     "domain": {
                         "name": ctx.domain_name
                     }
                 }
             }
        }
    }

    r = request(ctx, constants.HTTP_METHOD_POST, url, data=data)

    if r["status"] != 201:
        LOG.error("Get Keystone auth token failed")
        LOG.error("Keystone response: %(text)s" % r)
        raise KeystoneAuthError()

    ctx.auth_token = r["token"]
    resp_data = jsonutils.loads(r["text"])
    ctx.service_catalog = resp_data["token"]["catalog"]


def populate_tenant_id(ctx):
    # Note: Use service tenant id and admin role
    # operate Cinder volume snapshot and Nova instance
    # snapshot within other tenants.
    url = "/v3/projects?name={name}".format(name=ctx.tenant_name)
    r = request(ctx, constants.HTTP_METHOD_GET, url)
    if r["status"] != 200:
        LOG.error('Get tenant id of tenant "{tenant_name}" failed'
                  .format(tenant_name=ctx.tenant_name))
        LOG.error('Keystone response: %(text)s' % r)
        raise KeystoneAuthError()

    data = json.loads(r["text"])
    for project in data["projects"]:
        if project["name"] == ctx.tenant_name:
            ctx.tenant_id = project["id"]
            return

    LOG.error('Tenant id of tenant "{tenant_name}" not found'
              .format(tenant_name=ctx.tenant_name))
    raise KeystoneAuthError()


def generate_context(request_id=None, with_db_session=True):
    ctx = context.Context(
        domain_name=CONF.keystone_authtoken.project_domain_name,
        tenant_name=CONF.keystone_authtoken.project_name,
        username=CONF.keystone_authtoken.username,
        password=CONF.keystone_authtoken.password,
        is_admin=True,
        with_db_session=with_db_session,
        request_id=request_id)

    populate_auth_token(ctx)

    return ctx


def endpoint_list(ctx):
    url = "/v3/endpoints"
    r = request(ctx, constants.HTTP_METHOD_GET, url)
    if r["status"] != 200:
        LOG.error("Endpoint list failed")
        LOG.error("Keystone response: %(text)s" % r)
        raise KeystoneError("Endpoint list failed")
    data = json.loads(r["text"])
    return data["endpoints"]


def endpoint_get_by_service(ctx, service_id, interface="internal",
                            region=None):
    region = region or CONF.region
    endpoints = endpoint_list(ctx)
    found = 0
    result = None
    for endpoint in endpoints:
        if (endpoint["service_id"] == service_id
                and endpoint["interface"] == interface
                and endpoint["region"] == region):
            found += 1
            result = endpoint
    if found == 0:
        raise exceptions.EndpointNotFound2(service_id, interface, region)
    elif found == 1:
        return result
    else:
        raise exceptions.MultipleEndpointFound(service_id, interface, region)


def service_list(ctx):
    url = "/v3/services"
    r = request(ctx, constants.HTTP_METHOD_GET, url)
    if r["status"] != 200:
        LOG.error("Service list failed")
        LOG.error("Keystone response: %(text)s" % r)
        raise KeystoneError("Service list failed")
    data = json.loads(r["text"])
    return data["services"]


def service_get_by_name(ctx, service_name):
    services = service_list(ctx)
    found = 0
    result = None
    for service in services:
        if service["name"] == service_name:
            found += 1
            result = service
    if found == 0:
        raise exceptions.ServiceNotFound(service_name)
    elif found == 1:
        return result
    else:
        raise exceptions.MultipleServiceFound(service_name)


def project_list(ctx):
    url = "/v3/projects"
    r = request(ctx, constants.HTTP_METHOD_GET, url)
    if r["status"] != 200:
        LOG.error("Project list failed")
        LOG.error("Keystone response: %(text)s" % r)
        raise KeystoneError("Project list failed")
    data = json.loads(r["text"])
    return data["projects"]


def get_project_name(ctx, project_id):
    projects = project_list(ctx)
    found = 0
    result = None
    for project in projects:
        if project["id"] == project_id:
            found += 1
            result = project["name"]
    if found == 0:
        raise exceptions.ProjectNotFound(project_id)
    elif found == 1:
        return result
    else:
        raise exceptions.ProjectNotFound(project_id)


def region_statistics_update(ctx, region_id, data):
    url = "/v3/regions/" + region_id
    r = request(ctx, constants.HTTP_METHOD_PATCH, url, data=data)
    if r["status"] != 200:
        LOG.error('Update region "%s" information failed' % region_id)
        LOG.error('Keystone response: %(text)s' % r)
        raise KeystoneError()
