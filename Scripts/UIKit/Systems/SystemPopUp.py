from Foundation.System import System
from Foundation.DemonManager import DemonManager
from Foundation.TaskManager import TaskManager
from UIKit.Managers.PopUpManager import PopUpManager


TIME_VALUE = 250.0
FADE_VALUE = 0.5

POP_UP = "PopUp"
FADE_GROUP = "FadeUI"


class SystemPopUp(System):
    STATE_DISABLE = 0
    STATE_SHOWING = 1
    STATE_ACTIVE = 2
    STATE_HIDING = 3

    def __init__(self):
        super(SystemPopUp, self).__init__()
        self.demon = None
        self.pop_up_contents = []
        self.pop_up_state = None

    def _onRun(self):
        self.demon = DemonManager.getDemon(POP_UP)
        if self.demon is None:
            return True

        self.addObservers()
        return True

    def addObservers(self):
        self.addObserver(Notificator.onPopUpShow, self._cbPopUpShow)
        self.addObserver(Notificator.onPopUpHide, self._cbPopUpHide)
        self.addObserver(Notificator.onPopUpShowDebugAd, self._cbPopUpShowDebugAd)

    def _cbPopUpShow(self, content_id, buttons_state=None, background_size_type=None, **content_args):
        if PopUpManager.hasPopUpContent(content_id) is False:
            Trace.log("Manager", 0, "PopUpContent id {!r} doesn't exist in PopUpManager".format(content_id))
            return False

        if buttons_state is not None:
            if buttons_state not in self.demon.entity.BUTTONS_STATES:
                Trace.log("Manager", 0, "Invalid buttons state {!r}".format(buttons_state))
                return False

        self.showPopUp(content_id, buttons_state, background_size_type, **content_args)
        return False

    def _cbPopUpHide(self):
        if len(self.pop_up_contents) == 0:
            Trace.log("Manager", 0, "No opened PopUpContent to hide PopUp")
            return False

        self.hidePopUp()
        return False

    def _cbPopUpShowDebugAd(self):
        pop_up_entity = self.demon.entity
        self._cbPopUpShow("DebugAd", pop_up_entity.BUTTONS_STATE_DISABLE)
        return False

    # - PopUp ----------------------------------------------------------------------------------------------------------

    def setPopUpState(self, value):
        self.pop_up_state = value

    def getPopUpState(self):
        return self.pop_up_state

    def getCurrentContentId(self):
        current_content_id = None

        if len(self.pop_up_contents) > 1:
            current_content_id = self.pop_up_contents[-1]
        elif len(self.pop_up_contents) == 1:
            current_content_id = self.pop_up_contents[0]

        return current_content_id

    def showPopUp(self, content_id, buttons_state=None, background_size_type=None, **content_args):
        if TaskManager.existTaskChain(POP_UP + "Show") is True:
            return False

        self.setPopUpState(self.STATE_SHOWING)
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

        # set pop up background size type
        pop_up_entity.setBackgroundSizeType(background_size_type)

        # create task chain to show pop up
        with TaskManager.createTaskChain(Name=POP_UP + "Show") as tc:
            # enable pop up layer and initialize entity
            tc.addTask("TaskSceneLayerGroupEnable", LayerName=POP_UP, Value=True)

            with tc.addParallelTask(2) as (fade, pop_up):
                # play fade in if showing first pop up in queue
                with fade.addIfTask(lambda: buttons_state != pop_up_entity.BUTTONS_STATE_BACK) as (true, false):
                    true.addTask("TaskFadeIn", GroupName=FADE_GROUP, To=FADE_VALUE, Time=TIME_VALUE)

                pop_up.addScope(pop_up_entity.showPopUp, content_id, buttons_state, **content_args)

            tc.addNotify(Notificator.onPopUpShowEnd, content_id)
            tc.addFunction(self.setPopUpState, self.STATE_ACTIVE)

    def hidePopUp(self):
        if TaskManager.existTaskChain(POP_UP + "Hide") is True:
            return False

        self.setPopUpState(self.STATE_HIDING)
        pop_up_entity = self.demon.entity

        # remove content from contents queue
        previous_content_id = self.getCurrentContentId()
        self.pop_up_contents.remove(previous_content_id)

        # prepare variables for task chain
        new_content_id = self.getCurrentContentId()

        # create task chain to hide pop up
        with TaskManager.createTaskChain(Name=POP_UP + "Hide") as tc:
            with tc.addParallelTask(2) as (fade, pop_up):
                # play fade out if hiding last pop up in queue
                with fade.addIfTask(lambda: new_content_id is None) as (true, false):
                    true.addTask("TaskFadeOut", GroupName=FADE_GROUP, From=FADE_VALUE, Time=TIME_VALUE)

                pop_up.addScope(pop_up_entity.hidePopUp)

            # disable pop up layer and finalize entity or show last content in contents queue
            with tc.addIfTask(lambda: new_content_id is None) as (hide, show):
                hide.addTask("TaskSceneLayerGroupEnable", LayerName=POP_UP, Value=False)
                show.addFunction(self.showPopUp, new_content_id)

            tc.addNotify(Notificator.onPopUpHideEnd, previous_content_id)
            tc.addFunction(self.setPopUpState, self.STATE_DISABLE)
