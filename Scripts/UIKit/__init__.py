def onInitialize():
    Trace.msg_dev("UIKit onInitialize")

    from Foundation.Notificator import Notificator
    identities = [
        "onPopUpShow",
        "onPopUpShowEnd",
        "onPopUpHide",
        "onPopUpHideEnd",
        "onPopUpShowDebugAd",
    ]
    Notificator.addIdentities(identities)

    from TraceManager import TraceManager
    traces = [
        # "PopUp",
    ]
    TraceManager.addTraces(traces)

    EntityTypes = [
        {"Type": "PopUp", "Override": True}
    ]

    from Foundation.Bootstrapper import Bootstrapper
    if Bootstrapper.loadEntities("UIKit", EntityTypes) is False:
        return False

    return True


def onFinalize():
    Trace.msg_dev("UIKit onFinalize")
    pass
