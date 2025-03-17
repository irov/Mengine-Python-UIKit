from Foundation.System import System
from Foundation.DemonManager import DemonManager
from Foundation.TaskManager import TaskManager
from UIKit.Managers.PopUpManager import PopUpManager


TIME_VALUE = 250.0
FADE_VALUE = 0.5

POP_UP = "PopUp"
FADE_GROUP = "FadeUI"


class SystemPopUp(System):
    def __init__(self):
        super(SystemPopUp, self).__init__()
        self.demon = None
        self.pop_up_contents = []
        self.is_pop_up_active = False

    def _onRun(self):
        self.demon = DemonManager.getDemon(POP_UP)
        if self.demon is None:
            return True

        self.addObservers()
        return True

    def addObservers(self):
        self.addObserver(Notificator.onPopUpShow, self._cbPopUpShow)
        self.addObserver(Notificator.onPopUpHide, self._cbPopUpHide)

    def _cbPopUpShow(self, content_id, buttons_state=None):
        if PopUpManager.hasPopUpContent(content_id) is False:
            Trace.log("Manager", 0, "PopUpContent id {!r} doesn't exist in PopUpManager".format(content_id))
            return False

        if buttons_state is not None:
            if buttons_state not in self.demon.entity.BUTTONS_STATES:
                Trace.log("Manager", 0, "Invalid buttons state {!r}".format(buttons_state))
                return False

        self.showPopUp(content_id, buttons_state)
        return False

    def _cbPopUpHide(self):
        if len(self.pop_up_contents) == 0:
            Trace.log("Manager", 0, "No opened PopUpContent to hide PopUp")
            return False

        self.hidePopUp()
        return False

    # - PopUp ----------------------------------------------------------------------------------------------------------

    def getCurrentContentId(self):
        current_content_id = None

        if len(self.pop_up_contents) > 1:
            current_content_id = self.pop_up_contents[-1]
        elif len(self.pop_up_contents) == 1:
            current_content_id = self.pop_up_contents[0]

        return current_content_id

    def showPopUp(self, content_id, buttons_state=None):
        if TaskManager.existTaskChain(POP_UP + "Show") is True:
            return False

        pop_up_entity = self.demon.entity

        # add content to contents queue
        if content_id not in self.pop_up_contents:
            self.pop_up_contents.append(content_id)

        # param to handle pop up fully close or just back to previous content
        if buttons_state is None:
            if len(self.pop_up_contents) > 1:
                buttons_state = pop_up_entity.BUTTONS_STATE_BACK
            else:
                buttons_state = pop_up_entity.BUTTONS_STATE_CLOSE

        # create task chain to show pop up
        with TaskManager.createTaskChain(Name=POP_UP + "Show") as tc:
            # if any pop up is hiding right now, wait till it's done
            with tc.addIfTask(self.getIsPopUpActive) as (true, false):
                true.addListener(Notificator.onPopUpHideEnd)

            tc.addFunction(self.setIsPopUpActive, True)

            # enable pop up layer and initialize entity
            tc.addTask("TaskSceneLayerGroupEnable", LayerName=POP_UP, Value=True)

            with tc.addParallelTask(2) as (fade, pop_up):
                # play fade in if showing first pop up in queue
                with fade.addIfTask(lambda: buttons_state != pop_up_entity.BUTTONS_STATE_BACK) as (true, false):
                    true.addTask("TaskFadeIn", GroupName=FADE_GROUP, To=FADE_VALUE, Time=TIME_VALUE)

                pop_up.addScope(pop_up_entity.showPopUp, content_id, buttons_state)

            tc.addNotify(Notificator.onPopUpShowEnd)

    def hidePopUp(self):
        if TaskManager.existTaskChain(POP_UP + "Hide") is True:
            return False

        pop_up_entity = self.demon.entity

        # remove content from contents queue
        current_content_id = self.getCurrentContentId()
        self.pop_up_contents.remove(current_content_id)

        # prepare variables for task chain
        current_content_id = self.getCurrentContentId()

        # create task chain to hide pop up
        with TaskManager.createTaskChain(Name=POP_UP + "Hide") as tc:
            with tc.addParallelTask(2) as (fade, pop_up):
                # play fade out if hiding last pop up in queue
                with fade.addIfTask(lambda: current_content_id is None) as (true, false):
                    true.addTask("TaskFadeOut", GroupName=FADE_GROUP, From=FADE_VALUE, Time=TIME_VALUE)

                pop_up.addScope(pop_up_entity.hidePopUp)

            # disable pop up layer and finalize entity or show last content in contents queue
            with tc.addIfTask(lambda: current_content_id is None) as (hide, show):
                hide.addTask("TaskSceneLayerGroupEnable", LayerName=POP_UP, Value=False)
                hide.addFunction(self.setIsPopUpActive, False)
                show.addFunction(self.showPopUp, current_content_id)

            tc.addNotify(Notificator.onPopUpHideEnd)

    def setIsPopUpActive(self, value):
        self.is_pop_up_active = value

    def getIsPopUpActive(self):
        return self.is_pop_up_active
