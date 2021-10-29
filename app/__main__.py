from functions import *
from version import getVersion
import requests


if __name__ == '__main__':
    CONFIG = getConfig(Path('__file__').parent.parent.joinpath('config.yaml'))
    # ic(getVersion())
    # ic(CONFIG.client_secret_credential.__dict__)
    # ic(CONFIG.access_token.expires_on)
    # ic(CONFIG.access_token.token)
    # ic(CONFIG.session)
    ic(CONFIG.client.__dict__.keys())
    # ic(CONFIG.client.__dict__['config'].__dict__)
    # ic(CONFIG.client.__dict__.keys())
    # ic(CONFIG.client._deserialize())

    https: // api.powerbi.com/v1.0/myorg/admin/groups?$top = {$top}
    # ops = CONFIG.client.get_available_operations()
    # ic(ops.__dict__)
