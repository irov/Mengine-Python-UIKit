def onInitialize():
    from Foundation.Notificator import Notificator

    identities = [
    ]
    Notificator.addIdentities(identities)

    from TraceManager import TraceManager

    traces = [
    ]
    TraceManager.addTraces(traces)

    from Foundation.EntityManager import EntityManager
    from Foundation.ObjectManager import ObjectManager

    Types = [
    ]
    if EntityManager.importEntities("MobileKit.Entities", Types) is False:
        return False
    if ObjectManager.importObjects("MobileKit.Objects", Types) is False:
        return False

    # uncomment if you want to add new params for each account
    """
    from Foundation.AccountManager import AccountManager
    def accountSetuper(accountID, isGlobal):
        if isGlobal is True:
            return

    AccountManager.setCreateAccount(accountSetuper)
    """

    return True
