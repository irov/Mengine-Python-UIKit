from Foundation.System import System
from Foundation.DemonManager import DemonManager
from Foundation.TaskManager import TaskManager
from Foundation.SceneManager import SceneManager
from UIKit.Managers.PopUpManager import PopUpManager


class SystemPopUp(System):
    def __init__(self):
        super(SystemPopUp, self).__init__()

    def _onRun(self):
        self.addObservers()
        return True

    # observers
    def addObservers(self):
        self.addObserver(Notificator.onPopUpShow, self._cbPopUpShow)
        self.addObserver(Notificator.onPopUpHide, self._cbPopUpHide)
        self.addObserver(Notificator.onSceneActivate, self._cbSceneActivate)

    def _cbPopUpShow(self, pop_up_id=None):
        # if PopUpManager.hasPopUpContent(pop_up_id) is False:
        #     Trace.log("Manager", 0, "popup_ip {!r} doesn't exist in PopUpManager".format(pop_up_id))
        #     return False
        #
        # pop_up = DemonManager.getDemon("PopUp")
        # open_pop_ups = pop_up.getParam("OpenPopUps")
        #
        # if pop_up_id not in open_pop_ups:
        #     pop_up.appendParam("OpenPopUps", pop_up_id)

        # self._openPopUp(pop_up)
        self._openPopUp()

        return False

    def _cbPopUpHide(self, popup_id):
        pop_up = DemonManager.getDemon("PopUp")
        open_pop_ups = pop_up.getParam("OpenPopUps")

        if popup_id in open_pop_ups:
            pop_up.delParam("OpenPopUps", popup_id)

        self._closePopUp(open_pop_ups)

        if pop_up.isActive() is False or pop_up.isEntityActivate() is False:
            # not in scene groups or entity is not active (or scene is None at this moment)
            return False

        return False

    def _openPopUp(self, pop_up=None):
        # if pop_up.hasEntity() is False:
        #     if SceneManager.isCurrentSceneActive() is True:
        #         Trace.log("Manager", 0, "PopUp has no entity (maybe group is not attached at scene)")
        #     return
        # if pop_up.isEntityActivate() is True:
        #     return

        if TaskManager.existTaskChain("PopUp_OpenFlow") is True:
            return
        with TaskManager.createTaskChain(Name="PopUp_OpenFlow") as tc:
            # tc.addTask("TaskSceneLayerGroupEnable", LayerName="PopUp", Value=True)
            tc.addTask("TaskFadeIn", GroupName="Fade", To=0.5, Time=250.0)

    def _closePopUp(self, open_pop_ups):
        if len(open_pop_ups) != 0:
            return

        if TaskManager.existTaskChain("PopUp_CloseFlow") is True:
            return
        with TaskManager.createTaskChain(Name="PopUp_CloseFlow") as tc:
            # tc.addTask("TaskSceneLayerGroupEnable", LayerName="PopUp", Value=False)
            tc.addTask("TaskFadeOut", GroupName="Fade", From=0.5, Time=250.0)

    def _cbSceneActivate(self, scene_name):
        pop_up = DemonManager.getDemon("PopUp")
        open_pop_ups = pop_up.getParam("OpenPopUps")
        if len(open_pop_ups) != 0:
            self._openPopUp(pop_up)

        return False





