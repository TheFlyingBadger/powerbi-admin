from powerbiREST import powerbiREST
from pathlib import Path
from version import getVersion
import json
# from pathlib import Path
from datetime import datetime
# from time import strftime

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

if __name__ == '__main__':
    CONNECTION = powerbiREST(
        Path('__file__').parent.parent.joinpath('config.yaml'))

    ic(getVersion())

    ic(CONNECTION.is_admin)
    # content = CONNECTION.getWorkspaces(top=10, skip=70)

    # ic(content.odata_context, content.odata_count, content.value_count)
    # # ic(str(content))

    workspaceId = '2743379b-ecc4-4445-87c4-5c672aac2764'  # Power BI Common
    workspaceId = '3caa0e14-c866-45fc-9557-54b4a59d8a91'  # Test Premium

    # content = CONNECTION.getWorkspaceDatasets(
    #     workspace_id=workspaceId
    # )
    # # `ic(content.odata_context, content.odata_count, content.value_count)
    # # ic(content.api_url, content.status_code, content.reason)`
    # print(content.as_json())

    # content = CONNECTION.getDataset(dataset_id=content.value[0]['id']
    #                                 )
    # ic(content.api_url, content.status_code, content.reason)
    # print(content.value_json)

    content = CONNECTION.getWorkspaceDataflows(
        workspace_id=workspaceId
    )
    print(content.value_json)
    content = CONNECTION.getDataflow(
        workspace_id=workspaceId, dataflow_id='1f2bad6b-2a0e-4ef9-9fd4-220955be0416')
    # print(content.api_url)
    Path(f'./{content.name}.json').write_text(content.as_json(indent=None))
    # print(json.dumps(content.value, indent=2))
