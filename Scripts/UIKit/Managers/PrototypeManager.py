from Foundation.GroupManager import GroupManager
from Foundation.DatabaseManager import DatabaseManager
from UIKit.Managers.IconManager import IconManager
from UIKit.Managers.PrototypeContainer import PrototypeContainer


class PrototypeManager(object):
    s_group = "UIStore"
    s_db_module = "Database"
    s_db_name = "Prototypes"

    @staticmethod
    def _generateObjectUnique(prototype_name, object_name, **params):
        if GroupManager.hasPrototype(PrototypeManager.s_group, prototype_name) is False:
            Trace.log("Manager", 0, "Not found prototype {!r} in {!r}".format(prototype_name, PrototypeManager.s_group))
            return

        movie = GroupManager.generateObjectUnique(
            object_name,
            PrototypeManager.s_group,
            prototype_name,
            **params
        )
        return movie

    @staticmethod
    def generateObjectUniqueOnNode(node, name, object_name=None, **params):
        """ **params: Size, Color
            :returns: Object (default)
         """
        container = PrototypeManager.generateObjectContainerOnNode(node, name, object_name, **params)
        if container is not None:
            return container.movie
        return None

    @staticmethod
    def generateObjectContainerOnNode(node, name, object_name=None, **params):
        """ **params: Size, Color
            :returns: ObjectContainer ( contains movie and icon (optional) )
         """
        container = PrototypeManager.generateObjectContainer(name, object_name, **params)

        if container is None:
            return None

        entity_node = container.movie.getEntityNode()
        node.addChild(entity_node)

        return container

    @staticmethod
    def generateObjectUnique(name, object_name=None, **params):
        """ **params: Size, Color
            :returns: Object (default)
         """
        container = PrototypeManager.generateObjectContainer(name, object_name, **params)
        if container is not None:
            return container.movie
        return None

    @staticmethod
    def generateObjectContainer(name, object_name=None, **params):
        """ **params: Size, Color
            :returns: ObjectContainer ( contains movie and icon (optional) )
         """

        db = DatabaseManager.getDatabase(
            PrototypeManager.s_db_module,
            PrototypeManager.s_db_name
        )
        if db is None:
            return None

        params_orm = DatabaseManager.findDB(db, Name=name, **params)
        if params_orm is None:
            Trace.log("Manager", 0, "Not found Name={!r} in db {!r}".format(name, PrototypeManager.s_db_name))
            return None

        if object_name is None:
            object_name = params_orm.ObjectName

        object_unique = PrototypeManager._generateObjectUnique(params_orm.Prototype, object_name)
        if object_unique is None:
            return None

        icon = None
        param_prototype = params_orm.Icon.get("Prototype")
        param_size = params_orm.Icon.get("Size")
        param_slot = params_orm.Icon.get("Slot")

        if param_prototype is not None:
            icon = IconManager.generateIcon(param_prototype, param_size)
            icon_node = icon.getEntityNode()
            object_type = object_unique.getType()

            if object_type in ["ObjectMovie2Button", "ObjectMovie2CheckBox"]:
                object_unique.addChildToSlot(icon_node, param_slot)
            elif object_type in ["ObjectMovie2"]:
                slot = object_unique.getMovieSlot(param_slot)
                slot.addChild(icon_node)

        container = PrototypeContainer(object_unique, icon)
        return container
