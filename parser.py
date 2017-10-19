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
import urllib2
from common import getConfig
from common import getDataFromUrl
from graphite import start as graphiteDashboard
from opentsdb import start as opentsdbDashboard

def getNetdataConfig(mainConfig, sectionName):
    """
    Get netdata server config and also check backend configuration
    Input: Config: mainConfig  : All configuration
           str     sectionName : Section Name of that specific config
    Returns: boolean: True - success in getting config and all parameters defined correctly.
                      False - Failure in retrieving one or another configuration parameters.
             dict: {} - if boolean return is False, always empty as failed to retrieve.
                   otherwise dictionary of all parsed configuration parameters
    """
    # TODO look at netdata filters, and ignore which are not published to Database
    hostname = mainConfig.get(sectionName, 'hostname')
    outDict = {}
    with tempfile.NamedTemporaryFile(delete=False) as fd:
        try:
            tmpConf = getDataFromUrl("%s/netdata.conf" % hostname)
            for line in tmpConf.read().splitlines():
                fd.write(line.replace('\t', '') + "\n")
        except urllib2.URLError as ex:
            print 'Received URLError %s for %s. Checking if config file is present locally' % (ex, hostname)
            if os.path.isfile("%s.conf" % sectionName):
                with open("%s.conf" % sectionName, 'r') as fdConf:
                    for line in fdConf:
                        fd.write(line.replace('\t', '') + "\n")
            else:
                print 'Config file is also not present. Skipping this node %s check' % hostname
                return False, {}
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

def getValFromConfig(mainConfig, sectionName, optionName, defaultVal=''):
    """ Get Value from config if present, otherwise return defaultVal """
    if mainConfig.has_section(sectionName):
        if mainConfig.has_option(sectionName, optionName) and mainConfig.get(sectionName, optionName):
            return mainConfig.get(sectionName, optionName)
    return defaultVal

def checkSkipOthers(mainConfig, sectionName):
    return bool(getValFromConfig(mainConfig, sectionName, 'skipOthers', False))

def checkOrderConfig(mainConfig, sectionName):
    return getValFromConfig(mainConfig,
                            sectionName,
                            'order',
                            'system,mem,cpu,disk,net,ipv4,ipv6,netfilter,apps,users,groups,services,tc').split(',')

def getTags(mainConfig, sectionName):
    return getValFromConfig(mainConfig, sectionName, 'tags', [])

def main():
    """
    Main execution. For all config specified netdata hosts, prepare grafana dashboard template.
    Input: None
    Returns: None
    """
    # TODO. Allow to specify configuration location.
    allConfigs = {"HOSTS": {}}
    mainConfig = getConfig(['netdata-grafana-hosts.conf'])
    allConfigs['backend'] = mainConfig.get('global', 'backend')
    allConfigs['grafanaUrl'] = mainConfig.get('global', 'grafanaUrl')
    if allConfigs['backend'] == 'opentsdb':
        allConfigs['opentsdb'] = {"datasource": mainConfig.get('opentsdb', 'datasource'),
                                  "order": checkOrderConfig(mainConfig, 'opentsdb'),
                                  "skipOthers": checkSkipOthers(mainConfig, 'opentsdb')}
        allConfigs['opentsdb']['title'] = mainConfig.get('opentsdb', 'title')
        allConfigs['opentsdb']['description'] = mainConfig.get('opentsdb', 'description')
        allConfigs['opentsdb']['dimensionids'] = mainConfig.getboolean('opentsdb', 'dimensionids')
        allConfigs['opentsdb']['prefix'] = mainConfig.get('opentsdb', 'prefix')
        allConfigs['opentsdb']['tags'] = getTags(mainConfig, 'opentsdb')
        allConfigs['opentsdb']['customfilters'] = json.loads(mainConfig.get('opentsdb', 'customfilters'))
        # get customFirstRow and customLastRow
        allConfigs['opentsdb']['customFirstRow'] = getValFromConfig(mainConfig, 'opentsdb', 'customFirstRow')
        allConfigs['opentsdb']['customLastRow'] = getValFromConfig(mainConfig, 'opentsdb', 'customLastRow')
    for sectionName in mainConfig.sections():
        if sectionName in ['global', 'opentsdb']:
            continue
        # check if mandatory options are in place
        if not(mainConfig.has_option(sectionName, 'hostname') and
               mainConfig.get(sectionName, 'hostname')):
            print 'In section %s hostname is not defined. It is mandatory to define full url' % sectionName
            print '* Skipping this node check.'
            continue
        if allConfigs['backend'] == 'graphite':
            if not(mainConfig.has_option(sectionName, 'datasource') and
                   mainConfig.get(sectionName, 'datasource')):
                print 'In section %s dataspirce is not defined. It is mandatory to define datasource' % sectionName
                print '* Skipping this node check.'
                continue
        configSuccess, config = getNetdataConfig(mainConfig, sectionName)
        if not configSuccess:
            config['SKIP_NODE'] = False  # This is not looked in case of graphite. TODO
        config['tags'] = getTags(mainConfig, allConfigs['backend'])
        if allConfigs['backend'] == 'graphite':
            # This is relevant only for graphite
            config['datasource'] = mainConfig.get(sectionName, 'datasource')
            config['order'] = checkOrderConfig(mainConfig, sectionName)
            config['skipOthers'] = checkSkipOthers(mainConfig, sectionName)
        config['hostname'] = mainConfig.get(sectionName, 'hostname')
        config['section'] = sectionName
        # get customFirstRow and customLastRow
        config['customFirstRow'] = getValFromConfig(mainConfig, sectionName, 'customFirstRow')
        config['customLastRow'] = getValFromConfig(mainConfig, sectionName, 'customLastRow')
        allConfigs["HOSTS"][config['hostname']] = config
    print allConfigs
    # Now send allConfigs to a specific backend preparator.
    if allConfigs['backend'] == 'graphite':
        graphiteDashboard(allConfigs)
    elif allConfigs['backend'] == 'opentsdb':
        opentsdbDashboard(allConfigs)
    else:
        print 'Unknown backend type... Exiting'

if __name__ == '__main__':
    main()
