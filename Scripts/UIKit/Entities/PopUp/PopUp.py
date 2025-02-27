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
SCALE_VALUE = (1.1, 1.1, 1.0)


class PopUp(BaseEntity):
    def __init__(self):
        super(PopUp, self).__init__()
        self.tcs = []
        self.hotspot_block = None
        self.content = None
        self.background = None
        self.buttons = {}
        self.pop_up_content = None
        self.is_back_allowed = False

    # - BaseEntity -----------------------------------------------------------------------------------------------------

    def _onPreparation(self):
        super(PopUp, self)._onPreparation()

        if self._setupContentBase() is False:
            return False

        self._setupHotspotBlock()
        self._setupBackground()
        self._setupButtons()
        self._setupTitle()

        self._setupContentBasePos()

    def _onActivate(self):
        super(PopUp, self)._onActivate()

        self._runTaskChains()

    def _onDeactivate(self):
        super(PopUp, self)._onDeactivate()

        for tc in self.tcs:
            tc.cancel()
        self.tcs = []

        if self.pop_up_content is not None:
            if self.pop_up_content.isInitialized() is True:
                self.pop_up_content.onFinalize()
            self.pop_up_content = None

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

        if self.hotspot_block is not None:
            Mengine.destroyNode(self.hotspot_block)
            self.hotspot_block = None

        self.is_back_allowed = False

    # - PopUp Elements -------------------------------------------------------------------------------------------------

    def _setupHotspotBlock(self):
        self.hotspot_block = Mengine.createNode("HotSpotPolygon")
        self.hotspot_block.setName(self.__class__.__name__ + "_" + "Block")

        viewport = Mengine.getGameViewport()
        hotspot_polygon = [viewport.begin, (viewport.end.x, viewport.begin.y),
                           viewport.end, (viewport.begin.x, viewport.end.y)]
        self.hotspot_block.setPolygon(hotspot_polygon)

        self.addChildFront(self.hotspot_block)

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

    def _setupContentBasePos(self):
        pop_up_content_slot = self.content.getMovieSlot(SLOT_CONTENT)
        background_size = self.getBackgroundSize()
        content_size = self.getContentSize()

        pop_up_content_slot.setLocalPosition(Mengine.vec2f(0, (background_size.y - content_size.y)/2))

    def getContentSize(self):
        background_size = self.getBackgroundSize()
        header_size = self.getHeaderSize()
        content_size = Mengine.vec2f(background_size.x, background_size.y - header_size.y)
        return content_size

    def _setupBackground(self):
        slot_bg = self.content.getMovieSlot(SLOT_BG)
        background_prototype = PrototypeManager.generateObjectUniqueOnNode(slot_bg, PROTOTYPE_BG, Size=PROTOTYPE_BG_TYPE)
        background_prototype.setEnable(True)
        self.background = background_prototype

    def getBackgroundSize(self):
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
        background_size = self.getBackgroundSize()
        buttons_pos = Mengine.vec2f(background_size.x/2, -background_size.y/2)

        for button in self.buttons.values():
            button_bounds = button.getCompositionBounds()
            button_size = Utils.getBoundingBoxSize(button_bounds)
            button_pos = Mengine.vec2f(buttons_pos.x - button_size.x/2, buttons_pos.y + button_size.y/2)
            button_node = button.getEntityNode()
            button_node.setLocalPosition(button_pos)

    def getButtonSize(self):
        button_size = Mengine.vec2f(0, 0)

        for button in self.buttons.values():
            size = button.getSize()
            if button_size.y < size.y:
                button_size = size

        return button_size

    def _updateButtons(self):
        if self.is_back_allowed is True:
            self.buttons[PROTOTYPE_BUTTON_BACK].setEnable(True)
            self.buttons[PROTOTYPE_BUTTON_CLOSE].setEnable(False)
        else:
            self.buttons[PROTOTYPE_BUTTON_CLOSE].setEnable(True)
            self.buttons[PROTOTYPE_BUTTON_BACK].setEnable(False)

    def _setupTitle(self):
        Mengine.setTextAlias("", TITLE_ALIAS, TITLE_TEXT_ID)
        Mengine.setTextAliasArguments("", TITLE_ALIAS, "")

        title = self.content.getMovieText(TITLE_ALIAS)
        background_sizes = self.getBackgroundSize()
        title_height = title.getFontHeight()
        title.setLocalPosition(Mengine.vec2f(0, -background_sizes.y/2 + title_height/2 + TITLE_OFFSET_Y))
        title.setVerticalCenterAlign()
        title.setHorizontalCenterAlign()

    def _updateTitle(self):
        pop_up_content_title = self.pop_up_content.title_text_id

        title_text = Mengine.getTextFromId(pop_up_content_title)
        Mengine.setTextAliasArguments("", TITLE_ALIAS, title_text)

    def getTitleSize(self):
        title = self.content.getMovieText(TITLE_ALIAS)
        title_sizes = title.getTextSize()
        return title_sizes

    def getHeaderSize(self):
        title_size = self.getTitleSize()
        button_size = self.getButtonSize()
        header_size = Mengine.vec2f(max(title_size.x, button_size.x), max(title_size.y, button_size.y))
        return header_size

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

    def showPopUp(self, source, content_id, is_back_allowed):
        self.is_back_allowed = is_back_allowed
        content_node = self.content.getEntityNode()

        # play hide popup anim, before showing new content
        with source.addIfTask(lambda: self.pop_up_content is not None) as (true, false):
            true.addScope(self.hidePopUp)

        # play show popup anim with content
        with source.addParallelTask(2) as (pop_up, content):
            content.addScope(self.showPopUpContent, content_id)

            with pop_up.addParallelTask(2) as (alpha, scale):
                alpha.addTask("TaskNodeAlphaTo", Node=content_node, From=0.0, To=1.0, Time=TIME_VALUE)
                scale.addTask("TaskNodeScaleTo", Node=content_node, From=SCALE_VALUE, To=(1.0, 1.0, 1.0), Time=TIME_VALUE)

    def hidePopUp(self, source):
        content_node = self.content.getEntityNode()

        # play hide popup anim with content
        with source.addParallelTask(2) as (pop_up, content):
            content.addScope(self.hidePopUpContent)

            with pop_up.addParallelTask(2) as (alpha, scale):
                alpha.addTask("TaskNodeAlphaTo", Node=content_node, From=1.0, To=0.0, Time=TIME_VALUE)
                scale.addTask("TaskNodeScaleTo", Node=content_node, From=(1.0, 1.0, 1.0), To=SCALE_VALUE, Time=TIME_VALUE)

    def showPopUpContent(self, source, pop_up_content_id):
        self.pop_up_content = PopUpManager.getPopUpContent(pop_up_content_id)
        self.pop_up_content.onInitialize(self)

        pop_up_content_slot = self.content.getMovieSlot(SLOT_CONTENT)
        self.pop_up_content.attachTo(pop_up_content_slot)

        pop_up_content_node = self.pop_up_content.getNode()

        source.addFunction(self.updatePopUpElements)
        source.addTask("TaskNodeAlphaTo", Node=pop_up_content_node, From=0.0, To=1.0, Time=TIME_VALUE)

    def hidePopUpContent(self, source):
        pop_up_content = self.pop_up_content
        self.pop_up_content = None

        pop_up_content_node = pop_up_content.getNode()

        source.addTask("TaskNodeAlphaTo", Node=pop_up_content_node, From=1.0, To=0.0, Time=TIME_VALUE)
        source.addFunction(pop_up_content.onFinalize)
