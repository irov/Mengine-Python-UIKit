from Foundation.System import System
from Foundation.DemonManager import DemonManager
from Foundation.TaskManager import TaskManager
from Foundation.SceneManager import SceneManager
from UIKit.Managers.PopUpManager import PopUpManager


class SystemPopUp(System):
    def __init__(self):
        super(SystemPopUp, self).__init__()
        self.demon = None

    def _onRun(self):
        self.demon = DemonManager.getDemon("PopUp")
        if self.demon is None:
            return True

        self.addObservers()
        return True

    def addObservers(self):
        self.addObserver(Notificator.onPopUpShow, self._cbPopUpShow)
        self.addObserver(Notificator.onPopUpHide, self._cbPopUpHide)

    def _cbPopUpShow(self, content_id):
        if TaskManager.existTaskChain("PopUpShow") is True:
            return False

        pop_up_entity = self.demon.entity

        with TaskManager.createTaskChain(Name="PopUpShow") as tc:
            tc.addTask("TaskSceneLayerGroupEnable", LayerName="PopUp", Value=True)
            tc.addScope(pop_up_entity.showPopUp, content_id)

        return False

    def _cbPopUpHide(self):
        if TaskManager.existTaskChain("PopUpHide") is True:
            return False

        pop_up_entity = self.demon.entity

        with TaskManager.createTaskChain(Name="PopUpHide") as tc:
            tc.addScope(pop_up_entity.hidePopUp)
            tc.addTask("TaskSceneLayerGroupEnable", LayerName="PopUp", Value=False)

        return False
