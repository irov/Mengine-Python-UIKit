from Foundation.DemonManager import DemonManager
from Foundation.Providers.AdvertisementProvider import AdvertisementProvider


class AdjustableScreenUtils(object):
    __headers = []

    @staticmethod
    def registerHeaders(headers):
        """ What demons should we check as Header in future calculations.
            Use this function in framework's onInitialize.
        """
        diff = set(headers) - set(AdjustableScreenUtils.__headers)
        AdjustableScreenUtils.__headers.extend(diff)

        def _checkNewHeaders():
            for demon_name in diff:
                if DemonManager.hasDemon(demon_name) is False:
                    Trace.log("Utils", 0, "AdjustableScreenUtils: Registered Header demon {!r} "
                                          "not found in DemonManager!".format(demon_name))
            return True

        Notification.addObserver(Notificator.onRun, _checkNewHeaders)

    @staticmethod
    def getGameWidth():
        viewport = Mengine.getGameViewport()
        width = viewport.end.x - viewport.begin.x
        return width

    @staticmethod
    def getGameHeight():
        viewport = Mengine.getGameViewport()
        height = viewport.end.y - viewport.begin.y
        return height

    @staticmethod
    def getPhoneAdaptiveBannerHeight(width):
        """ Applovin Banners are automatically sized to 320x50 on phones """
        height = 50.0 * width / 320.0
        return height

    @staticmethod
    def getTabletAdaptiveBannerHeight(width):
        """ Applovin Banners are automatically sized to 728x90 on tablets """
        height = 90.0 * width / 728.0
        return height

    @staticmethod
    def getHeaderHeight():
        for header_name in AdjustableScreenUtils.__headers:
            if DemonManager.hasDemon(header_name) is False:
                continue

            demon = DemonManager.getDemon(header_name)
            if demon.isActive() is True:
                return demon.getHeight()

        return 0.0

    @staticmethod
    def getHeaderSize():
        """ :returns: header_width, header_height """
        header_size = Mengine.vec2f(0.0, 0.0)

        for header_name in AdjustableScreenUtils.__headers:
            if DemonManager.hasDemon(header_name) is False:
                continue

            demon = DemonManager.getDemon(header_name)
            if demon.isActive() is True:
                header_size = demon.getSize()
                break

        return header_size

    @staticmethod
    def getBannerHeight():
        game_width = AdjustableScreenUtils.getGameWidth()

        if Mengine.hasOption("ignorebanner") is True:
            banner_height = 0.0
        else:
            banner_height = AdvertisementProvider.getBannerHeight()
            if banner_height is None:
                banner_height = AdjustableScreenUtils.getPhoneAdaptiveBannerHeight(game_width)

        return banner_height

    @staticmethod
    def getActualBannerHeight():
        return AdvertisementProvider.getBannerHeight()

    @staticmethod
    def getActualBannerWidth():
        return AdvertisementProvider.getBannerWidth()

    @staticmethod
    def getMainSizes():
        """ :returns: game_width, game_height, header_height, banner_height """
        game_width = AdjustableScreenUtils.getGameWidth()
        game_height = AdjustableScreenUtils.getGameHeight()
        header_height = AdjustableScreenUtils.getHeaderHeight()
        banner_height = AdjustableScreenUtils.getBannerHeight()

        return game_width, game_height, header_height, banner_height

    @staticmethod
    def getMainSizesExt():
        """ :returns: game_width, game_height, header_height, banner_height, viewport, x_center, y_center """
        game_width, game_height, header_height, banner_height = AdjustableScreenUtils.getMainSizes()
        viewport = Mengine.getGameViewport()
        x_center = viewport.begin.x + game_width / 2
        y_center = viewport.begin.y + game_height / 2

        return game_width, game_height, header_height, banner_height, viewport, x_center, y_center

    @staticmethod
    def getGameCenter():
        """ :returns: x_center, y_center """
        game_width = AdjustableScreenUtils.getGameWidth()
        game_height = AdjustableScreenUtils.getGameHeight()
        viewport = Mengine.getGameViewport()
        x_center = viewport.begin.x + game_width / 2
        y_center = viewport.begin.y + game_height / 2

        return Mengine.vec2f(x_center, y_center)
