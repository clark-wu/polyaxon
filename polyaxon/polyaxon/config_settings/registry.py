import json

from rhea import RheaError
from rhea.manager import UriSpec

from polyaxon.config_manager import config

REGISTRY_USER = config.get_string('POLYAXON_REGISTRY_USER', is_optional=True)
REGISTRY_PASSWORD = config.get_string('POLYAXON_REGISTRY_PASSWORD', is_optional=True)
REGISTRY_HOST_NAME = config.get_string('POLYAXON_REGISTRY_HOST', is_optional=True)
REGISTRY_PORT = config.get_string('POLYAXON_REGISTRY_PORT', is_optional=True)
REGISTRY_NODE_PORT = config.get_string('POLYAXON_REGISTRY_NODE_PORT', is_optional=True)
REGISTRY_HOST = '{}:{}'.format('192.168.1.50', REGISTRY_NODE_PORT)
PRIVATE_REGISTRIES_PREFIX = 'POLYAXON_PRIVATE_REGISTRY_'


def get_external_registries():
    registries = []
    for key in config.keys_startswith(PRIVATE_REGISTRIES_PREFIX):

        try:
            registry_dict = config.get_dict(key, is_secret=True)
            registry_spec = UriSpec(**registry_dict)
        except RheaError:
            registry_spec = config.get_string(key, is_secret=True)
            try:
                # We might get this value from a chart with `toJson` applied.
                registry_spec = json.loads(registry_spec)
            except json.decoder.JSONDecodeError:
                pass

            registry_spec = config.parse_uri_spec(registry_spec)

        if registry_spec:
            registries.append(registry_spec)

    return registries


PRIVATE_REGISTRIES = get_external_registries()
