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


class PopUp(BaseEntity):

    def __init__(self):
        super(PopUp, self).__init__()
        self.content = None
        self.tcs = []
        self.background = None
        self.buttons = {}
        self.title = None
        self.pop_up_contents = {}

    # - BaseEntity -----------------------------------------------------------------------------------------------------

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addActionActivate(Type, "OpenPopUps", Append=PopUp._cbAppendOpenPopUps, Remove=PopUp._cbRemoveOpenPopUps)

    def _cbAppendOpenPopUps(self, index, popup_id):
        self._updatePopUp()

        prev_popup_id = self.object.getParam("OpenPopUps")[index-1]
        # self.contents[prev_popup_id].onDeactivate()

    def _cbRemoveOpenPopUps(self, index, popup_id, old):
        self._updatePopUp()
        # self.contents[popup_id].onDeactivate()

    def _onPreparation(self):
        super(PopUp, self)._onPreparation()

        if self._setupContent() is False:
            return False

        self._setupBackground()
        self._setupButtons()
        self._setupTitle()

        self._setupPopUpContent()
        self._updatePopUp()

    def _onActivate(self):
        super(PopUp, self)._onActivate()

        self._runTaskChains()

    def _onDeactivate(self):
        super(PopUp, self)._onDeactivate()

        for tc in self.tcs:
            tc.cancel()
        self.tcs = []

        for popup_content in self.pop_up_contents.values():
            # if popup_content.isActivated() is True:
            #     popup_content.onDeactivate()
            popup_content.onFinalize()
        self.pop_up_contents = {}

        if self.title is not None:
            Mengine.destroyNode(self.title)
            self.title = None

        for btn in self.buttons.values():
            btn.onDestroy()
        self.buttons = {}

        if self.background is not None:
            self.background.onDestroy()
            self.background = None

        if self.content is not None:
            self.content.onDestroy()
            self.content = None

    # - PopUp Setup ----------------------------------------------------------------------------------------------------

    def _setupContent(self):
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
        open_popups = self.object.getParam("OpenPopUps")

        if len(open_popups) <= 1:
            self.buttons[PROTOTYPE_BUTTON_CLOSE].setEnable(True)
            self.buttons[PROTOTYPE_BUTTON_BACK].setEnable(False)
        else:
            self.buttons[PROTOTYPE_BUTTON_BACK].setEnable(True)
            self.buttons[PROTOTYPE_BUTTON_CLOSE].setEnable(False)

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
        open_pop_ups = self.object.getParam("OpenPopUps")

        if len(open_pop_ups) == 0:
            return

        current_popup_id = open_pop_ups[-1]
        current_popup_content = self.pop_up_contents[current_popup_id]
        title_text = Mengine.getTextFromId(current_popup_content.title_text_id)
        Mengine.setTextAliasArguments("", TITLE_ALIAS, title_text)

    def getTitleSizes(self):
        title = self.content.getMovieText(TITLE_ALIAS)
        title_sizes = title.getTextSize()
        return title_sizes

    def _setupPopUpContent(self):
        current_popup_id = self.object.getParam("OpenPopUps")[-1]
        pop_up_content = PopUpManager.getPopUpContent(current_popup_id)
        self.pop_up_contents[current_popup_id] = pop_up_content
        pop_up_content.onInitialize(self)

        content_slot = self.content.getMovieSlot(SLOT_CONTENT)
        pop_up_content.attachTo(content_slot)

    def _updatePopUpContent(self):
        if len(self.object.getParam("OpenPopUps")) == 0:
            return

        current_popup_id = self.object.getParam("OpenPopUps")[-1]
        popup_content = self.pop_up_contents[current_popup_id]

        # if popup_content.isActivated() is False:
        #     popup_content.onActivate()

    def _updatePopUp(self):
        self._updatePopUpContent()
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
            tc.addScope(self._scopeCloseLastContent)

    def _scopeCloseLastContent(self, source):
        open_popups = self.object.getParam("OpenPopUps")
        if len(open_popups) == 0:
            source.addNotify(Notificator.onPopUpHide, None)
            return

        last_popup_id = open_popups[-1]
        source.addNotify(Notificator.onPopUpHide, last_popup_id)
