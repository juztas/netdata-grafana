#!/usr/bin/python
# pylint: disable=line-too-long
"""
Grafana dashs, panels, rows variables. ##### will be replaced with metric value

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
GRAFANA_DASHBOARD = {
    "annotations": {"list": []},
    "description": "#####",
    "title": "#####",
    "editable": True,
    "gnetId": 1,
    "graphTooltip": 0,
    "hideControls": False,
    "id": 1,
    "tags": [],
    "links": [],
    "refresh": False,
    "rows": []}

GRAFANA_ROW = {
    "collapse": True,
    "height": "250px",
    "repeat": None,
    "repeatIteration": None,
    "repeatRowId": None,
    "showTitle": True,
    "title": "#####",
    "titleSize": "h3",
    "panels": []}

GRAFANA_PANEL = {
    "aliasColors": {},
    "bars": False,
    "dashLength": 10,
    "dashes": False,
    "datasource": "#####",
    "description": "#####",
    "editable": True,
    "error": False,
    "fill": 1,
    "id": 1,
    "legend": {"avg": True, "current": False, "max": True, "min": True, "show": True, "total": False, "values": True},
    "lines": True,
    "linewidth": 1,
    "links": [],
    "nullPointMode": "connected",
    "percentage": False,
    "pointradius": 5,
    "points": False,
    "renderer": "flot",
    "seriesOverrides": [],
    "spaceLength": 10,
    "span": 6,
    "stack": False,
    "steppedLine": False,
    "targets": [],
    "thresholds": [],
    "timeFrom": None,
    "timeShift": None,
    "title": "######",
    "tooltip": {"msResolution": False, "shared": True, "sort": 0, "value_type": "individual"},
    "type": "graph",
    "xaxis": {"buckets": None, "mode": "time", "name": None, "show": True, "values": []},
    "yaxes": [
        {"format": "########", "label": "Label #####", "logBase": 1, "max": None, "min": None, "show": True},
        {"format": "short", "label": None, "logBase": 1, "max": None, "min": None, "show": True}]}

GRAFANA_TARGET = {
    "alias": "######",
    "dsType": "influxdb",
    "groupBy": [
        {"params": ["$interval"], "type": "time"},
        {"params": ["null"], "type": "fill"}],
    "measurement": "########",
    "orderByTime": "ASC",
    "policy": "default",
    "refId": "#####",
    "resultFormat": "time_series",
    "select": [[
        {"params": ["value"],
         "type": "field"},
        {"params": [], "type": "mean"}]],
    "tags": []}

GRAFANA_LINKS = {
    "icon": "external link",
    "tags": [],
    "targetBlank": True,
    "tooltip": "#####",
    "title": "#####",
    "type": "link",
    "url": "#####"}


FIELD_DESC = {
    'system': {'title': 'System Overview',
               'info': 'Overview of the key system metrics.'},
    'mem': {'title': 'Memory',
            'info': 'Detailed information about the memory management of the system.'},
    'cpu': {'title': 'CPUs',
            'info': 'Detailed information for each CPU of the system. A summary of the system for all CPUs can be found at the <a href="#menu_system">System Overview</a> section.'},
    'disk': {'title': 'Disks',
             'info': 'Charts with performance information for all the system disks. Special care has been given to present disk performance metrics in a way compatible with <code>iostat -x</code>. netdata by default prevents rendering performance charts for individual partitions and unmounted virtual disks. Disabled charts can still be enabled by configuring the relative settings in the netdata configuration file.'},
    'net': {'title': 'Network Interfaces',
            'info': 'Performance metrics for network interfaces.'},
    'ipv4': {'title': 'IPv4 Networking',
             'info': 'Metrics for the IPv4 stack of the system. <a href="https://en.wikipedia.org/wiki/IPv4" target="_blank">Internet Protocol version 4 (IPv4)</a> is the fourth version of the Internet Protocol (IP). It is one of the core protocols of standards-based internetworking methods in the Internet. IPv4 is a connectionless protocol for use on packet-switched networks. It operates on a best effort delivery model, in that it does not guarantee delivery, nor does it assure proper sequencing or avoidance of duplicate delivery. These aspects, including data integrity, are addressed by an upper layer transport protocol, such as the Transmission Control Protocol (TCP).'},
    'ipv6': {'title': 'IPv6 Networking',
             'info': 'Metrics for the IPv6 stack of the system. <a href="https://en.wikipedia.org/wiki/IPv6" target="_blank">Internet Protocol version 6 (IPv6)</a> is the most recent version of the Internet Protocol (IP), the communications protocol that provides an identification and location system for computers on networks and routes traffic across the Internet. IPv6 was developed by the Internet Engineering Task Force (IETF) to deal with the long-anticipated problem of IPv4 address exhaustion. IPv6 is intended to replace IPv4.'},
    'netfilter': {'title': 'Firewall (netfilter)',
                  'info': 'Performance metrics of the netfilter components.'},
    'apps': {'title': 'Applications',
             'info': 'Per application statistics are collected using netdata\'s <code>apps.plugin</code>. This plugin walks through all processes and aggregates statistics for applications of interest, defined in <code>/etc/netdata/apps_groups.conf</code> (the default is <a href="https://github.com/firehol/netdata/blob/master/conf.d/apps_groups.conf" target="_blank">here</a>). The plugin internally builds a process tree (much like <code>ps fax</code> does), and groups processes together (evaluating both child and parent processes) so that the result is always a chart with a predefined set of dimensions (of course, only application groups found running are reported). The reported values are compatible with <code>top</code>, although the netdata plugin counts also the resources of exited children (unlike <code>top</code> which shows only the resources of the currently running processes). So for processes like shell scripts, the reported values include the resources used by the commands these scripts run within each timeframe.'},
    'users': {'title': 'Users',
              'info': 'Per user statistics are collected using netdata\'s <code>apps.plugin</code>. This plugin walks through all processes and aggregates statistics per user. The reported values are compatible with <code>top</code>, although the netdata plugin counts also the resources of exited children (unlike <code>top</code> which shows only the resources of the currently running processes). So for processes like shell scripts, the reported values include the resources used by the commands these scripts run within each timeframe.'},
    'groups': {'title': 'User Groups',
               'info': 'Per user group statistics are collected using netdata\'s <code>apps.plugin</code>. This plugin walks through all processes and aggregates statistics per user group. The reported values are compatible with <code>top</code>, although the netdata plugin counts also the resources of exited children (unlike <code>top</code> which shows only the resources of the currently running processes). So for processes like shell scripts, the reported values include the resources used by the commands these scripts run within each timeframe.'},
    'services': {'title': 'systemd Services',
                 'info': 'Resources utilization of systemd services. netdata monitors all systemd services via cgroups (the resources accounting used by containers). '},
    'tc': {'title': 'Quality of Service',
           'info': 'Netdata collects and visualizes <code>tc</code> class utilization using its <a href="https://github.com/firehol/netdata/blob/master/plugins.d/tc-qos-helper.sh" target="_blank">tc-helper plugin</a>. If you also use <a href="http://firehol.org/#fireqos" target="_blank">FireQOS</a> for setting up QoS, netdata automatically collects interface and class names. If your QoS configuration includes overheads calculation, the values shown here will include these overheads (the total bandwidth for the same interface as reported in the Network Interfaces section, will be lower than the total bandwidth reported here). QoS data collection may have a slight time difference compared to the interface (QoS data collection uses a BASH script, so a shift in data collection of a few milliseconds should be justified).'},
    'ap': {'title': 'Access Points',
           'info': 'Performance metrics for the access points (i.e. wireless interfaces in AP mode) found on the system.'},
    'ipvs': {'title': 'IP Virtual Server',
             'info': '<a href="http://www.linuxvirtualserver.org/software/ipvs.html" target="_blank">IPVS (IP Virtual Server)</a> implements transport-layer load balancing inside the Linux kernel, so called Layer-4 switching. IPVS running on a host acts as a load balancer at the front of a cluster of real servers, it can direct requests for TCP/UDP based services to the real servers, and makes services of the real servers to appear as a virtual service on a single IP address.'},
    'ipfw': {'title': 'Firewall (ipfw)',
             'info': 'Counters and memory usage for the ipfw rules.'},
    'sensors': {'title': 'Sensors',
                'info': 'Readings of the configured system sensors.'},
    'ipmi': {'title': 'IPMI',
             'info': 'The Intelligent Platform Management Interface (IPMI) is a set of computer interface specifications for an autonomous computer subsystem that provides management and monitoring capabilities independently of the host system\'s CPU, firmware (BIOS or UEFI) and operating system.'},
    'samba': {'title': 'Samba',
              'info': 'Performance metrics of the Samba file share operations of this system. Samba is a implementation of Windows services, including Windows SMB protocol file shares.'},
    'nfsd': {'title': 'NFS Server',
             'info': 'Performance metrics of the Network File Server. NFS is a distributed file system protocol, allowing a user on a client computer to access files over a network, much like local storage is accessed. NFS, like many other protocols, builds on the Open Network Computing Remote Procedure Call (ONC RPC) system. The NFS is an open standard defined in Request for Comments (RFC).'},
    'nfs': {'title': 'NFS Client',
            'info': 'Performance metrics of the NFS operations of this system, acting as an NFS client.'},
    'zfs': {'title': 'ZFS filesystem',
            'info': 'Performance metrics of the ZFS filesystem. The following charts visualize all metrics reported by <a href="https://github.com/zfsonlinux/zfs/blob/master/cmd/arcstat/arcstat.py" target="_blank">arcstat.py</a> and <a href="https://github.com/zfsonlinux/zfs/blob/master/cmd/arc_summary/arc_summary.py" target="_blank">arc_summary.py</a>.'},
    'netdata': {'title': 'Netdata Monitoring',
                'info': 'Performance metrics for the operation of netdata itself and its plugins.'},
    'example': {'title': 'Example Charts',
                'info': 'Example charts, demonstrating the external plugin architecture.'},
    'cgroup': {'title': '',
               'info': 'Container resource utilization metrics. Netdata reads this information from <b>cgroups</b> (abbreviated from <b>control groups</b>), a Linux kernel feature that limits and accounts resource usage (CPU, memory, disk I/O, network, etc.) of a collection of processes. <b>cgroups</b> together with <b>namespaces</b> (that offer isolation between processes) provide what we usually call: <b>containers</b>.'},
    'cgqemu': {'title': 'QEMU Utilization',
               'info': 'QEMU virtual machine resource utilization metrics. QEMU (short for Quick Emulator) is a free and open-source hosted hypervisor that performs hardware virtualization.'},
    'fping': {'title': 'fping',
              'info': 'Network latency statistics, via <b>fping</b>. <b>fping</b> is a program to send ICMP echo probes to network hosts, similar to <code>ping</code>, but much better performing when pinging multiple hosts. fping versions after 3.15 can be directly used as netdata plugins.'},
    'memcached': {'title': 'memcached',
                  'info': 'Performance metrics for <b>memcached</b>. Memcached is a general-purpose distributed memory caching system. It is often used to speed up dynamic database-driven websites by caching data and objects in RAM to reduce the number of times an external data source (such as a database or API) must be read.'},
    'mysql': {'title': 'MySQL',
              'info': 'Performance metrics for <b>mysql</b>, the open-source relational database management system (RDBMS).'},
    'postgres': {'title': 'Postgres',
                 'info': 'Performance metrics for <b>PostgresSQL</b>, the object-relational database (ORDBMS).'},
    'redis': {'title': 'Redis',
              'info': 'Performance metrics for <b>redis</b>. Redis (REmote DIctionary Server) is a software project that implements data structure servers. It is open-source, networked, in-memory, and stores keys with optional durability.'},
    'retroshare': {'title': 'RetroShare',
                   'info': 'Performance metrics for <b>RetroShare</b>. RetroShare is open source software for encrypted filesharing, serverless email, instant messaging, online chat, and BBS, based on a friend-to-friend network built on GNU Privacy Guard (GPG).'},
    'ipfs': {'title': 'IPFS',
             'info': 'Performance metrics for the InterPlanetary File System (IPFS), a content-addressable, peer-to-peer hypermedia distribution protocol.'},
    'phpfpm': {'title': 'PHP-FPM',
               'info': 'Performance metrics for <b>PHP-FPM</b>, an alternative FastCGI implementation for PHP.'},
    'postfix': {'title': 'postfix',
                'info': None},
    'dovecot': {'title': 'Dovecot',
                'info': None},
    'hddtemp': {'title': 'HDD Temp',
                'info': None},
    'nginx': {'title': 'nginx',
              'info': None},
    'apache': {'title': 'Apache',
               'info': None},
    'lighttpd': {'title': 'Lighttpd',
                 'info': None},
    'web_log': {'title': 'Web Log',
                'info': 'Information extracted from a server log file. <code>web_log</code> plugin incrementally parses the server log file to provide, in real-time, a break down of key server performance metrics. For web servers, an extended log file format may optionally be used (for <code>nginx</code> and <code>apache</code>) offering timing information and bandwidth for both requests and responses. <code>web_log</code> plugin may also be configured to provide a break down of requests per URL pattern (check <a href="https://github.com/firehol/netdata/blob/master/conf.d/python.d/web_log.conf" target="_blank"><code>/etc/netdata/python.d/web_log.conf</code></a>).'},
    'named': {'title': 'named',
              'info': None},
    'squid': {'title': 'squid',
              'info': None},
    'nut': {'title': 'UPS',
            'info': None},
    'apcupsd': {'title': 'UPS',
                'info': None},
    'smawebbox': {'title': 'Solar Power',
                  'info': None},
    'fronius': {'title': 'Fronius',
                'info': None},
    'stiebeleltron': {'title': 'Stiebel Eltron',
                      'info': None},
    'snmp': {'title': 'SNMP',
             'info': None},
    'go_expvar': {'title': 'Go - expvars',
                  'info': 'Statistics about running Go applications exposed by the <a href="https://golang.org/pkg/expvar/" target="_blank">expvar package</a>.'},
    'chrony': {'title': 'System Clock performance',
               'info': 'chronyd parameters about the system\'s clock performance.'}
}

# TODO sub components descriptions. I would love to if all of this in netdata is in just simple json format.
