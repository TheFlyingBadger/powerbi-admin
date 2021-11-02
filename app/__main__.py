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
    # ic(CONFIG.__dict__.keys())
    # ic(CONFIG.client.__dict__['config'].__dict__)
    # ic(CONFIG.client.__dict__.keys())
    # ic(CONFIG.client._deserialize())

    # ic(type(CONFIG.client_secret_credential))
    # ic(CONFIG.client_secret_credential)
    # ic(CONFIG.client_secret_credential.__dict__)
#     token = CONFIG.client_secret_credential.get_token(
#         ["https://analysis.windows.net/powerbi/api/.default"])
#     ic(type(token))
#     ic(token)
#     ic(str(token))
#     ic(token.__dict__)
#     ic(token.__dir__())
#     raise Exception
# # --------------------------------------------------
# Check if a token was obtained, grab it and call the
# Power BI REST API, otherwise throw up the error message
# --------------------------------------------------
    # access_token = result['access_token']
    url_groups = 'https://api.powerbi.com/v1.0/myorg/groups'
    url_groups = 'https://api.powerbi.com/v1.0/myorg/capacities'

    header = {'Content-Type': 'application/json',
              'Authorization': f'Bearer {CONFIG.access_token}',
              'Host': 'api.powerbi.com'
              }
    api_out = requests.get(url=url_groups, headers=header)
    ic(type(api_out))
    ic(api_out)
    ic(api_out.__dict__)
    # print(api_out.json())
    # # ops = CONFIG.client.get_available_operations()
    # ic(ops.__dict__)
