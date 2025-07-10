class LayoutWrapper(object):
    class SpriteWrapper:
        def __init__(self, sprite):
            self.sprite = sprite

        def getSpriteSize(self):
            sprite_size_unscaled = self.sprite.getSurfaceSize()
            sprite_scale = self.sprite.getScale()
            sprite_size = (sprite_size_unscaled.x * sprite_scale.x, sprite_size_unscaled.y * sprite_scale.y)
            return sprite_size

        def getLayoutSize(self):
            return self.getSpriteSize()

        def setLayoutOffset(self, layout_box, layout_offset, layout_size):
            layout_box_width, layout_box_height = layout_box.getSize()
            sprite_size = self.getSpriteSize()
            self.sprite.setLocalPosition((
                layout_offset[0] + layout_size[0] / 2 - layout_box_width / 2 - sprite_size[0] / 2,
                layout_offset[1] + layout_size[1] / 2 - layout_box_height / 2 - sprite_size[1] / 2
            ))

    class TextWrapper:
        def __init__(self, text):
            self.text = text

        def getTextSize(self):
            text_size = self.text.getTextSize()
            return (text_size.x, text_size.y)

        def getLayoutSize(self):
            return self.getTextSize()

        def setLayoutOffset(self, layout_box, layout_offset, layout_size):
            layout_box_width, layout_box_height = layout_box.getSize()
            self.text.setLocalPosition((
                layout_offset[0] + layout_size[0] / 2 - layout_box_width / 2,
                layout_offset[1] + layout_size[1] / 2 - layout_box_height / 2
            ))

