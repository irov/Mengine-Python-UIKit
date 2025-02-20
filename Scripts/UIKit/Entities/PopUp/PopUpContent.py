from Foundation.Initializer import Initializer
from Foundation.TaskManager import TaskManager


class PopUpContent(Initializer):
    popup_id = ""
    title_text_id = ""
    content_movie_name = ""

    def __init__(self):
        super(PopUpContent, self).__init__()
        self.root = None
        self.pop_up_base = None
        self.content = None
        self.tcs = []

    # - Initializer ----------------------------------------------------------------------------------------------------

    def _onInitialize(self, pop_up_base):
        super(PopUpContent, self)._onInitialize()
        self.pop_up_base = pop_up_base

        self.content = self.pop_up_base.object.getObject(self.content_movie_name)
        if self.content is None:
            Trace.log("PopUp", 0, "Not found {!r} in {!r}".format(self.content_movie_name, self.pop_up_base.getName()))
            return False

        self.__setupRoot()
        self.__setupContent()

        self._onInitializeContent()

    def _onInitializeContent(self):
        print "_initializeContent", self.popup_id
        pass

    def _onFinalize(self):
        super(PopUpContent, self)._onFinalize()

        for tc in self.tcs:
            tc.cancel()
        self.tcs = []

        self._onFinalizeContent()

        if self.root is not None:
            Mengine.destroyNode(self.root)
            self.root = None

        self.content = None
        self.pop_up_base = None

    def _onFinalizeContent(self):
        print "_finalizeContent", self.popup_id
        pass

    # - Root -----------------------------------------------------------------------------------------------------------

    def __setupRoot(self):
        self.root = Mengine.createNode("Interender")
        self.root.setName(self.__class__.__name__)

    # - Setup Content --------------------------------------------------------------------------------------------------

    def __setupContent(self):
        self.pop_up_base.attachChild(self.root)
        content_node = self.content.getEntityNode()
        self.root.addChild(content_node)

    def _createTaskChain(self, name, **params):
        tc = TaskManager.createTaskChain(Name=self.__class__.__name__+"_"+name, **params)
        self.tcs.append(tc)
        return tc
