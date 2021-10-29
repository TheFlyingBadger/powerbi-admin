

from pathlib import Path
from datetime import datetime

try:
    from icecream import ic

    def ic_set(debug):
        if debug:
            ic.enable()
        else:
            ic.disable()


except ImportError:  # Graceful fallback if IceCream isn't installed.
    doDebug: bool = False

    def ic(thing):  # just print to STDOUT
        if doDebug:
            print(thing)

    def ic_set(debug):
        global doDebug
        doDebug = debug
        ic("* icecream module not imported successfully, using STDOUT")


def nowString():
    return f"{datetime.now().strftime('%Y.%m.%d %T')} |> "


try:
    ic.configureOutput(prefix=nowString)
except AttributeError:
    pass


class azureClientSecretConnection (object):
    def __init__(self, configYAML: str | Path):
        from configFileHelper import Config
        if isinstance(configYAML, str):
            configYAML = Path(configYAML).resolve()
        config = Config(file_path=configYAML)

        self._debug = config.get_bool("APP/DEBUG")

        from azure.identity import ClientSecretCredential

        self._tenant_id = config.get('AZURE/TENANT_ID')
        client_id = config.get('AZURE/CLIENT_ID')
        scope = config.get('AZURE/SCOPE')

        try:
            clientSecretFile = Path(config.get('AZURE/CLIENT_SECRET_FILE'))
            if not clientSecretFile:
                raise KeyError

            if not clientSecretFile.is_file():
                raise FileNotFoundError

            client_secret = clientSecretFile.read_text()

        except KeyError:
            client_secret = config.get('AZURE/CLIENT_SECRET')

        self.client_secret_credential = ClientSecretCredential(
            tenant_id=self._tenant_id, client_id=client_id, client_secret=client_secret)
        self.access_token = self.client_secret_credential.get_token(scope)

        from azure.mgmt.powerbiembedded.power_bi_embedded_management_client import PowerBIEmbeddedManagementClient

        self.client = PowerBIEmbeddedManagementClient(
            credentials=self.client_secret_credential, subscription_id=self.subscription_id, base_url=None)

    @property
    def debug(self):
        return self._debug

    @property
    def tenant_id(self):
        return self._tenant_id

    @property
    def subscription_id(self):
        return self._tenant_id


def getConfig(configFile: str = "config.yaml"):

    config = azureClientSecretConnection(configYAML=configFile)
    ic_set(config.debug)
    return config
