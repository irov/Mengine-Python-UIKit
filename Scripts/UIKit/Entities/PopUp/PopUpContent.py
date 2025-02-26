from Foundation.Initializer import Initializer
from Foundation.TaskManager import TaskManager


class PopUpContent(Initializer):
    popup_id = ""
    title_text_id = ""
    content_movie_name = ""

    def __init__(self):
        super(PopUpContent, self).__init__()
        self.pop_up_base = None
        self.content = None
        self.tcs = []

    # - Initializer ----------------------------------------------------------------------------------------------------

    def _onInitialize(self, pop_up_base):
        super(PopUpContent, self)._onInitialize()
        self.pop_up_base = pop_up_base

        if self.__setupContent() is False:
            return False

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

        if self.content is not None:
            self.content.onDestroy()
            self.content = None

        self.pop_up_base = None

    def _onFinalizeContent(self):
        print "_finalizeContent", self.popup_id
        pass

    # - Content --------------------------------------------------------------------------------------------------------

    def __setupContent(self):
        self.content = self.pop_up_base.object.generateObjectUnique(self.content_movie_name, self.content_movie_name)
        if self.content is None:
            Trace.log("PopUp", 0, "Not found {!r} in {!r}".format(self.content_movie_name, self.pop_up_base.getName()))
            return False

        self.content.setEnable(True)

        return True

    # - Tools ----------------------------------------------------------------------------------------------------------

    def attachTo(self, node):
        content_node = self.content.getEntityNode()
        content_node.removeFromParent()
        node.addChild(content_node)

    def getNode(self):
        content_node = self.content.getEntityNode()
        return content_node

    def _createTaskChain(self, name, **params):
        tc = TaskManager.createTaskChain(Name=self.__class__.__name__+"_"+name, **params)
        self.tcs.append(tc)
        return tc
