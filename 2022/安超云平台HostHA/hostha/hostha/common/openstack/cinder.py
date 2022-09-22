import json
import urlparse
from eventlet.green import httplib
from oslo_log import log
from oslo_config import cfg

from hostha import constants
from hostha import exceptions


CONF = cfg.CONF
LOG = log.getLogger(__name__)


class CinderError(exceptions.CloudultraError):
    code = "CINDER_ERROR"
    message = "Error when access Cinder"


class VolumeSnapshotError(exceptions.CloudultraError):
    code = "VOLUME_SNAPSHOT_ERROR"
    message = "Failed to access or operate volume snapshots"


class VolumeNotFound(exceptions.CloudultraError):
    code = 'VOLUME_NOT_FOUND'

    def __init__(self, volume_id):
        message = 'Cinder volume "%s" not found' % volume_id
        super(VolumeNotFound, self).__init__(message)


def request(ctx, method, path, data=None):
    headers = {"X-Auth-Token": ctx.auth_token,
               'Content-Type': 'application/json'}

    endpoint = ctx.get_endpoint_this_region('volumev2')
    u = urlparse.urlparse(endpoint)
    url = u.path + path

    conn = httplib.HTTPConnection(u.netloc)
    try:
        if data is None:
            conn.request(method, url, headers=headers)
        else:
            conn.request(method, url, headers=headers, body=json.dumps(data))
        response = conn.getresponse()
    except Exception:
        LOG.exception("Access Cinder failed")
        raise VolumeSnapshotError()
    return {"status": response.status,
            "text": response.read().strip()}


def volume_get(ctx, volume_id):
    url = '/volumes/' + volume_id
    r = request(ctx, constants.HTTP_METHOD_GET, url)
    if r['status'] == 404:
        raise VolumeNotFound(volume_id)
    elif r['status'] != 200:
        LOG.error('Get volume "%s" failed' % volume_id)
        LOG.error('Cinder response: %(text)s' % r)
        raise CinderError()
    data = json.loads(r['text'])
    return data['volume']


def volume_snapshot_list(ctx, volume_id):
    url = ("/snapshots/detail"
           "?all_tenants=1"
           "&volume_id={volume_id}"
           "&is_scheduled=1"
           "&sort_key=created_at"
           "&sort_dir=asc"
           .format(volume_id=volume_id))
    r = request(ctx, constants.HTTP_METHOD_GET, url)
    if r["status"] != 200:
        LOG.error('Get snapshots of volume "{volume_id}" failed'
                  .format(volume_id=volume_id))
        LOG.error('Cinder response: %(text)s' % r)
        raise VolumeSnapshotError()

    data = json.loads(r["text"])
    return data["snapshots"]


def volume_snapshot_create(ctx, volume_id, name):
    url = "/snapshots"
    data = {
        "snapshot": {
            "name": name,
            "force": True,
            "volume_id": volume_id,
            "is_scheduled": True
        }
    }
    r = request(ctx, constants.HTTP_METHOD_POST, url, data=data)
    if r["status"] != 202:
        LOG.error('Create snapshot of volume "{volume_id}" failed'
                  .format(volume_id=volume_id))
        LOG.error('Cinder response: %(text)s' % r)
        raise VolumeSnapshotError()
    else:
        LOG.info('Create snapshot of volume "{volume_id}" succeeded'
                 .format(volume_id=volume_id))


def volume_snapshot_delete(ctx, snapshot_id):
    url = "/snapshots/" + snapshot_id
    r = request(ctx, constants.HTTP_METHOD_DELETE, url)
    if r["status"] != 202:
        LOG.error('Delete volume snapshot "{snapshot_id}" failed'
                  .format(snapshot_id=snapshot_id))
        LOG.error('Cinder response: %(text)s' % r)
        raise VolumeSnapshotError()
    else:
        LOG.info('Delete volume snapshot "{snapshot_id}" succeeded'
                 .format(snapshot_id=snapshot_id))


def pool_detail_get(ctx):
    url = "/scheduler-stats/get_pools?detail=True"
    r = request(ctx, constants.HTTP_METHOD_GET, url)
    if r["status"] != 200:
        LOG.error("Get OpenStack Cinder pool detail failed")
        LOG.error("Cinder response: %(text)s" % r)
        raise CinderError()
    return json.loads(r["text"])


def get_quota_usage(ctx, tenant_id):
    url = "/os-quota-sets/" + tenant_id + '?usage=True'
    r = request(ctx, constants.HTTP_METHOD_GET, url)
    if r["status"] != 200:
        LOG.error("Get OpenStack Cinder quota_usage failed")
        LOG.error("Cinder response: %(text)s" % r)
        raise CinderError()
    result = json.loads(r["text"])
    return result
