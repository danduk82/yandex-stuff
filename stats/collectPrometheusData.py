#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This program is used to collect instance metrics from prometheus after load tests.

"""

import requests
import json
from operator import itemgetter
import argparse as ap
import numpy as np
import os, sys

def usage():
    print("usage:\n%s [options]" % (os.path.basename(sys.argv[0])))
    print(" ")
    print("try -h or --help for extended help")

class PrometheusInfo(object):
    def __init__(self,endpoint, user, passwd, baseQuery):
        self.endpoint=endpoint
        self.user=user
        self.passwd=passwd
        self.baseQuery=baseQuery

def loadPrometheusMetrics(prometheusInfo,metricName,instance,start,end,step='10s',metricOption=''):
    r = requests.get(url = prometheusInfo.endpoint,
                     params = prometheusInfo.baseQuery.format(metricName,
                                                             instance,
                                                             start,
                                                             end,
                                                             step),
                     auth= (prometheusInfo.user,
                            prometheusInfo.passwd)
                     )
    data = json.loads(r.text)
    metrics =  data['data']['result']
    results = {}
    for result in metrics:
        if not metricOption:
            print('samere')
            results.update( {metricName : sorted(result['values'], key=itemgetter(0))}) # sorted by date
        else:
            results.update( {result['metric'][metricOption] : sorted(result['values'], key=itemgetter(0))}) # sorted by date
    return results


def createParser():
    parser = ap.ArgumentParser(description="""
This program retrieves metrics from prometheus and export them as json

Example:

    %(prog)s -E 'https://${PROMETHEUS_ENDPOINT}/api/v1/query_range' -u ${PROMETHEUS_USER} -p ${PROMETHEUS_PASS} -i ${instance} -s 1504853000 -e 1504853123 -S 5s -m collectd_cpu_percent -o cpu

""",
                         epilog="""

Disclaimer:
    This software is provided \"as is\" and
    is not granted to work in particular cases or without bugs. The author
    disclaims any responsability in case of data loss, computer damage or any
    other bad issue that could arise using (directly or indirectly) this software.

    Author:
    Andrea Borghi

    Date: September, 2017
    """,
        formatter_class=ap.RawDescriptionHelpFormatter)


    optionGroup = parser.add_argument_group('Program options')
    optionGroup.add_argument('-v', '--version', action='version', version="%(prog)s v0.1 Licence: WTFPL v2")
    optionGroup.add_argument('-E', '--endpoint', dest='endpoint', action='store', type=str, required = True, help="prometheus API endpoint")
    optionGroup.add_argument('-m', '--metric', dest='metric', action='store', type=str, required = True, help="the metric name")
    optionGroup.add_argument('-i', '--instance', dest='instance', action='store', type=str, required = True, help="hostname of the AWS instance we want to collect")
    optionGroup.add_argument('-s', '--start', dest='start', action='store', type=int, required = True, help="start time to be used for the range query (in seconds from the epoch)")
    optionGroup.add_argument('-e', '--end', dest='end', action='store', type=int, required = True, help="end time to be used for the range query (in seconds from the epoch)")
    optionGroup.add_argument('-S', '--step', dest='step', action='store', type=str, default='1s', help="the time step to be used, this is a string. default='1s'")
    optionGroup.add_argument('-u', '--user', dest='user', action='store', type=str, default='prometheus', help="the user to login in prometheus api, default='prometheus'")
    optionGroup.add_argument('-o', '--metricOption', dest='metricOption', action='store', type=str, default = '', help="the metric option, if this is enabled the output will be an array of metrics using this field as field name")
    optionGroup.add_argument('-p', '--passwd', dest='passwd', action='store', type=str, default='nothing', help="the user to login in prometheus api, default='nothing'")

    return parser


if __name__ == '__main__':
    parser = createParser()
    options, other = parser.parse_known_args()
    baseQuery='query={0}{{exported_instance=~"{1}"}}&start={2}&end={3}&step={4}'
    info = PrometheusInfo(options.endpoint, options.user, options.passwd, baseQuery)
    metrics = loadPrometheusMetrics( info,
                                    options.metric,
                                    options.instance,
                                    options.start,
                                    options.end,
                                    options.step,
                                    options.metricOption)
    keys = list(metrics.keys())
    output = np.zeros((len(metrics[keys[0]]),len(keys)+1))
    i = 0
    for key in keys:
        if i == 0:
            output[:,i] = np.array(metrics[key])[:,0]
            i+=1
        output[:,i] = np.array(metrics[key])[:,1]
        i+=1

    outputStr = 'date;'+';'.join(keys)+'\n'
    fmt = '%d;'+';'.join(['%.3f' for i in range(np.shape(output)[1]-1)])+'\n'
    for i in range(np.shape(output)[0]):
        outputStr += fmt % ( tuple(output[i,:]) )
    print(outputStr)


# small reminder of which metrics we are getting from prometheus:
#
#load
#collectd_load_longterm{exported_instance=~"$hostname"}
#collectd_load_midterm{exported_instance=~"$hostname"}
#collectd_load_shortterm{exported_instance=~"$hostname"}
#
#cpu
#collectd_cpu_percent{exported_instance=~"$hostname",cpu="interrupt"}
#collectd_cpu_percent{exported_instance=~"$hostname",cpu="nice"}
#collectd_cpu_percent{exported_instance=~"$hostname",cpu="softirq"}
#collectd_cpu_percent{exported_instance=~"$hostname",cpu="steal"}
#collectd_cpu_percent{exported_instance=~"$hostname",cpu="system"}
#collectd_cpu_percent{exported_instance=~"$hostname",cpu="user"}
#collectd_cpu_percent{exported_instance=~"$hostname",cpu="wait"}
#collectd_cpu_percent{exported_instance=~"$hostname",cpu="idle"}
#
#memory
#collectd_memory{exported_instance=~"$hostname", memory="slab_recl"}
#collectd_memory{exported_instance=~"$hostname", memory="slab_unrecl"}
#collectd_memory{exported_instance=~"$hostname", memory="buffered"}
#collectd_memory{exported_instance=~"$hostname", memory="used"}
#collectd_memory{exported_instance=~"$hostname", memory="cached"}
#collectd_memory{exported_instance=~"$hostname", memory="free"}
