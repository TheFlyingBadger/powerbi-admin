

from pathlib import Path
from datetime import datetime
import json

from azure.identity import UsernamePasswordCredential, ClientSecretCredential
from requests.models import HTTPError

from urllib.parse import (
    urlencode, unquote, urlparse, parse_qsl, ParseResult
)


def add_url_params(url, params):
    """ Add GET params to provided URL being aware of existing.

    :param url: string of target URL
    :param params: dict containing requested params to be added
    :return: string with updated URL

    >> url = 'http://stackoverflow.com/test?answers=true'
    >> new_params = {'answers': False, 'data': ['some','values']}
    >> add_url_params(url, new_params)
    'http://stackoverflow.com/test?data=some&data=values&answers=false'



    Because this is for the PowerBI REST API all parameters begin with $
      (which of course python isn't happy with as a kwarg) so we'll add
      that onto each one

    """

    tweakedParams = {}
    for p in params:
        tweakedParams[f'~{p}'] = params[p]

    # Unquoting URL first so we don't loose existing args
    url = unquote(url)
    # Extracting url info
    parsed_url = urlparse(url)
    # Extracting URL arguments from parsed URL
    get_args = parsed_url.query
    # Converting URL arguments to dict
    parsed_get_args = dict(parse_qsl(get_args))
    # Merging URL arguments dict with new params
    parsed_get_args.update(tweakedParams)

    # Bool and Dict values should be converted to json-friendly values
    # you may throw this part away if you don't like it :)
    parsed_get_args.update(
        {k: json.dumps(v) for k, v in parsed_get_args.items()
         if isinstance(v, (bool, dict))}
    )

    # Converting URL argument to proper query string
    filterString = parsed_get_args.pop('~filter', None)
    encoded_get_args = urlencode(parsed_get_args, doseq=True)
    if filterString:
        encoded_get_args += f'~filter={filterString}'
    # Creating new parsed result object based on provided with new
    # URL arguments. Same thing happens inside of urlparse.
    new_url = ParseResult(
        parsed_url.scheme, parsed_url.netloc, parsed_url.path,
        parsed_url.params, encoded_get_args, parsed_url.fragment
    ).geturl()

    if tweakedParams:
        for char in ["?", "&"]:
            new_url = new_url.replace(f"{char}~", f"{char}$")
    # print(f'URL={new_url}')

    return new_url


def obj_as_dict(theObj):
    asDict = theObj.__dict__
    d = {}
    for k in (k for k in asDict if not k[0] == "_"):
        val = asDict[k]
        if type(val) == Path:
            val = str(val)
        elif type(val) == datetime:
            val = val.strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(val, int | str | dict | list):
            d[k] = val
    return d


def obj_as_json(theObj: object, indent: int = 2):
    return json.dumps(obj_as_dict(theObj=theObj), indent=indent)


class apiResult (object):

    def __repr__(self):
        return f"apiResult(apiURL = \'{self.api_url}\',headers = powerbiREST(\'{str(self.configREST)}\').getHeaders(), restConfigFile = \'{self.configREST}\')"

    def __str__(self):
        return str(self.as_dict())

    def as_json(self, indent: int = 2):
        return obj_as_json(self, indent=indent)

    def as_dict(self):
        return obj_as_dict(theObj=self)

    def __init__(self, apiURL: str, headers: dict, restConfigFile: Path | str):

        print('IN INIT')
        self.configREST = str(restConfigFile)
        self._apiURL = apiURL
        try:
            import requests
            with requests.get(url=self._apiURL, headers=headers) as req:
                if req.status_code != 200:
                    raise HTTPError(req.status_code, req.reason, apiURL)
                self._status_code = req.status_code
                self._reason = req.reason
                theContent = json.loads(req.content)
        finally:
            try:
                req.close()
            except:
                ...

        for attr in theContent.keys():
            attrName = attr.replace('@', '').replace('.', '_')
            setattr(self, attrName, theContent[attr])
            # theContent.pop(attr, None)

        try:
            if not self.value:
                self.value_count = 0
            elif isinstance(self.value, list):
                self.value_count = len(self.value)
            elif isinstance(self.value, dict | object):
                self.value_count = 1
            else:
                self.value_count = -1
        except AttributeError:
            ...

    @ property
    def api_url(self):
        return self._apiURL

    @ property
    def status_code(self):
        return self._status_code

    @ property
    def reason(self):
        return self._reason

    @ property
    def value_json(self, indent: int = 2):
        val = getattr(self, 'value', None)
        if val:
            return json.dumps(val, indent=indent)
        else:
            return json.dumps(self.as_dict(), indent=indent)


class powerbiREST (object):
    def __repr__(self):
        return f"powerbiREST(\'{str(self.yaml_file)}\')"

    def as_json(self, indent: int = 2):
        return obj_as_json(self, indent=indent)

    def as_dict(self):
        return obj_as_dict(theObj=self)

    def __str__(self):
        return str(self.as_dict())

    def __init__(self, configYAML: str | Path):
        from configFileHelper import Config

        if isinstance(configYAML, str):
            configYAML = Path(configYAML)
        configYAML = configYAML.resolve()
        config = Config(file_path=configYAML)

        self._yaml = configYAML
        self._debug = config.get_bool("APP/DEBUG")

        self.auth_type = config.get('AZURE/AUTH_TYPE').lower()
        auth_types = ['usernamepassword', 'clientsecret']
        if self.auth_type not in auth_types:
            raise AttributeError(
                f"AUTH_TYPE should be in {''.join(auth_types)}")
        self.tenant_id = config.get('AZURE/TENANT_ID')
        self.client_id = config.get('AZURE/CLIENT_ID')
        self.scope = config.get('AZURE/SCOPE')
        if isinstance(self.scope, list):
            self.scope = ','.join(self.scope)

        def getSecret(theDict: dict, secretType: str):
            try:
                fileKey = f'{secretType}_FILE'
                secretFile = Path(theDict[fileKey])
                if not secretFile:
                    raise KeyError

                if not secretFile.is_file():
                    raise FileNotFoundError(secretFile)
                _secret = secretFile.read_text()
            except KeyError:
                _secret = theDict[secretType]
            if not _secret:
                raise KeyError(f'AZURE/{secretType}')
            return _secret

        if self.auth_type == 'usernamepassword':
            azureCredential = UsernamePasswordCredential(
                client_id=self.client_id, username=config.get('AZURE/USERNAME'), password=getSecret(config.get('AZURE'), 'PASSWORD'), tenant_id=self.tenant_id)
        elif self.auth_type == 'clientsecret':
            azureCredential = ClientSecretCredential(
                client_id=self.client_id, client_secret=getSecret(config.get('AZURE'), 'CLIENT_SECRET'), tenant_id=self.tenant_id)
        if not isinstance(azureCredential,  UsernamePasswordCredential | ClientSecretCredential):
            raise TypeError(
                f"azureCredential should be ( UsernamePasswordCredential or ClientSecretCredential), not \'{type(azureCredential)}\'")
        _AccessToken = azureCredential.get_token(
            self.scope, tenant_id=self.tenant_id)
        self.access_token = _AccessToken.token
        self.token_expires_on = datetime.fromtimestamp(
            _AccessToken.expires_on)
        try:
            self._isAdmin = True
            _ = self.getWorkspaces(asAdmin=self._isAdmin, limit=1)
        except HTTPError:
            self._isAdmin = False
        print(self._isAdmin)

    def getHeaders(self):
        return {'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.access_token}'
                }

    def getContent(self, apiREST: str):
        print(apiREST)
        return apiResult(apiURL=apiREST, headers=self.getHeaders(), restConfigFile=self.yaml_file)

    @ property
    def debug(self):
        return self._debug

    @ property
    def yaml_file(self):
        return self._yaml

    @ property
    def is_admin(self):
        return self._isAdmin

    @ property
    def subscription_id(self):
        return self.tenant_id

    def baseURL(self, asAdmin: bool = False):
        if asAdmin and not self.is_admin:
            raise PermissionError(
                'cannot run as admin, not authenticated as an admin')
        return f"https://api.powerbi.com/v1.0/myorg{'/admin' if asAdmin else ''}"

    def getWorkspaces(self, asAdmin: bool = False, **kwargs):
        return self.getContent(add_url_params(f'{self.baseURL(asAdmin)}/groups', kwargs))

    def getWorkspace(self, workspace_id: str, asAdmin: bool = False):
        raise NotImplementedError
        # return self.getContent(f'{self.baseURL(asAdmin)}groups/{workspace_id}')

    def getWorkspaceDatasets(self, workspace_id: str, asAdmin: bool = False, **kwargs):
        return self.getWorkspaceThingies(workspace_id=workspace_id, thingyType='datasets', asAdmin=asAdmin, **kwargs)

    def getWorkspaceDataflows(self, workspace_id: str, asAdmin: bool = False, **kwargs):
        return self.getWorkspaceThingies(workspace_id=workspace_id, thingyType='dataflows', asAdmin=asAdmin, **kwargs)

    def getDataflow(self, workspace_id: str, dataflow_id: str, asAdmin: bool = False, **kwargs):
        return self.getWorkspaceThingy(workspace_id=workspace_id, thingyType='dataflows', thingyId=dataflow_id, asAdmin=asAdmin, **kwargs)

    def getDataset(self, dataset_id: str):
        return self.getThingy(thingyType='datasets', thingyId=dataset_id)

    def getWorkspaceThingies(self, workspace_id: str, thingyType: str, asAdmin: bool = False, **kwargs):
        return self.getWorkspaceThingy(workspace_id=workspace_id, thingyType=thingyType, thingyId=None, asAdmin=asAdmin, **kwargs)

    def getWorkspaceThingy(self, workspace_id: str, thingyType: str, thingyId: str = None, asAdmin: bool = False, **kwargs):
        url = f'{self.baseURL(asAdmin)}/groups/{workspace_id}/{thingyType}'
        if thingyId:
            url += f"/{thingyId}"
        if kwargs and len(kwargs.keys()) > 0:
            url = add_url_params(url, **kwargs)
        return self.getContent(url)

    def getThingy(self, thingyType: str, thingyId: str = None, asAdmin: bool = False, **kwargs):
        url = f'{self.baseURL(asAdmin)}/{thingyType}'
        if thingyId:
            url += f'/{thingyId}'
        if kwargs and len(kwargs.keys()) > 0:
            url = add_url_params(url, **kwargs)
        return self.getContent(url)
