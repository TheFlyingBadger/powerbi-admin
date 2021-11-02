

from pathlib import Path
from datetime import datetime
from time import strftime

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

    def __repr__(self):
        return f"azureClientSecretConnection(\'{self.yaml_file}\')"

    def as_json(self, indent: int = 2):
        import json
        d = self.as_dict()
        print(d)
        return json.dumps(d, indent=indent)

    def as_dict(self):
        asDict = self.__dict__
        d = {}
        for k in (k for k in asDict if not k[0] == "_"):
            val = asDict[k]
            ic(k, type(val))
            if type(val) == Path:
                val = str(val)
            elif type(val) == datetime:
                val = val.strftime('%Y-%m-%d %H:%M:%S')
            if isinstance(val, int | str | dict | list):
                d[k] = val
        return d

    def __str__(self):
        return str(self.as_dict())

    def __init__(self, configYAML: str | Path):
        from configFileHelper import Config
        if isinstance(configYAML, str):
            configYAML = Path(configYAML).resolve()
        config = Config(file_path=configYAML)

        self._yaml = configYAML
        self._debug = config.get_bool("APP/DEBUG")

        from azure.identity import ClientSecretCredential

        self.tenant_id = config.get('AZURE/TENANT_ID')
        self.client_id = config.get('AZURE/CLIENT_ID')
        self.scope = config.get('AZURE/SCOPE')
        print(type(self.scope))
        if isinstance(self.scope, list):
            self.scope = ','.join(self.scope)
            print(type(self.scope))
        print(self.scope)

        try:
            clientSecretFile = Path(config.get('AZURE/CLIENT_SECRET_FILE'))
            if not clientSecretFile:
                raise KeyError

            if not clientSecretFile.is_file():
                raise FileNotFoundError

            self._client_secret = clientSecretFile.read_text()

        except KeyError:
            self._client_secret = config.get('AZURE/CLIENT_SECRET')

        self._ClientSecretCredential = ClientSecretCredential(
            tenant_id=self.tenant_id, client_id=self.client_id, client_secret=self._client_secret)
        self._AccessToken = self._ClientSecretCredential.get_token(
            self.scope, tenant_id=self.tenant_id)
        self.access_token = self._AccessToken.token
        self.token_expires_on = datetime.fromtimestamp(
            self._AccessToken.expires_on)

        # Temp
        self.client_secret = self._client_secret

    @ property
    def debug(self):
        return self._debug

    @ property
    def yaml_file(self):
        return self._yaml

    @ property
    def subscription_id(self):
        return self.tenant_id


def getConfig(configFile: str = "config.yaml"):

    config = azureClientSecretConnection(configYAML=configFile)
    return config
