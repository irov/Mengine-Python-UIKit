from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager
from UIKit.Managers.PopUpManager import PopUpManager
from UIKit.Managers.PrototypeManager import PrototypeManager
from UIKit.AdjustableScreenUtils import AdjustableScreenUtils


PROTOTYPE_BG = "PopUpBackground"
PROTOTYPE_BG_TYPE = "Normal"

PROTOTYPE_BUTTON = "PopUpButton"
PROTOTYPE_BUTTON_CLOSE = "close"
PROTOTYPE_BUTTON_BACK = "back"

POPUP_TITLE_ALIAS = "$AliasPopUpTitle"
TITLE_OFFSET_Y = 50.0


class PopUp(BaseEntity):

    def __init__(self):
        super(PopUp, self).__init__()
        self.root = None
        self.tcs = []
        self.background = None
        self.buttons = {}
        self.title = None
        self.contents = {}

    # - BaseEntity -----------------------------------------------------------------------------------------------------

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addActionActivate(Type, "OpenPopUps", Append=PopUp._cbAppendOpenPopUps, Remove=PopUp._cbRemoveOpenPopUps)

    def _cbAppendOpenPopUps(self, index, popup_id):
        self._updatePopUp()

        prev_popup_id = self.object.getParam("OpenPopUps")[index-1]
        self.contents[prev_popup_id].onDeactivate()

    def _cbRemoveOpenPopUps(self, index, popup_id, old):
        self._updatePopUp()
        self.contents[popup_id].onDeactivate()

    def _onPreparation(self):
        super(PopUp, self)._onPreparation()

        self._setupRoot()
        self._setupBackground()
        self._setupButtons()
        self._setupTitle()

        self._loadContent()
        self._updatePopUp()

    def _onActivate(self):
        super(PopUp, self)._onActivate()

        self._runTaskChains()

    def _onDeactivate(self):
        super(PopUp, self)._onDeactivate()

        for tc in self.tcs:
            tc.cancel()
        self.tcs = []

        for popup_content in self.contents.values():
            if popup_content.isActivated() is True:
                popup_content.onDeactivate()
            popup_content.onFinalize()
        self.contents = {}

        if self.title is not None:
            Mengine.destroyNode(self.title)
            self.title = None

        for btn in self.buttons.values():
            btn.onDestroy()
        self.buttons = {}

        if self.background is not None:
            self.background.onDestroy()
            self.background = None

        if self.root is not None:
            Mengine.destroyNode(self.root)
            self.root = None

    # - Root -----------------------------------------------------------------------------------------------------------

    def _setupRoot(self):
        node = Mengine.createNode("Interender")
        node.setName(self.__class__.__name__)

        self.addChild(node)
        _, _, _, _, _, x_center, y_center = AdjustableScreenUtils.getMainSizesExt()
        node.setWorldPosition(Mengine.vec2f(x_center, y_center))

        self.root = node

    # - PopUp base -----------------------------------------------------------------------------------------------------

    def _setupBackground(self):
        background_prototype = PrototypeManager.generateObjectUniqueOnNode(self.root, PROTOTYPE_BG, Size=PROTOTYPE_BG_TYPE)
        background_prototype.setEnable(True)
        background_prototype.setInteractive(True)
        self.background = background_prototype

    def _setupButtons(self):
        # generating buttons
        button_close_prototype = PrototypeManager.generateObjectContainerOnNode(self.root, PROTOTYPE_BUTTON, Size=PROTOTYPE_BUTTON_CLOSE)
        self.buttons[PROTOTYPE_BUTTON_CLOSE] = button_close_prototype

        button_back_prototype = PrototypeManager.generateObjectContainerOnNode(self.root, PROTOTYPE_BUTTON, Size=PROTOTYPE_BUTTON_BACK)
        self.buttons[PROTOTYPE_BUTTON_BACK] = button_back_prototype

        # calculating and setting buttons pos
        background_sizes = self.getSizes()
        buttons_pos = Mengine.vec2f(background_sizes.x/2, -background_sizes.y/2)

        for button in self.buttons.values():
            button_bounds = button.getCompositionBounds()
            button_size = Utils.getBoundingBoxSize(button_bounds)
            button_pos = Mengine.vec2f(buttons_pos.x - button_size.x/2, buttons_pos.y + button_size.y/2)
            button_node = button.getEntityNode()
            button_node.setLocalPosition(button_pos)

    def _setupTitle(self):
        node = Mengine.createNode("TextField")
        node.setName(self.__class__.__name__+"_"+"Title")
        node.setVerticalCenterAlign()
        node.setHorizontalCenterAlign()
        node.setTextId("ID_EMPTY")

        self.root.addChild(node)
        background_sizes = self.getSizes()
        text_height = node.getFontHeight()
        node.setLocalPosition(Mengine.vec2f(0, -background_sizes.y/2 + text_height/2 + TITLE_OFFSET_Y))

        self.title = node

    def getSizes(self):
        bounding_box = self.background.getCompositionBounds()
        box_size = Utils.getBoundingBoxSize(bounding_box)
        return box_size

    # - Content --------------------------------------------------------------------------------------------------------

    def _loadContent(self):
        for popup_id, popup_content in PopUpManager.getAllPopUpContents().items():
            self.contents[popup_id] = popup_content
            popup_content.onInitialize(self)
            popup_content.onPreparation()

    def _updatePopUp(self):
        self._updateContent()
        self._updateActionButtons()
        self._updateTitle()

    def _updateContent(self):
        if len(self.object.getParam("OpenPopUps")) == 0:
            return

        current_popup_id = self.object.getParam("OpenPopUps")[-1]
        popup_content = self.contents[current_popup_id]

        if popup_content.isActivated() is False:
            popup_content.onActivate()

    def _updateActionButtons(self):
        open_popups = self.object.getParam("OpenPopUps")

        if len(open_popups) <= 1:
            self.buttons[PROTOTYPE_BUTTON_CLOSE].setEnable(True)
            self.buttons[PROTOTYPE_BUTTON_BACK].setEnable(False)
        else:
            self.buttons[PROTOTYPE_BUTTON_BACK].setEnable(True)
            self.buttons[PROTOTYPE_BUTTON_CLOSE].setEnable(False)

    def _updateTitle(self):
        open_pop_ups = self.object.getParam("OpenPopUps")

        if len(open_pop_ups) == 0:
            return

        current_popup_id = open_pop_ups[-1]
        current_popup_content = self.contents[current_popup_id]
        Mengine.setTextAlias("", POPUP_TITLE_ALIAS, current_popup_content.title_text_id)

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
