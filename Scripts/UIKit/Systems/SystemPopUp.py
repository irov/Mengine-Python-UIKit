from Foundation.System import System
from Foundation.DemonManager import DemonManager
from Foundation.TaskManager import TaskManager
from UIKit.Managers.PopUpManager import PopUpManager


TIME_VALUE = 250.0
FADE_VALUE = 0.5


class SystemPopUp(System):
    def __init__(self):
        super(SystemPopUp, self).__init__()
        self.demon = None
        self.contents = []

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
        if PopUpManager.hasPopUpContent(content_id) is False:
            Trace.log("Manager", 0, "PopUpContent id {!r} doesn't exist in PopUpManager".format(content_id))
            return False

        self.showPopUp(content_id)

        return False

    def showPopUp(self, content_id):
        if TaskManager.existTaskChain("PopUpShow") is True:
            return False

        if content_id not in self.contents:
            self.contents.append(content_id)

        if len(self.contents) > 1:
            is_back_allowed = True
        else:
            is_back_allowed = False

        pop_up_entity = self.demon.entity

        with TaskManager.createTaskChain(Name="PopUpShow") as tc:
            tc.addTask("TaskSceneLayerGroupEnable", LayerName="PopUp", Value=True)

            with tc.addParallelTask(2) as (fade, pop_up):
                with fade.addIfTask(lambda: is_back_allowed is False) as (true, false):
                    true.addTask("TaskFadeIn", GroupName="FadeUI", To=FADE_VALUE, Time=TIME_VALUE)

                pop_up.addScope(pop_up_entity.showPopUp, content_id, is_back_allowed)

    def _cbPopUpHide(self):
        if TaskManager.existTaskChain("PopUpHide") is True:
            return False

        current_content_id = self.__getCurrentContentId()
        self.contents.remove(current_content_id)
        current_content_id = self.__getCurrentContentId()

        pop_up_entity = self.demon.entity

        with TaskManager.createTaskChain(Name="PopUpHide") as tc:
            with tc.addParallelTask(2) as (fade, pop_up):
                with fade.addIfTask(lambda: current_content_id is None) as (true, false):
                    true.addTask("TaskFadeOut", GroupName="FadeUI", From=FADE_VALUE, Time=TIME_VALUE)

                pop_up.addScope(pop_up_entity.hidePopUp)

            with tc.addIfTask(lambda: current_content_id is None) as (hide, show):
                hide.addTask("TaskSceneLayerGroupEnable", LayerName="PopUp", Value=False)
                show.addFunction(self.showPopUp, current_content_id)

        return False

    def __getCurrentContentId(self):
        current_content_id = None
        if len(self.contents) > 1:
            current_content_id = self.contents[-1]
        elif len(self.contents) == 1:
            current_content_id = self.contents[0]

        return current_content_id
