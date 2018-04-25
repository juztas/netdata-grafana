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
import urllib2
import ConfigParser

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