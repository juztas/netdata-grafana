""" NV plugin modifier """
import copy
CONFIG = {
    "nv.load": {"title_start": "Load for ", "title_end": " (nv.load)", "title_split": "|",
                "dimensions": ['device_load_mem_%s', 'device_load_gpu_%s'],
                "group_key": True, 'key_starts': [{'start': 'device_load_mem_', 'value': 'Memory'},
                                                  {'start': 'device_load_gpu_', 'value': 'GPU'}]},
    "nv.memory": {"title_start": "Memory for ", "title_end": " (nv.memory)", "title_split": "|",
                  "dimensions": ['device_mem_used_%s', 'device_mem_free_%s'], "group_key": True,
                  'key_starts': [{'start': 'device_mem_used_', 'value': 'Memory Used'},
                                 {'start': 'device_mem_free_', 'value': 'Memory Free'}]},
    "nv.frequency": {"title_start": "Frequency for ", "title_end": " (nv.frequency)", "title_split": "|",
                     "dimensions": ['device_mem_clock_%s', 'device_sm_clock_%s', 'device_core_clock_%s'],
                     "group_key": True, 'key_starts': [{'start': 'device_mem_clock_', 'value': 'Memory'},
                                                       {'start': 'device_mem_free_', 'value': 'SM'},
                                                       {'start': 'device_core_clock_', 'value': 'Core'}]},
}

def start(sectionName, chartName, charts):
    print charts
    title = charts['title']
    preparedCharts = []
    if CONFIG[chartName].has_key('title_start') and \
       CONFIG[chartName].has_key('title_end') and \
       CONFIG[chartName].has_key('title_split'):
        lenStart = len(CONFIG[chartName]['title_start'])
        lenEnd = len(CONFIG[chartName]['title_end'])
        if charts['title'][:lenStart] != CONFIG[chartName]['title_start']:
            print 'Not equal!'
            raise
        elif charts['title'][-lenEnd:] != CONFIG[chartName]['title_end']:
            print 'Not equal!'
            raise
        else:
            title = charts['title'][lenStart:-lenEnd].split(CONFIG[chartName]['title_split'])
        for item in title:
            tmpChart = copy.deepcopy(charts)
            del tmpChart['dimensions']
            tmpChart.setdefault('dimensions', {})
            name = item.rstrip()
            tmpChart['title'] = "%s%s%s" % (CONFIG[chartName]['title_start'], name, CONFIG[chartName]['title_end'])
            # get it's number
            numC = name[-2:-1]
            for dim in CONFIG[chartName]['dimensions']:
                dimName = dim % numC
                tmpChart['dimensions'][dimName] = charts['dimensions'][dimName]
            preparedCharts.append(tmpChart)
        if CONFIG[chartName]['group_key']:
            for keyC in CONFIG[chartName]['key_starts']:
                tmpChart = copy.deepcopy(charts)
                del tmpChart['dimensions']
                tmpChart.setdefault('dimensions', {})
                tmpChart['title'] = "%s%s %s%s" % (CONFIG[chartName]['title_start'],
                                                   keyC['value'],
                                                   charts['title'][lenStart:-lenEnd],
                                                   CONFIG[chartName]['title_end'])
                for dimkey, dimDict in charts['dimensions'].items():
                    if dimkey.startswith(keyC['start']):
                        tmpChart['dimensions'][dimkey] = dimDict
                print tmpChart
  # Title can be a list or it can be string;
    # Now take first dimmensions groups, make deepcopy of chartDict and append new chartDict;
   # TODO if there is a group key begining and group key ending, go again through whole chartDict and group by key
    return preparedCharts