from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager
from UIKit.Managers.PopUpManager import PopUpManager
from UIKit.Managers.PrototypeManager import PrototypeManager
from UIKit.AdjustableScreenUtils import AdjustableScreenUtils


SLOT_BG = "background"
PROTOTYPE_BG = "PopUpBackground"

SLOT_CLOSE = "close"
SLOT_BACK = "back"
PROTOTYPE_BUTTON = "PopUpButton"

POPUP_TITLE_ALIAS = "$AliasPopUpTitle"


class PopUp(BaseEntity):

    def __init__(self):
        super(PopUp, self).__init__()
        self._content = None
        self.contents = {}

        self.tc_buttons = None
        self.buttons = {}
        self.generated = {}

    # - BaseEntity -----------------------------------------------------------------------------------------------------

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addActionActivate(Type, "OpenPopUps", Append=PopUp._cbAppendOpenPopUps, Remove=PopUp._cbRemoveOpenPopUps)

    def _cbAppendOpenPopUps(self, index, popup_id):
        self._update()

        prev_popup_id = self.object.OpenPopUps[index-1]
        self.contents[prev_popup_id].onDeactivate()

    def _cbRemoveOpenPopUps(self, index, popup_id, old):
        self._update()
        self.contents[popup_id].onDeactivate()

    def _onPreparation(self):
        super(PopUp, self)._onPreparation()

        if self.object.hasObject("Movie2_Content") is False:
            Trace.log("Entity", 0, "Not found Movie2_Content in {!r}".format(self.object.getName()))
            return

        self._content = self.object.getObject("Movie2_Content")
        self._content.setInteractive(True)

        self._setPosition()

        self._setupBackground()
        self._setupButtons()

        self._loadContent()
        self._update()

    def _onActivate(self):
        super(PopUp, self)._onActivate()

        self.tc_buttons = TaskManager.createTaskChain(Name="PopUp_ActionButtons", Repeat=True)
        with self.tc_buttons as tc:
            with tc.addRaceTask(2) as (close, back):
                close.addTask("TaskMovie2ButtonClick", Movie2Button=self.buttons["close"])
                back.addTask("TaskMovie2ButtonClick", Movie2Button=self.buttons["back"])
            tc.addScope(self._scopeCloseLastContent)

    def _onDeactivate(self):
        super(PopUp, self)._onDeactivate()

        if self.tc_buttons is not None:
            self.tc_buttons.cancel()
            self.tc_buttons = None

        self._content = None

        for btn in self.buttons.values():
            btn.onDestroy()
        self.buttons = {}

        for obj in self.generated.values():
            obj.onDestroy()
        self.generated = {}

        for popup_content in self.contents.values():
            if popup_content.isActivated() is True:
                popup_content.onDeactivate()
            popup_content.onFinalize()
        self.contents = {}

    # - Utils ----------------------------------------------------------------------------------------------------------

    def _attachTo(self, btn, slot_name):
        slot = self._content.getMovieSlot(slot_name)
        node = btn.getEntityNode()
        slot.addChild(node)

    def getContentBoundingBox(self):
        """ returns bounding box which is used for content positioning """
        bounding_box = self._content.getCompositionBounds()
        return bounding_box

    # - Components -----------------------------------------------------------------------------------------------------

    def _setupBackground(self):
        background_slot = self._content.getMovieSlot(SLOT_BG)
        background_prototype = PrototypeManager.generateObjectUniqueOnNode(background_slot, PROTOTYPE_BG, Size="Normal")
        background_prototype.setEnable(True)
        self.generated[SLOT_BG] = background_prototype

    def _setupButtons(self):
        button_close_slot = self._content.getMovieSlot(SLOT_CLOSE)
        button_close_prototype = PrototypeManager.generateObjectUniqueOnNode(button_close_slot, PROTOTYPE_BUTTON, Size="Close")
        self.buttons[SLOT_CLOSE] = button_close_prototype

        button_back_slot = self._content.getMovieSlot(SLOT_BACK)
        button_back_prototype = PrototypeManager.generateObjectUniqueOnNode(button_back_slot, PROTOTYPE_BUTTON, Size="Back")
        self.buttons[SLOT_BACK] = button_back_prototype

    # - View -----------------------------------------------------------------------------------------------------------

    def _loadContent(self):
        for popup_id, popup_content in PopUpManager.getAllPopUpContents().items():
            self.contents[popup_id] = popup_content
            popup_content.onInitialize(self)
            popup_content.onPreparation()

    def _update(self):
        self._updateContent()
        self._updateActionButton()
        self._updateTitle()

    def _updateContent(self):
        if len(self.object.getParam("OpenPopUps")) == 0:
            return

        current_popup_id = self.object.getParam("OpenPopUps")[-1]
        popup_content = self.contents[current_popup_id]
        if popup_content.isActivated() is False:
            popup_content.onActivate()

    def _updateActionButton(self):
        open_popups = self.object.getParam("OpenPopUps")
        if len(open_popups) <= 1:   # 0, 1
            self.buttons["close"].setEnable(True)
            self.buttons["back"].setEnable(False)
        else:   # 2+
            self.buttons["back"].setEnable(True)
            self.buttons["close"].setEnable(False)

    def _updateTitle(self):
        open_pop_ups = self.object.getParam("OpenPopUps")

        if len(open_pop_ups) == 0:
            return

        current_popup_id = open_pop_ups[-1]
        current_popup_content = self.contents[current_popup_id]
        Mengine.setTextAlias("", POPUP_TITLE_ALIAS, current_popup_content.title_text_id)

    def _setPosition(self):
        _, _, _, _, _, x_center, y_center = AdjustableScreenUtils.getMainSizesExt()

        content_entity = self._content.getEntityNode()
        content_entity.setWorldPosition(Mengine.vec2f(x_center, y_center))

    # - Scopes ---------------------------------------------------------------------------------------------------------

    def _scopeCloseLastContent(self, source):
        open_popups = self.object.getParam("OpenPopUps")
        last_popup_id = open_popups[-1]

        source.addNotify(Notificator.onPopUpClose, last_popup_id)
