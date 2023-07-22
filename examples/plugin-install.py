"""
Example program for checking whether a data source is healthy.

Documentation: https://github.com/panodata/grafana-client/blob/main/examples/datasource-health-check.rst
"""
import json
import logging
import time
import requests
from distutils.version import LooseVersion
from optparse import OptionParser

from grafana_client import GrafanaApi
from grafana_client.util import setup_logging

logger = logging.getLogger(__name__)

VERSION_7 = LooseVersion("7")


def run(grafana: GrafanaApi):
    parser = OptionParser()
    parser.add_option("--uid", dest="uid", help="Data source UID")
    (options, args) = parser.parse_args()
    logger.info("Health check results {}", grafana.plugin.health_check_plugin())
    try:
        logger.info("Plugin UnInstall results {}", grafana.plugin.uninstall_plugins())
    except Exception as e:
        logger.warning("Got exception from uninstall call = {}", e)
    time.sleep(60)
    try:
        logger.info("Plugin Install results {}", grafana.plugin.install_plugins())
    except Exception as e:
        logger.warning("Got exception from install call = {}", e)
    time.sleep(60)
    logger.info("Finished running plugin-install")


def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


def install_plugins(grafana: GrafanaApi):
    plugin_versions = read_json_file("./plugin-build-manifest.json")["plugins"]["versions"]
    for pluginV in plugin_versions:
        logger.info("Installing plugin %s", pluginV["name"])
        try:
            #logger.info("Plugin Install results {}", grafana.plugin.install_plugins(pluginV["name"], pluginV["version"]))
            grafana.plugin.install_plugins(pluginV["name"], pluginV["version"])
        except Exception as e:
            logger.warning("Got exception from install call = {}", e)
        time.sleep(1)

def uninstall_plugins(grafana: GrafanaApi):
    plugin_versions = read_json_file("./plugin-build-manifest.json")["plugins"]["versions"]
    for pluginV in plugin_versions:
        logger.info("UnInstalling plugin %s", pluginV)
        try:
            grafana.plugin.uninstall_plugins(pluginV["name"])
        except Exception as e:
            logger.warning("Got exception from install call = {}", e)
        time.sleep(1)

def install_from_external_plugins(grafana: GrafanaApi):
    plugin_versions = get_json_data()
    for pluginV in plugin_versions:
        logger.info("Installing plugin %s", pluginV["name"])
        if pluginV["internal"] or pluginV["internal"] == "true":
            logger.info("Skipping Internal/Core Plugin ")
            continue
        try:
            #logger.info("Plugin Install results {}", grafana.plugin.install_plugins(pluginV["name"], pluginV["version"]))
            grafana.plugin.install_plugins(pluginV["name"], pluginV["version"])
        except Exception as e:
            logger.warning("Got exception from install call = {}", e)
        time.sleep(1)

def get_json_data():
    response = requests.get("https://grafana.com/api/plugins")
    response.raise_for_status()  # Raise an exception if the request fails (optional)

    # Parse the JSON data from the response
    json_data = response.json()

    plugins = []

    for item in json_data["items"]:
        plugins.append({
            "name": item["slug"],
            "version": item["version"],
            "internal": item["internal"]
        })
    return plugins


def uninstall_from_external_plugins(grafana: GrafanaApi):
    plugin_versions = get_json_data()
    for pluginV in plugin_versions:
        logger.info("UnInstalling plugin %s", pluginV)
        if pluginV["internal"] or pluginV["internal"] == "true":
            logger.info("Skipping Internal/Core Plugin ")
            continue
        try:
            grafana.plugin.uninstall_plugins(pluginV["name"])
        except Exception as e:
            logger.warning("Got exception from install call = {}", e)
        time.sleep(1)

def get_plugins_from_workspace(grafana :GrafanaApi):
    plugins = grafana.plugin.get_plugins()
    for plug in plugins:
        logger.info(" Plugin name = %s, version = %s and signature = %s", plug["name"], plug["info"]["version"], plug["signature"])
    logger.info("Total plugins installed = %s", len(plugins))
def healthcheck(grafana: GrafanaApi):
    print(grafana.plugin.health_check_plugin())

if __name__ == "__main__":
    setup_logging(level=logging.INFO)

    # Connect to Grafana instance and run health check.
    grafana_client = GrafanaApi.from_env()

    # try:
    #     grafana_client.connect()
    # except requests.exceptions.ConnectionError:
    #     logger.exception("Connecting to Grafana failed")
    #     raise SystemExit(1)
    #
    # grafana_version = LooseVersion(grafana_client.version)
    # if grafana_version < VERSION_7:
    #     raise NotImplementedError(f"Data source health check subsystem not ready for Grafana version {grafana_version}")

    #uninstall_from_external_plugins(grafana_client)
    healthcheck(grafana_client)
    #time.sleep(60)
    #install_from_external_plugins(grafana_client)
    get_plugins_from_workspace(grafana_client)
