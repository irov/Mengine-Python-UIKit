from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager
from UIKit.Managers.PopUpManager import PopUpManager
from UIKit.Managers.PrototypeManager import PrototypeManager
from UIKit.AdjustableScreenUtils import AdjustableScreenUtils


MOVIE_CONTENT = "Movie2_Content"
SLOT_BG = "background"
SLOT_CONTENT = "content"
SLOT_CLOSE = "close"
SLOT_BACK = "back"
TITLE_ALIAS = "$AliasPopUpTitle"
TITLE_TEXT_ID = "ID_PopUpTitle"


PROTOTYPE_BG = "PopUpBackground"
PROTOTYPE_BG_TYPE = "Normal"

PROTOTYPE_BUTTON = "PopUpButton"
PROTOTYPE_BUTTON_CLOSE = "close"
PROTOTYPE_BUTTON_BACK = "back"

TITLE_OFFSET_Y = 50.0

TIME_VALUE = 250.0
FADE_VALUE = 0.5
SCALE_VALUE = (1.1, 1.1, 1.0)


class PopUp(BaseEntity):
    def __init__(self):
        super(PopUp, self).__init__()
        self.content = None
        self.tcs = []
        self.background = None
        self.buttons = {}
        self.pop_up_contents = {}

    # - BaseEntity -----------------------------------------------------------------------------------------------------

    def _onPreparation(self):
        super(PopUp, self)._onPreparation()

        if self._setupContentBase() is False:
            return False

        self._setupBackground()
        self._setupButtons()
        self._setupTitle()

    def _onActivate(self):
        super(PopUp, self)._onActivate()

        self._runTaskChains()

    def _onDeactivate(self):
        super(PopUp, self)._onDeactivate()

        for tc in self.tcs:
            tc.cancel()
        self.tcs = []

        for popup_content in self.pop_up_contents.values():
            popup_content.onFinalize()
        self.pop_up_contents = {}

        self.last_pop_up_content_id = None

        for btn in self.buttons.values():
            btn.onDestroy()
        self.buttons = {}

        if self.background is not None:
            self.background.onDestroy()
            self.background = None

        if self.content is not None:
            self.content.onDestroy()
            self.content = None

    # - PopUp Elements -------------------------------------------------------------------------------------------------

    def _setupContentBase(self):
        self.content = self.object.generateObjectUnique(MOVIE_CONTENT, MOVIE_CONTENT)
        if self.content is None:
            Trace.log("Entity", 0, "Not found {!r} in {!r}".format(MOVIE_CONTENT, self.object.getName()))
            return False

        self.content.setEnable(True)

        content_node = self.content.getEntityNode()
        self.addChild(content_node)

        _, _, _, _, _, x_center, y_center = AdjustableScreenUtils.getMainSizesExt()
        content_node.setWorldPosition(Mengine.vec2f(x_center, y_center))

        return True

    def _setupBackground(self):
        slot_bg = self.content.getMovieSlot(SLOT_BG)
        background_prototype = PrototypeManager.generateObjectUniqueOnNode(slot_bg, PROTOTYPE_BG, Size=PROTOTYPE_BG_TYPE)
        background_prototype.setEnable(True)
        self.background = background_prototype

    def getBackgroundSizes(self):
        bounding_box = self.background.getCompositionBounds()
        box_size = Utils.getBoundingBoxSize(bounding_box)
        return box_size

    def _setupButtons(self):
        # generating buttons
        slot_close = self.content.getMovieSlot(SLOT_CLOSE)
        button_close_prototype = PrototypeManager.generateObjectContainerOnNode(slot_close, PROTOTYPE_BUTTON, Size=PROTOTYPE_BUTTON_CLOSE)
        button_close_prototype.setEnable(True)
        self.buttons[PROTOTYPE_BUTTON_CLOSE] = button_close_prototype

        slot_back = self.content.getMovieSlot(SLOT_BACK)
        button_back_prototype = PrototypeManager.generateObjectContainerOnNode(slot_back, PROTOTYPE_BUTTON, Size=PROTOTYPE_BUTTON_BACK)
        self.buttons[PROTOTYPE_BUTTON_BACK] = button_back_prototype

        # calculating and setting buttons pos
        background_sizes = self.getBackgroundSizes()
        buttons_pos = Mengine.vec2f(background_sizes.x/2, -background_sizes.y/2)

        for button in self.buttons.values():
            button_bounds = button.getCompositionBounds()
            button_size = Utils.getBoundingBoxSize(button_bounds)
            button_pos = Mengine.vec2f(buttons_pos.x - button_size.x/2, buttons_pos.y + button_size.y/2)
            button_node = button.getEntityNode()
            button_node.setLocalPosition(button_pos)

    def _updateButtons(self):
        pop_ups_contents = self.pop_up_contents.values()

        if len(pop_ups_contents) > 1:
            self.buttons[PROTOTYPE_BUTTON_BACK].setEnable(True)
            self.buttons[PROTOTYPE_BUTTON_CLOSE].setEnable(False)
        else:
            self.buttons[PROTOTYPE_BUTTON_CLOSE].setEnable(True)
            self.buttons[PROTOTYPE_BUTTON_BACK].setEnable(False)

    def _setupTitle(self):
        Mengine.setTextAlias("", TITLE_ALIAS, TITLE_TEXT_ID)
        Mengine.setTextAliasArguments("", TITLE_ALIAS, "")

        title = self.content.getMovieText(TITLE_ALIAS)
        background_sizes = self.getBackgroundSizes()
        title_height = title.getFontHeight()
        title.setLocalPosition(Mengine.vec2f(0, -background_sizes.y/2 + title_height/2 + TITLE_OFFSET_Y))
        title.setVerticalCenterAlign()
        title.setHorizontalCenterAlign()

    def _updateTitle(self):
        pop_up_content_id = list(self.pop_up_contents)[-1]
        pop_up_content = self.pop_up_contents[pop_up_content_id]
        title_text = Mengine.getTextFromId(pop_up_content.title_text_id)
        Mengine.setTextAliasArguments("", TITLE_ALIAS, title_text)

    def getTitleSizes(self):
        title = self.content.getMovieText(TITLE_ALIAS)
        title_sizes = title.getTextSize()
        return title_sizes

    def updatePopUpElements(self):
        self._updateButtons()
        self._updateTitle()

    # - TaskChain ------------------------------------------------------------------------------------------------------

    def _createTaskChain(self, name, **params):
        tc = TaskManager.createTaskChain(Name=self.__class__.__name__+"_"+name, **params)
        self.tcs.append(tc)
        return tc

    def _runTaskChains(self):
        with self._createTaskChain("ActionButtons", Repeat=True) as tc:
            for key, tc_race in tc.addRaceTaskList(self.buttons.keys()):
                tc_race.addTask("TaskMovie2ButtonClick", Movie2Button=self.buttons[key].movie)
                tc_race.addNotify(Notificator.onPopUpHide)

    def showPopUp(self, source, content_id):
        content_node = self.content.getEntityNode()

        # play hide popup anim, before showing new content
        with source.addIfTask(lambda: len(self.pop_up_contents) != 0) as (true, false):
            true.addScope(self.hidePopUp)

        # play show popup anim with content
        with source.addParallelTask(2) as (pop_up, content):
            content.addScope(self.showPopUpContent, content_id)

            with pop_up.addParallelTask(3) as (fade, alpha, scale):
                alpha.addTask("TaskNodeAlphaTo", Node=content_node, From=0.0, To=1.0, Time=TIME_VALUE)
                fade.addTask("TaskFadeIn", GroupName="FadeUI", To=FADE_VALUE, Time=TIME_VALUE)
                scale.addTask("TaskNodeScaleTo", Node=content_node, From=SCALE_VALUE, To=(1.0, 1.0, 1.0), Time=TIME_VALUE)

    def hidePopUp(self, source):
        content_node = self.content.getEntityNode()

        # play hide popup anim with content
        with source.addParallelTask(2) as (pop_up, content):
            content.addScope(self.hidePopUpContent)

            with pop_up.addParallelTask(3) as (fade, alpha, scale):
                alpha.addTask("TaskNodeAlphaTo", Node=content_node, From=1.0, To=0.0, Time=TIME_VALUE)
                fade.addTask("TaskFadeOut", GroupName="FadeUI", From=FADE_VALUE, Time=TIME_VALUE)
                scale.addTask("TaskNodeScaleTo", Node=content_node, From=(1.0, 1.0, 1.0), To=SCALE_VALUE, Time=TIME_VALUE)

    def showPopUpContent(self, source, pop_up_content_id):
        if pop_up_content_id not in self.pop_up_contents:
            pop_up_content = PopUpManager.getPopUpContent(pop_up_content_id)
            pop_up_content.onInitialize(self)
            self.pop_up_contents[pop_up_content_id] = pop_up_content

        pop_up_content = self.pop_up_contents[pop_up_content_id]

        pop_up_content_slot = self.content.getMovieSlot(SLOT_CONTENT)
        pop_up_content.attachTo(pop_up_content_slot)

        pop_up_content_node = pop_up_content.getNode()

        source.addFunction(self.updatePopUpElements)
        source.addTask("TaskNodeAlphaTo", Node=pop_up_content_node, From=0.0, To=1.0, Time=TIME_VALUE)

    def hidePopUpContent(self, source):
        pop_up_content_id = list(self.pop_up_contents)[-1]
        pop_up_content = self.pop_up_contents[pop_up_content_id]
        pop_up_content_node = pop_up_content.getNode()

        self.pop_up_contents.pop(pop_up_content_id)

        source.addTask("TaskNodeAlphaTo", Node=pop_up_content_node, From=1.0, To=0.0, Time=TIME_VALUE)
        source.addFunction(pop_up_content.onFinalize)
