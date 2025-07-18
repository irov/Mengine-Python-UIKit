class LayoutBoxElementFuncWrapper(object):
    def __init__(self, func_getLayoutSize, func_setLayoutOffset):
        self.func_getLayoutSize = func_getLayoutSize
        self.func_setLayoutOffset = func_setLayoutOffset

    def getLayoutSize(self):
        return self.func_getLayoutSize()

    def setLayoutOffset(self, layout_box, layout_offset, layout_size):
        if self.func_setLayoutOffset is None:
            return
        self.func_setLayoutOffset(layout_box, layout_offset, layout_size)
