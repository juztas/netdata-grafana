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
import json
import copy
from common import getDataFromUrl
from common import getUnitMapping
from grafana_vars import MAPPINGS
from grafana_vars import FIELD_DESC
from grafana_vars import GRAFANA_ROW
from grafana_vars import GRAFANA_PANEL
from grafana_vars import GRAFANA_LINKS
from grafana_vars import GRAFANA_TARGET_GRAPHITE
from grafana_vars import GRAFANA_DASHBOARD

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
            print 'skip', dimensionKey, inName, dimensionDict
            continue
        tmpTarget = copy.deepcopy(GRAFANA_TARGET_GRAPHITE)
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

def start(config):
    """
    Go through all list of HOSTs and prepare dashboards for each;
    Input: dict: config : all configuration parameters
    Returns: None
    """
    for hostName, hostConf in config["HOSTS"].items():
        print 'Preparing Dashboard for %s' % hostName
        prepareDashboard(hostConf)
