from .base import Base
import logging

class Plugin(Base):
    def __init__(self, client):
        super(Plugin, self).__init__(client)
        self.client = client
        self.logger = logging.getLogger(__name__)
    def health_check_plugin(self):
        """

        :return:
        """
        path = "/healthz"
        r = self.client.GET(path)
        return r

    def get_plugins(self):
        """

        :return:
        """
        path = "/api/plugins?embedded=0"
        r = self.client.GET(path)
        return r

    def install_plugins(self, pluginId, version):
        """
        : return:
        """
        try:
            path = "/api/plugins/%s/install" % pluginId
            r = self.client.POST(path, json={"version": version})
            return r
        except Exception as ex:
            self.logger.info("Skipped installing %s and err = %s", pluginId, ex)
        return None

    def uninstall_plugins(self, pluginId):
        """
        : return:
        """
        try:
            path = "/api/plugins/%s/uninstall" % pluginId
            r = self.client.POST(path)
            return r
        except Exception as ex:
            self.logger.info("Skipped uninstalling %s and error = %s", pluginId, ex)
        return None
    def get_plugin_metrics(self, pluginId):
        try:
            path = "/api/plugins/%s/metrics" % pluginId
            r = self.client.GET(path)
            return r
        except Exception as ex:
            self.logger.info("Got error in fetching metrics for plugin %s and error = %s", pluginId, ex)
        return None
