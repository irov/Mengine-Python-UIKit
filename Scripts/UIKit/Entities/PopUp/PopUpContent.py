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

    def setupObjectsSlotsAsTable(self, objects_list):
        """
        objects_list = [
            dict_1 = {
                slot_name_1: object_1,
                slot_name_2: object_2,
                ...
            },
            dict_2 = {
                slot_name_1: object_1,
                ...
            },
            ...
        ]
        """

        # prepare variables
        content_size = self.pop_up_base.getContentSize()
        start_pos = Mengine.vec2f(0, 0)
        start_pos -= content_size / 2

        # setup objects between each other
        current_size_y = 0
        objects_len_y = len(objects_list)
        for row in objects_list:

            current_size_x = 0
            maximum_size_y = 0

            for key, obj in row.items():
                obj_pos = obj.getLocalPosition()
                obj_pos += start_pos

                obj_size = obj.getSize()
                obj_pos += obj_size / 2

                obj_pos.x += current_size_x
                obj_pos.y += current_size_y

                obj_slot = self.content.getMovieSlot(key)
                obj_slot.setLocalPosition(obj_pos)

                current_size_x += obj_size.x
                if maximum_size_y < obj_size.y:
                    maximum_size_y = obj_size.y

            current_size_y += maximum_size_y

        # calc offset y
        available_space_y = content_size.y - current_size_y
        offset_y = available_space_y / (objects_len_y + 1)

        # adding offsets between objects
        for y, row in enumerate(objects_list):
            current_size_x = 0
            objects_len_x = len(row.items())

            # add offset y
            for key, obj in row.items():
                old_pos = obj.getLocalPosition()
                new_pos = Mengine.vec2f(old_pos.x, old_pos.y + offset_y * (y + 1))
                obj.setLocalPosition(new_pos)

                obj_size = obj.getSize()
                current_size_x += obj_size.x

            # calc offset x
            available_space_x = content_size.x - current_size_x
            offset_x = available_space_x / (objects_len_x + 1)

            # add offset x
            for x, (key, obj) in enumerate(row.items()):
                old_pos = obj.getLocalPosition()
                new_pos = Mengine.vec2f(old_pos.x + offset_x * (x + 1), old_pos.y)
                obj.setLocalPosition(new_pos)
