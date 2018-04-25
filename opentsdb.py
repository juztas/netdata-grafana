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
import sys
import json
import copy
import importlib
import modifiers
from common import getDataFromUrl
from common import getUnitMapping
from grafana_vars import MAPPINGS
from grafana_vars import FIELD_DESC
from grafana_vars import GRAFANA_ROW
from grafana_vars import GRAFANA_PANEL
from grafana_vars import GRAFANA_LINKS
from grafana_vars import GRAFANA_DASHBOARD
from grafana_vars import GRAFANA_TEMPLATE
from grafana_vars import GRAFANA_TEMPLATE_OPTION
from grafana_vars import GRAFANA_TARGET_OPENTSDB
from grafana_vars import GRAFANA_OPENTSDB_FILTER



def modifierCheck(sectionName, chartName, charts):
    if '__all__' in dir(modifiers):
        if sectionName in modifiers.__all__:
            try:
                method = importlib.import_module("modifiers.%s" % sectionName)
                if hasattr(method, 'CONFIG'):
                    tmpConf = method.CONFIG
                else:
                    print 'Plugin does not have CONFIG defined, which has to have all charts inside. No changes are made'
                    return charts
                if chartName not in tmpConf:
                    print 'Configuration exists, but chart name not. Not applying any changes.'
                    return charts
                tmp = method.start(sectionName, chartName, charts)
                return tmp
            except:
                excType, excValue = sys.exc_info()[:2]
                print "errorType", str(excType.__name__), str(excValue)
                raise
        return charts


def prepareGrafanaTarget(inName, inDict, config):
    """
    Prepare Grafana Target
    Input: str: inName : name of the group metric
           dict: inDict : group metric config from netdata
           dict: config : all configuration parameters
    Returns: list: list of generated targets
    """
    refIDs = [chr(i) for i in xrange(ord('A'), ord('Z') + 1)]
    # refIDs = [x for x in range(100)] You can change and use any number of range... TODO: config...
    tmpTargets = []
    print inDict
    for dimensionKey, dimensionDict in inDict['dimensions'].items():
        # TODO. Look at grafana doc if we can have more of these dimensions
        if not refIDs:
            print 'skip', dimensionKey, inName
            continue
        tmpTarget = copy.deepcopy(GRAFANA_TARGET_OPENTSDB)
        tmpTarget['refId'] = refIDs[0]
        refIDs = list(refIDs[1:])
        valKey = ""
        if config['opentsdb']['dimensionids']:
            valKey = dimensionKey
        else:
            valKey = dimensionDict['name']
        tmpTarget['metric'] = "%s.%s.%s" % (config['opentsdb']['prefix'], inDict['name'], valKey)
        tmpTarget['alias'] = '%s $tag_hostname' % dimensionDict['name'].title()
        # This is for new OPENTSDBs. New one uses Filters
        tmpFilter = copy.deepcopy(GRAFANA_OPENTSDB_FILTER)
        tmpFilter['filter'] = "$HOSTNAME"
        tmpFilter['tagk'] = "hostname"
        tmpFilter['groupBy'] = True
        tmpTarget['filters'].append(tmpFilter)
        if config['opentsdb']['customfilters']:
            for keyFilter in config['opentsdb']['customfilters'].keys():
                tmpFilter = copy.deepcopy(GRAFANA_OPENTSDB_FILTER)
                tmpFilter['filter'] = "$%s" % keyFilter
                tmpFilter['tagk'] = keyFilter.lower()
                tmpTarget['filters'].append(tmpFilter)
        # This is for older opentsdbs.
        #tmpTarget["tags"]["hostname"] = "$HOSTNAME"
        #if config['opentsdb']['customfilters']:
        #    for keyFilter in config['opentsdb']['customfilters'].keys():
        #        tmpTarget["tags"][keyFilter.lower()] = "$%s" % keyFilter
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
    allprios = inDict.keys()
    allprios.sort()
    for prio in allprios:
        # we want to modify all panels here:
        allPanels = {}
        allPanels.setdefault(prio, {})
        for panel, panelDict in inDict[prio].items():
            tmp = modifierCheck(inName, panel, panelDict)
            allPanels[prio][panel] = tmp
        for panel, panelDict in allPanels[prio].items():
            print panel, panelDict
            if isinstance(panelDict, dict):
                tmpPanel = copy.deepcopy(GRAFANA_PANEL)
                tmpPanel['title'] = panelDict['title']
                tmpPanel['id'] = panelID
                tmpPanel['datasource'] = config['opentsdb']['datasource']
                panelID += 1
                unitMapping = getUnitMapping(panelDict['units'])
                tmpPanel['yaxes'][0]['format'] = unitMapping
                tmpPanel['yaxes'][0]['label'] = panelDict['units']
                for repKey, repVal in MAPPINGS[panelDict['chart_type'].upper()].items():
                    tmpPanel[repKey] = repVal
                tmpTargets = prepareGrafanaTarget(inName, panelDict, config)
                for item in tmpTargets:
                    tmpPanel['targets'].append(item)
                tmpPanels.append(tmpPanel)
            elif isinstance(panelDict, list):
                for panelItem in panelDict:
                    tmpPanel = copy.deepcopy(GRAFANA_PANEL)
                    tmpPanel['title'] = panelItem['title']
                    tmpPanel['id'] = panelID
                    tmpPanel['datasource'] = config['opentsdb']['datasource']
                    panelID += 1
                    unitMapping = getUnitMapping(panelItem['units'])
                    tmpPanel['yaxes'][0]['format'] = unitMapping
                    tmpPanel['yaxes'][0]['label'] = panelItem['units']
                    for repKey, repVal in MAPPINGS[panelItem['chart_type'].upper()].items():
                        tmpPanel[repKey] = repVal
                    tmpTargets = prepareGrafanaTarget(inName, panelItem, config)
                    for item in tmpTargets:
                        tmpPanel['targets'].append(item)
                    tmpPanels.append(tmpPanel)
            else:
                raise
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

def prepareDashboard(tmpOut, config):
    """
    Prepare dashboard for specific host
    Input: dict: config : all configuration parameters
    Returns: None
    """
    # opentsdb looks only at global level configs
    newDash = copy.deepcopy(GRAFANA_DASHBOARD)
    newDash['description'] = config['opentsdb']['description']
    newDash['title'] = config['opentsdb']['title']
    if 'tags' in config['opentsdb']:
        newDash['tags'] = config['opentsdb']['tags']
    autoTemplate = copy.deepcopy(GRAFANA_TEMPLATE)
    autoTemplate['name'] = 'HOSTNAME'
    newDash['templating']['list'] = []
        # "list": [
    for hostname, hostDict in config["HOSTS"].items():
        newLink = copy.deepcopy(GRAFANA_LINKS)
        newLink['tooltip'] = "Open Real Time Netdata monitoring at %s" % hostDict['section']
        newLink['title'] = "RTM at %s" % hostDict['section']
        newLink['url'] = hostname
        newDash['links'].append(newLink)
        # Generate new templating parameters;
        tmpOpt = copy.deepcopy(GRAFANA_TEMPLATE_OPTION)
        tmpOpt["text"] = hostDict['section']
        tmpOpt["value"] = hostDict['section']
        autoTemplate['options'].append(tmpOpt)
    newDash['templating']['list'].append(autoTemplate)
    # allow to add other options for selection:
    if config['opentsdb']['customfilters']:
        for keyFilter, valFilter in config['opentsdb']['customfilters'].items():
            tmpTemplate = copy.deepcopy(GRAFANA_TEMPLATE)
            tmpTemplate['name'] = keyFilter
            for value in valFilter:
                tmpOpt = copy.deepcopy(GRAFANA_TEMPLATE_OPTION)
                tmpOpt["text"] = value
                tmpOpt["value"] = value
                tmpTemplate['options'].append(tmpOpt)
            newDash['templating']['list'].append(tmpTemplate)
    # Append FIRST row.
    if 'customFirstRow' in config['opentsdb'].keys():
        tmpRows = []
        with open(config['opentsdb']['customFirstRow'], 'r') as fd:
            tmpRows = json.load(fd)
        for item in tmpRows:
            newDash['rows'].append(item)
    # Start with FIELD_DESC keys as important ones.
    for key in config['opentsdb']['order']:
        if key in tmpOut.keys():
            newRow = prepareGrafanaRow(key, tmpOut[key], config)
            newDash['rows'].append(newRow)
            del tmpOut[key]
    if not config['opentsdb']['skipOthers']:
        for key in tmpOut.keys():
            newRow = prepareGrafanaRow(key, tmpOut[key], config)
            newDash['rows'].append(newRow)
    # Append LAST rows.
    with open('opentsdb.json', 'w') as fd:
        fd.write(json.dumps(newDash, sort_keys=True, indent=2, separators=(',', ': ')))
    return


def start(config):
    """
    Go through all list of HOSTs and prepare dashboards for each and also one big joint dashboard;
    Input: dict: config : all configuration parameters
    Returns: None
    """
    tmpOut = {}
    for hostName, hostConf in config["HOSTS"].items():
        netdataIn = json.load(getDataFromUrl('%s/api/v1/charts' % hostConf['hostname']))
        if 'charts' in netdataIn.keys():
            for chartName, chartDict in netdataIn['charts'].items():
                tmpRowOut = tmpOut.setdefault(chartDict['type'], {})
                tmpPrioOut = tmpRowOut.setdefault(chartDict['priority'], {})
                tmpTypeOut = tmpPrioOut.setdefault(chartName, {})
                if tmpTypeOut:
                    # Means there is already this specific chart in place...
                    # print 'Already in place this type'
                    for dimName, dimDict in chartDict['dimensions'].items():
                        if dimName not in tmpTypeOut['dimensions'].keys():
                            # print 'Added new dimension. %s' % dimName
                            tmpTypeOut['dimensions'][dimName] = dimDict
                        elif dimDict["name"] != tmpTypeOut['dimensions'][dimName]['name']:
                            continue  # We work only with IDs, so this check is not needed.
                            #print 'Big Problem... Two different names, while keys are the same...'
                            #print 'We are not overwriting it, so please check %s hostname %s chart and %s dimensions ' % (hostName, chartName, chartDict['type'])
                else:
                    tmpRowOut[chartDict['priority']][chartName] = chartDict
    prepareDashboard(tmpOut, config)
