import json
import urlparse
from eventlet.green import httplib
from oslo_log import log
from oslo_config import cfg

from hostha import constants
from hostha import exceptions
import six


CONF = cfg.CONF
LOG = log.getLogger(__name__)


class NovaError(exceptions.CloudultraError):
    code = "NOVA_ERROR"
    message = "Error when access OpenStack Nova"


class InstanceSnapshotError(exceptions.CloudultraError):
    code = "INSTANCE_SNAPSHOT_ERROR"
    message = "Failed to access or operate instance snapshots"


def request(ctx, method, path, data=None, api_version=None):
    headers = {"X-Auth-Token": ctx.auth_token,
               'Content-Type': 'application/json'}
    if api_version:
        LOG.debug("api version %s", api_version)
        headers["X-OpenStack-Nova-API-Version"] = api_version
    endpoint = ctx.get_endpoint_this_region('compute')
    u = urlparse.urlparse(endpoint)
    url = u.path + path

    conn = httplib.HTTPConnection(u.netloc, timeout=10)
    try:
        if data is None:
            conn.request(method, url, headers=headers)
        else:
            conn.request(method, url, headers=headers, body=json.dumps(data))
        response = conn.getresponse()

        return {"status": response.status,
                "text": response.read().strip()}

    except Exception:
        LOG.exception("Access Nova service failed")
        raise InstanceSnapshotError()
    finally:
        conn.close()


def instance_snapshot_list(ctx, instance_id):
    url = ("/os-live_snapshot_instance"
           "?instance_id={instance_id}"
           "&snapshot_build_type=automatic"
           .format(instance_id=instance_id))
    r = request(ctx, constants.HTTP_METHOD_GET, url)
    if r["status"] != 200:
        LOG.error('Get snapshots of instance "{instance_id}" failed'
                  .format(instance_id=instance_id))
        LOG.error('Nova response: %(text)s' % r)
        raise InstanceSnapshotError()
    data = json.loads(r["text"])
    return data["snapshot_list"]


def instance_snapshot_create(ctx, instance_id, name,
                             specify_volume=False, system_volume=True,
                             data_volumes=None):
    url = "/os-live_snapshot_instance"
    data = {
        "live_snapshot": {
            "instance_id": instance_id,
            "display_name": name,
            "snapshot_build_type": "automatic"
        }
    }

    if specify_volume:
        data['live_snapshot']['system_snapshot'] = system_volume
        data['live_snapshot']['volume_snapshot_list'] = data_volumes

    r = request(ctx, constants.HTTP_METHOD_POST, url, data=data)
    if r["status"] != 200:
        LOG.error('Create snapshot of instance "{instance_id}" failed'
                  .format(instance_id=instance_id))
        LOG.error("Nova response: %(text)s" % r)
        raise InstanceSnapshotError()
    else:
        LOG.info('Create snapshot of instance "%s" succeeded' % instance_id)


def instance_snapshot_delete(ctx, snapshot_id):
    url = "/os-live_snapshot_instance/" + snapshot_id
    r = request(ctx, constants.HTTP_METHOD_DELETE, url)
    if r["status"] != 200:
        LOG.error('Delete instance snapshot "%s" failed' % snapshot_id)
        LOG.error("Nova response: %(text)s" % r)
        raise InstanceSnapshotError
    else:
        LOG.info('Delete instance snapshot "%s" succeeded'
                 % snapshot_id)


def hypervisor_stats_get(ctx):
    path = '/os-hypervisors/statistics'
    r = request(ctx, constants.HTTP_METHOD_GET, path)
    if r['status'] != 200:
        LOG.error("Get OpenStack Nova hypervisor statistics failed")
        LOG.error("Nova response: %(text)s" % r)
        raise NovaError()
    result = json.loads(r["text"])['hypervisor_statistics']
    data = {
        'memory': {
            'total': result['memory_mb'],
            'used': result['memory_mb_used']
        },
        'vcpus': {
            'total': result['vcpus'],
            'used': result['vcpus_used']
        }
    }
    return data


def hypervisor_list(ctx):
    path = '/os-hypervisors/detail'
    r = request(ctx, constants.HTTP_METHOD_GET, path)
    if r['status'] != 200:
        LOG.error('Get Nova hypervisor detail list failed')
        LOG.error('Nova response: %(text)s' % r)
        raise NovaError()
    hypervisors = json.loads(r['text'])['hypervisors']
    return hypervisors


def host_list(ctx):
    path = '/os-hosts'
    r = request(ctx, constants.HTTP_METHOD_GET, path)
    if r['status'] != 200:
        LOG.error('Get Nova host list failed')
        LOG.error('Nova response: %(text)s' % r)
        raise NovaError()
    hosts = json.loads(r['text'])['hosts']
    return hosts


def service_force_down(ctx, host, binary, forced_down):
    # forced_down is New in version 2.11
    path = '/os-services/force-down'
    data = {"host": host,
            "binary": binary,
            "forced_down": forced_down}
    r = request(ctx, constants.HTTP_METHOD_PUT, path, data,
                api_version='2.11')
    if r['status'] != 200:
        LOG.error("Force Set Nova Service state Error")
        LOG.error('Nova response: %(text)s' % r)
        raise NovaError()
    else:
        LOG.debug("Success Set %s %s service %s", host,
                  binary, str(forced_down))


def disable_compute_service(ctx, host):
    path = '/os-services/disable'
    data = {"host": host,
            "binary": "nova-compute"}
    r = request(ctx, constants.HTTP_METHOD_PUT, path, data,
                api_version='2.11')
    if r['status'] != 200:
        LOG.error("Disable %s nova-compute service error: %s", host, str(r))
        raise NovaError()
    else:
        LOG.debug("Success disable %s nova-compute service", host)


def hypervisor_servers(ctx, hostname):
    path = '/os-hypervisors/%s/servers' % hostname
    r = request(ctx, constants.HTTP_METHOD_GET, path)
    if r['status'] != 200:
        LOG.error("Get hypervisors servers Error")
        LOG.error('Nova response: %(text)s' % r)
        raise NovaError()
    hypervisor = json.loads(r['text'])['hypervisors'][0]
    LOG.debug("Success get %s hypervisor service %s", hostname,
              str(hypervisor))
    return hypervisor


def get_services_list(ctx):
    path = '/os-services'
    r = request(ctx, constants.HTTP_METHOD_GET, path,
                api_version='2.11')
    if r['status'] != 200:
        LOG.error("Get service list Error")
        LOG.error('Nova response: %(text)s' % r)
        raise NovaError()
    services = json.loads(r['text'])['services']
    LOG.debug("Success get nova service list %s",
              str(services))
    return services


def server_evacuate(ctx, uuid, target_host):
    path = '/servers/%s/action' % uuid
    data = {"evacuate": {}}
    if target_host:
        data["evacuate"]["host"] = target_host
    # Starting since version 2.14, Nova automatically
    # detects whether the server is on shared storage or not
    r = request(ctx, constants.HTTP_METHOD_POST, path, data,
                api_version='2.14')
    if r['status'] != 200:
        LOG.error("Server Evacuate Error")
        LOG.error('Nova response: %(text)s' % r)
        raise NovaError(six.text_type(r))
    else:
        LOG.debug("Success trigger %s vm evacuate ", uuid)


def server_migrate(ctx, uuid):
    path = '/servers/%s/action' % uuid
    data = {"migrate": {}}
    r = request(ctx, constants.HTTP_METHOD_POST, path, data,
                api_version='2.14')
    if r['status'] != 202:
        LOG.error("VM %s migrate error: %s", uuid, str(r))
        raise NovaError()
    else:
        LOG.debug("Success trigger VM %s migrate ", uuid)


def server_migrate_live(ctx, uuid, target_host=None):
    path = '/servers/%s/action' % uuid
    data = {"os-migrateLive": {"block_migration": "auto",
                               "host": None}}
    if target_host:
        data["os-migrateLive"]["host"] = target_host
    r = request(ctx, constants.HTTP_METHOD_POST, path, data,
                api_version='2.25')
    if r['status'] != 202:
        LOG.error("VM %s live-migrate error: %s", uuid, str(r))
        raise NovaError()
    else:
        LOG.debug("Success trigger VM %s live-migrate ", uuid)


def server_details(ctx, uuid):
    path = '/servers/%s' % uuid
    r = request(ctx, constants.HTTP_METHOD_GET, path)
    if r['status'] != 200:
        LOG.error("Server Details Error")
        LOG.error("Nova response: %(text)s" % r)
        raise NovaError()
    else:
        LOG.debug("Success show %s vm details", uuid)
    server = json.loads(r['text'])['server']
    return server


def servers_list(ctx, limit=None, marker=None, host=None):
    # just get servers name & uuid
    path = '/servers?all_tenants=1'
    if host:
        path = path + '&host=%s' % host
    if limit:
        path = path + '&limit=' + str(limit)
    if marker:
        path = path + '&marker=' + str(marker)
    r = request(ctx, constants.HTTP_METHOD_GET, path,
                api_version='2.25')
    if r['status'] != 200:
        LOG.error("Servers List Error")
        LOG.error("Nova response: %(text)s" % r)
        raise NovaError()
    else:
        LOG.debug("Success get servers list")
    servers = json.loads(r['text'])['servers']
    return servers


def servers_list_all(ctx, host=None):
    servers_all = []
    remaining_tag = True
    limit = 1000
    marker = None
    while remaining_tag:
        servers = servers_list(ctx, limit=limit, marker=marker, host=host)
        servers_all.extend(servers)
        if len(servers) == limit:
            marker = servers[-1]['id']
        elif len(servers) < limit:
            remaining_tag = False
    return servers_all


def get_instance_actions(ctx, uuid):
    path = '/servers/%s/os-instance-actions' % uuid
    r = request(ctx, constants.HTTP_METHOD_GET, path)
    if r['status'] != 200:
        LOG.error("Get Instance Actions Error")
        LOG.error("Nova response: %(text)s" % r)
        raise NovaError()
    else:
        LOG.debug("Success get %s instance actions", uuid)
    instance_actions = json.loads(r['text'])["instanceActions"]
    return instance_actions


def instance_action(ctx, uuid, data):
    path = '/servers/%s/action' % uuid
    r = request(ctx, constants.HTTP_METHOD_POST, path,
                data)
    if r['status'] != 202:
        LOG.error("Trigger Instance %s Action %s Error",
                  uuid, data)
        LOG.error("Nova response: %(text)s" % r)
        raise NovaError(six.text_type(r))
    else:
        LOG.debug("Success exec %s instance action %s ",
                  uuid, data)


def instance_create(ctx, instance):
    path = '/servers'
    data = {"server": {
                "name": instance.get("name"),
                "imageRef": instance.get("image"),
                "flavorRef": instance.get("flavor"),
                "networks": instance.get("network"),
                }
            }

    r = request(ctx, constants.HTTP_METHOD_POST, path,
                data)
    if r['status'] != 202:
        LOG.error("Fail create instance %s ", instance.get("name"))
        LOG.error("Nova response: %(text)s" % r)
        raise NovaError(six.text_type(r))
    else:
        LOG.debug("Success create instance %s ", instance.get("name"))
        return json.loads(r['text'])["server"]


def instance_get(ctx, instance_id):
    path = '/servers/detail'
    r = request(ctx, constants.HTTP_METHOD_GET, path)
    if r['status'] != 200:
        LOG.error("Insrance Get Details Error")
        LOG.error("Nova response: %(text)s" % r)
        raise NovaError()
    else:
        LOG.debug("Success get instance %s details", instance_id)
    all_instances = json.loads(r['text'])["servers"]
    for instance in all_instances:
        if instance["id"] == instance_id:
            return instance
    raise NovaError()


def instance_delete(ctx, instance_id):
    path = '/servers/%s' % instance_id
    r = request(ctx, constants.HTTP_METHOD_DELETE, path)
    if r["status"] != 204:
        LOG.error('Delete instance %s failed' % instance_id)
        LOG.error("Nova response: %(text)s" % r)
        raise InstanceSnapshotError
    else:
        LOG.info('Delete instance %s succeeded' % instance_id)


def instance_stop(ctx, instance_id):
    path = '/servers/%s/action' % instance_id
    data = {"os-stop": None}
    r = request(ctx, constants.HTTP_METHOD_POST, path, data)
    if r["status"] != 202:
        LOG.error('Stop instance %s failed' % instance_id)
        LOG.error("Nova response: %(text)s" % r)
        raise InstanceSnapshotError
    else:
        LOG.info('Stop instance %s succeeded' % instance_id)


def flavor_list(ctx):
    path = '/flavors'
    r = request(ctx, constants.HTTP_METHOD_GET, path)
    if r['status'] != 200:
        LOG.error("Get All Flavors Error")
        LOG.error("Nova response: %(text)s" % r)
        raise NovaError()
    else:
        LOG.debug("Success get all flavors")
    flavor = json.loads(r['text'])["flavors"]
    return flavor


def flavor_get(ctx, flavor_id):
    path = '/flavors/%s' % flavor_id
    r = request(ctx, constants.HTTP_METHOD_GET, path)
    if r['status'] != 200:
        LOG.error("Flavors Get Details Error")
        LOG.error("Nova response: %(text)s" % r)
        raise NovaError()
    else:
        LOG.debug("Success get flavor %s details", flavor_id)
    flavor = json.loads(r['text'])["flavor"]
    return flavor
