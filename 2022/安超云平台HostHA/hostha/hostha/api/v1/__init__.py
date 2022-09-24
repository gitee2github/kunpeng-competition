

from hostha.api.v1 import configuration
from hostha.api.v1 import host_ha
from hostha.api.v1 import host_evacuation
from hostha.api.v1 import vm_evacuation


def register_blueprints(app, url_prefix):
    app.register_blueprint(configuration.rest, url_prefix=url_prefix)
    app.register_blueprint(host_ha.rest, url_prefix=url_prefix)
    app.register_blueprint(host_evacuation.rest, url_prefix=url_prefix)
    app.register_blueprint(vm_evacuation.rest, url_prefix=url_prefix)
