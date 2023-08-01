"""
Example program for checking whether a data source is healthy.

Documentation: https://github.com/panodata/grafana-client/blob/main/examples/datasource-health-check.rst
"""
import json
import logging
import random
import os
import time
import requests
from distutils.version import LooseVersion
from optparse import OptionParser

from grafana_client import GrafanaApi
from grafana_client.util import setup_logging
from prometheus_client.parser import text_string_to_metric_families

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


def install_plugins_from_amg_file(grafana: GrafanaApi):
    plugin_versions = read_json_file("./amg-plugins.json")
    for pluginV in plugin_versions:
        logger.info("Installing plugin %s", pluginV["id"])
        if pluginV["signature"] == "internal":
            logger.info("Skipping Internal/Core Plugin ")
            continue
        try:
            #logger.info("Plugin Install results {}", grafana.plugin.install_plugins(pluginV["name"], pluginV["version"]))
            grafana.plugin.install_plugins(pluginV["id"], pluginV["info"]["version"])
        except Exception as e:
            logger.warning("Got exception from install call = {}", e)
        time.sleep(1)

def uninstall_plugins_from_amg_file(grafana: GrafanaApi):
    plugin_versions = read_json_file("./amg-plugins.json")
    for pluginV in plugin_versions:
        logger.info("UnInstalling plugin %s", pluginV)
        try:
            grafana.plugin.uninstall_plugins(pluginV["id"])
        except Exception as e:
            logger.warning("Got exception from install call = {}", e)
        time.sleep(1)

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

def filter_by_attributes_inclusion_exclusion(items, attributes_to_include, attributes_to_exclude):
    filtered_items = items
    if attributes_to_include:
        for attribute, values in attributes_to_include.items():
            filtered_items = [item for item in filtered_items if item.get(attribute) in values]
    if attributes_to_exclude:
        for attribute, values in attributes_to_exclude.items():
            filtered_items = [item for item in filtered_items if item.get(attribute) not in values]
    return filtered_items

def install_from_external_plugins(grafana: GrafanaApi, attributes_to_include, attributes_to_exclude, total_plugins):
    plugin_versions = get_json_data()
    # plugin_versions = filter_by_type(plugin_versions, plugin_types)
    plugin_versions = filter_by_attributes_inclusion_exclusion(plugin_versions, attributes_to_include, attributes_to_exclude)
    print("Total plugins before shuffle " + str(len(plugin_versions)))
    plugin_versions = select_items_with_fair_probability(plugin_versions, total_plugins)
    print("Total plugins after shuffle " + str(len(plugin_versions)))
    for pluginV in plugin_versions:
        print(pluginV)
    #     logger.info("Installing plugin %s", pluginV["name"])
    #     # if pluginV["internal"] or pluginV["internal"] == "true":
    #     #     logger.info("Skipping Internal/Core Plugin ")
    #     #     continue
    #     try:
    #         #logger.info("Plugin Install results {}", grafana.plugin.install_plugins(pluginV["name"], pluginV["version"]))
    #         grafana.plugin.install_plugins(pluginV["name"], pluginV["version"])
    #     except Exception as e:
    #         logger.warning("Got exception from install call = {}", e)
    #     time.sleep(1)

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
            "internal": item["internal"],
            "typeCode": item["typeCode"]
        })
    return plugins


def uninstall_from_external_plugins(grafana: GrafanaApi, attributes_to_include, attributes_to_exclude):
    plugin_versions = get_json_data()
    plugin_versions = filter_by_attributes_inclusion_exclusion(plugin_versions, attributes_to_include, attributes_to_exclude)
    for pluginV in plugin_versions:
        logger.info("UnInstalling plugin %s", pluginV)
        # if pluginV["internal"] or pluginV["internal"] == "true":
        #     logger.info("Skipping Internal/Core Plugin ")
        #     continue
        # if pluginV["typeCode"] not in plugin_types:
        #     continue
        try:
            grafana.plugin.uninstall_plugins(pluginV["name"])
        except Exception as e:
            logger.warning("Got exception from install call = {}", e)
        time.sleep(1)

def write_json_to_file(json_data, output_file):
    with open(output_file, 'w') as file:
        json.dump(json_data, file, indent=4)
def get_plugins_from_workspace(grafana :GrafanaApi):
    plugins = grafana.plugin.get_plugins()
    pluginsMap = {}
    pluginIds = []
    for plug in plugins:
        key = plug["type"] + "-" + plug["signature"]
        if key in pluginsMap.keys():
            pluginsMap[key].append(plug["id"])
        else:
            pluginsMap[key] = []
            pluginsMap[key].append(plug["id"])
        #logger.info(" Plugin name = %s, Id= %s, version = %s and signature = %s", plug["name"], plug["id"], plug["info"]["version"], plug["signature"])
    #logger.info("Total plugins installed = %s", len(plugins))
    plugins = grafana.plugin.get_plugins()
    logger.info("Total plugins installed = %s", len(plugins))
    internal = []
    for plugin in plugins:
        pluginIds.append(plugin["id"])
        if plugin["signature"] == 'internal':
            internal.append(plugin)
            continue
        if plugin["type"] == "panel":
            continue
        #pluginIds.append(plugin["id"])
        # if plugin["id"] not in pluginsMap.keys():
        #     logger.info("Plugin diff = %s", plugin["id"])
    logger.info("Internal plugins = %s", len(internal))
    logger.info("Total non core plugins = %s", len(plugins) - len(internal))
    for k, v in pluginsMap.items():
        logger.info("Plugin type = %s and count = %s", k, len(v))
    write_json_to_file(plugins, 'external-plugins-all.json')
    return pluginIds
    #logger.info("non Internal plugin = %s", nonInternal)

def get_plugin_metrics(grafana :GrafanaApi, plugins):
    allMetrics = {}
    #logger.info(" All Metrics = %s", metrics)
    for pluginId in plugins:
        metrics = grafana.plugin.get_plugin_metrics(pluginId)
        print("Plugin Id metrics " + pluginId)
        allMetrics[pluginId] = []
        for family in text_string_to_metric_families(metrics):
            for sample in family.samples:
                #print(*sample)
                #print("Name: {0} Labels: {1} Value: {2}".format(*sample))
                name = "{0}".format(*sample)
                if name == 'process_open_fds':
                    #print("Name: {0} Labels: {1} Value: {2}".format(*sample))
                    pluginMetric = {
                        "Name": 'process_open_fds',
                        "Value": "{2}".format(*sample)
                    }
                    allMetrics[pluginId].append(pluginMetric)
                elif name == 'process_max_fds':
                    #print("Name: {0} Labels: {1} Value: {2}".format(*sample))
                    pluginMetric = {
                        "Name": 'process_max_fds',
                        "Value": "{2}".format(*sample)
                    }
                    allMetrics[pluginId].append(pluginMetric)
    #         if len(pluginMetrics) == 2:
    #             allMetrics[pluginId] = pluginMetrics
    for k, v in allMetrics.items():
         print(" {} = {}".format(k,v))
    return allMetrics

def filter_by_type(items, type_codes_to_filter):
    return [item for item in items if item.get("typeCode") in type_codes_to_filter]

def select_items_with_fair_probability(items, num_items_to_select):
    if num_items_to_select > len(items):
        raise ValueError("Number of items to select exceeds the length of the list.")

    # Shuffle the items to ensure a random order
    random.shuffle(items)

    # Return the first num_items_to_select elements from the shuffled list
    return items[:num_items_to_select]

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

    #uninstall_from_external_plugins(grafana_client, {"typeCode": ["app", "datasource"]}, {"internal": [True]})
    #uninstall_plugins(grafana_client)
    healthcheck(grafana_client)
    #time.sleep(60)
    #install_from_external_plugins(grafana_client, {"typeCode": ["app", "datasource"]}, {"internal": [True]}, 100)
    #install_plugins_from_amg_file(grafana_client)
    #time.sleep(60)
    pluginsIds = get_plugins_from_workspace(grafana_client)
    #get_plugin_metrics(grafana_client, pluginsIds)
