#! /usr/bin/env python
# pylint: disable=import-error, line-too-long
"""
Python script to automatically generate grafana dashboards from netdata metrics.

Copyright 2017 Justas Balcas

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
Title 			: netdata-grafana
Author			: Justas Balcas
Email 			: justas.balcas (at) cern.ch
@Copyright		: Copyright (C) 2016 Justas Balcas
Date			: 2017/09/26
"""
import os
import json
import tempfile
import copy
import urllib2
import ConfigParser
from grafana_vars import GRAFANA_DASHBOARD, GRAFANA_PANEL, GRAFANA_ROW
from grafana_vars import GRAFANA_TARGET, GRAFANA_LINKS, FIELD_DESC

# TODO. Allow this to come from configuration, so that user can specify it's own.
MAPPINGS = {'AREA': {'fill': 6, 'stack': False, 'steppedLine': False},
            'LINE': {'fill': 1, 'stack': False, 'steppedLine': False},
            'STACKED': {'fill': 5, 'stack': True, 'steppedLine': True}}

def getConfig(locations):
    """
    Get parsed configuration object.
    Input: list(str,str,str): ['filename1', 'filename2']
    Returns: ConfigParserObject if file is present
             None if file is not present
    Raises: ConfigParser.ParsingError if file formatting is not correct
    """
    tmpCp = ConfigParser.ConfigParser()
    for fileName in locations:
        if os.path.isfile(fileName):
            tmpCp.read(fileName)
            return tmpCp
    return None

def getUnitMapping(unit):
    """
    Map netdata mapping to grafana type.
    Input: str: unit
    Returns: str of mapped grafana unit, if not present in mapping, str(short)
    """
    units = {"kilobits/s": "Kbits",
             "kilobytes/s": "KBs",
             "% of time working": "percent",
             "cpu time %": "percent",
             "percentage": "percent",
             "KB": "deckbytes",
             "MB": "decmbytes",
             "GB": "decgbytes",
             "seconds": "s",
             "backlog (ms)": "ms",
             "operations/s": "ops"}
    if unit in units:
        return units[unit]
    return 'short'

def getDataFromUrl(url):
    """
    Get data from specified url
    Input: str: url
    Returns: response socket object
    Raises: Might raise urllib2 exception associated with failing connection
    """
    response = urllib2.urlopen(url)
    return response

def prepareGrafanaTarget(inName, inDict, config):
    """
    Prepare Grafana Target
    Input: str: inName : name of the group metric
           dict: inDict : group metric config from netdata
           dict: config : all configuration parameters
    Returns: list: list of generated targets
    """
    refIDs = [chr(i) for i in xrange(ord('A'), ord('Z') + 1)]
    tmpTargets = []
    for dimensionKey, dimensionDict in inDict['dimensions'].items():
        # TODO. Look at grafana doc if we can have more of these dimensions
        if not refIDs:
            print 'skip', dimensionKey, inName
            continue
        tmpTarget = copy.deepcopy(GRAFANA_TARGET)
        tmpTarget['alias'] = dimensionDict['name']
        tmpTarget['refId'] = refIDs[0]
        refIDs = list(refIDs[1:])
        valKey = ""
        if config['dimensionids']:
            valKey = dimensionKey
        else:
            valKey = dimensionDict['name']
        tmpTarget['measurement'] = "%s.%s.%s.%s" % (config['prefix'], config['section'], inDict['name'], valKey)
        tmpTargets.append(tmpTarget)
    return tmpTargets

def prepareGrafanaPanel(inName, inDict, config):
    """
    Make grafana Panel
    Input: str: inName : name of the group metric
           dict: inDict : group metric config from netdata
           dict: config : all configuration parameters
    Returns: list: list of generated panels
    """
    panelID = 1
    tmpPanels = []
    # First panel is description if there is one...
    if inName in FIELD_DESC and 'title' in FIELD_DESC[inName] and 'info' in FIELD_DESC[inName]:
        tmpPanels.append({"content": FIELD_DESC[inName]['info'],
                          "height": "20px",
                          "id": panelID,
                          "links": [],
                          "mode": "html",
                          "span": 12,
                          "title": FIELD_DESC[inName]['title'],
                          "type": "text"})
        panelID += 1
    for panel in inDict:
        tmpPanel = copy.deepcopy(GRAFANA_PANEL)
        tmpPanel['title'] = panel['title']
        tmpPanel['id'] = panelID
        tmpPanel['datasource'] = config['datasource']
        panelID += 1
        unitMapping = getUnitMapping(panel['units'])
        tmpPanel['yaxes'][0]['format'] = unitMapping
        tmpPanel['yaxes'][0]['label'] = panel['units']
        for repKey, repVal in MAPPINGS[panel['chart_type'].upper()].items():
            tmpPanel[repKey] = repVal
        tmpTargets = prepareGrafanaTarget(inName, panel, config)
        for item in tmpTargets:
            tmpPanel['targets'].append(item)
        tmpPanels.append(tmpPanel)
    return tmpPanels

def prepareGrafanaRow(inName, inDict, config):
    """
    Make Grafana Row
    Input: str: inName : name of the group metric
           dict: inDict : group metric config from netdata
           dict: config : all configuration parameters
    Returns: list: list of generated rows
    """
    tmpRow = copy.deepcopy(GRAFANA_ROW)
    try:
        tmpRow['title'] = FIELD_DESC[inName]['title']
    except KeyError:
        tmpRow['title'] = inName.title()
    tmpPanels = prepareGrafanaPanel(inName, inDict, config)
    for item in tmpPanels:
        tmpRow['panels'].append(item)
    return tmpRow

def prepareDashboard(config):
    """
    Prepare dashboard for specific host
    Input: dict: config : all configuration parameters
    Returns: None
    """
    netdataIn = json.load(getDataFromUrl('%s/api/v1/charts' % config['hostname']))
    tmpOut = {}
    if 'charts' in netdataIn.keys():
        for _chartName, chartDict in netdataIn['charts'].items():
            tmpRowOut = tmpOut.setdefault(chartDict['type'], [])
            tmpRowOut.append(chartDict)
    newDash = copy.deepcopy(GRAFANA_DASHBOARD)
    newDash['description'] = "Dashboard for %s" % config['hostname']
    newDash['title'] = config['section']
    if 'tags' in config:
        print config
        newDash['tags'] = config['tags']
    newLink = copy.deepcopy(GRAFANA_LINKS)
    newLink['tooltip'] = "Open Real Time Netdata monitoring"
    newLink['title'] = "Netdata - Real Time Monitoring"
    newLink['url'] = config['hostname']
    newDash['links'].append(newLink)
    # Start with FIELD_DESC keys as important ones.
    for key in config['order']:
        if key in tmpOut.keys():
            newRow = prepareGrafanaRow(key, tmpOut[key], config)
            newDash['rows'].append(newRow)
            del tmpOut[key]
    if not config['skipOthers']:
        for key in tmpOut.keys():
            newRow = prepareGrafanaRow(key, tmpOut[key], config)
            newDash['rows'].append(newRow)
    with open('%s.json' % config['section'], 'w') as fd:
        fd.write(json.dumps(newDash, sort_keys=True, indent=2, separators=(',', ': ')))
    return


def getNetdataConfig(hostname):
    """
    Get netdata server config and also check backend configuration
    Input: str: hostname : url with protocol and port
    Returns: boolean: True - success in getting config and all parameters defined correctly.
                      False - Failure in retrieving one or another configuration parameters.
             dict: {} - if boolean return is False, always empty as failed to retrieve.
                   otherwise dictionary of all parsed configuration parameters
    """
    # TODO look at netdata filters, and ignore which are not published to Database
    try:
        tmpConf = getDataFromUrl("%s/netdata.conf" % hostname)
    except urllib2.URLError as ex:
        print 'Received URLError %s for %s. Ignoring this node check' % (ex, hostname)
        return False, {}
    tempfileName = ""
    outDict = {}
    with tempfile.NamedTemporaryFile(delete=False) as fd:
        for line in tmpConf.read().splitlines():
            fd.write(line.replace('\t', '') + "\n")
        tempfileName = fd.name
    hostConfig = getConfig([tempfileName])
    if not hostConfig.has_section('backend'):
        print 'Hostname %s Netdata server is not configured to publish anything to any backend' % hostname
        print '* Skipping this node check.'
        return False, {}
    if not hostConfig.has_option('backend', 'enabled'):
        print 'Hostname %s Netdata does not have enabled option in backend configuration' % hostname
        print '* Skipping this node check.'
        return False, {}
    if not hostConfig.has_option('backend', 'destination'):
        print 'Hostname %s Netdata is configured to send metrics but destination is not set.' % hostname
        print '* Skipping this node check.'
        return False, {}
    if not hostConfig.has_option('backend', 'prefix'):
        outDict['prefix'] = 'netdata'
    for optionKey in hostConfig.options('backend'):
        outDict[optionKey] = hostConfig.get('backend', optionKey)
    print outDict
    # Make boolean from send names instead of ids
    if 'send names instead of ids' in outDict:
        if outDict['send names instead of ids'] == 'yes':
            outDict['dimensionids'] = True
        elif outDict['send names instead of ids'] == 'no':
            outDict['dimensionids'] = False
        else:
            outDict['dimensionids'] = True
    else:
        outDict['dimensionids'] = False
        outDict['send names instead of ids'] = 'no'
    return True, outDict

def main():
    """
    Main execution. For all config specified netdata hosts, prepare grafana dashboard template.
    Input: None
    Returns: None
    """
    # TODO. Allow to specify configuration location.
    mainConfig = getConfig(['netdata-grafana-hosts.conf'])
    for sectionName in mainConfig.sections():
        # check if mandatory options are in place
        if not(mainConfig.has_option(sectionName, 'hostname') and
               mainConfig.get(sectionName, 'hostname')):
            print 'In section %s hostname is not defined. It is mandatory to define full url' % sectionName
            print '* Skipping this node check.'
            continue
        elif not(mainConfig.has_option(sectionName, 'datasource') and
                 mainConfig.get(sectionName, 'datasource')):
            print 'In section %s hostname is not defined. It is mandatory to define full url' % sectionName
            print '* Skipping this node check.'
            continue
        configSuccess, config = getNetdataConfig(mainConfig.get(sectionName, 'hostname'))
        if not configSuccess:
            continue
        if mainConfig.has_option(sectionName, 'tags') and mainConfig.get(sectionName, 'tags'):
            config['tags'] = mainConfig.get(sectionName, 'tags').split(',')
        config['datasource'] = mainConfig.get(sectionName, 'datasource')
        config['hostname'] = mainConfig.get(sectionName, 'hostname')
        config['section'] = sectionName
        if mainConfig.has_option(sectionName, 'order') and mainConfig.get(sectionName, 'order'):
            config['order'] = mainConfig.get(sectionName, 'order').split(',')
        else:
            config['order'] = ['system', 'mem', 'cpu', 'disk', 'net', 'ipv4', 'ipv6',
                               'netfilter', 'apps', 'users', 'groups', 'services', 'tc']
        if mainConfig.has_option(sectionName, 'skipOthers') and mainConfig.get(sectionName, 'skipOthers'):
            config['skipOthers'] = mainConfig.getboolean(sectionName, 'skipOthers')
        prepareDashboard(config)

if __name__ == '__main__':
    main()
