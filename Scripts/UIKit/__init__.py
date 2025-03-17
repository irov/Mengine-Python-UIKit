def onInitialize():
    from Foundation.Notificator import Notificator
    identities = [
        "onPopUpShow",
        "onPopUpShowEnd",
        "onPopUpHide",
        "onPopUpHideEnd",
    ]
    Notificator.addIdentities(identities)

    from TraceManager import TraceManager
    traces = [
        # "PopUp",
    ]
    TraceManager.addTraces(traces)

    from Foundation.EntityManager import EntityManager
    from Foundation.ObjectManager import ObjectManager
    types = [
        {"name": "PopUp", "override": True}
    ]
    if EntityManager.importEntities("UIKit.Entities", types) is False:
        return False
    if ObjectManager.importObjects("UIKit.Objects", types) is False:
        return False

    return True


def onFinalize():
    pass
