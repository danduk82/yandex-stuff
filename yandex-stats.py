#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 27 14:40:42 2016

@author: borghia
"""


import csv,sys,os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import argparse as ap




class PhoutContents():
    """ reads CSV file and loads data"""
    def __init__(self,csvFileNameList):
        self.fields = ['time' , 
        'tag', 
        'interval_real', 
        'connect_time', 
        'send_time',  
        'latency', 
        'receive_time', 
        'interval_event', 
        'size_out', 
        'size_in', 
        'net_code', 
        'proto_code']
        raw_values = {key: [] for key in self.fields}
        for csvFileName in csvFileNameList:
            with open(csvFileName,'r') as csvFile:
                # sniffing csv file to detect dialect
                self.dialect=csv.Sniffer().sniff(csvFile.readline())
                csvFile.seek(0)
                csvReader = csv.reader(csvFile, dialect=self.dialect)
                cRow=0        
                for row in csvReader:
                    iCol=0
                    for cell in row:
                        raw_values[self.fields[iCol]].append(cell)
                        iCol+=1
                    cRow+=1
        self.values = {}
        for field in self.fields:
            if not field == 'tag':
                self.values[field] = np.array([float(c) for c in raw_values[field]])
            else:
                self.values[field] = raw_values

def usage():
    print("usage:\n%s [options]" % (os.path.basename(sys.argv[0])))
    print(" ")
    print("try -h or --help for extended help")


class PrintLicense(ap.Action):
    #    def __init__(self, option_strings, dest, nargs=0, **kwargs):
    #        if nargs is not 0:
    #            raise ValueError("nargs not allowed")
    #        super(PrintLicense, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_strings=None):
        print(self.licenseText)
        setattr(namespace, self.dest, values)
        sys.exit(0)

    licenseText = """
    Licence:
            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
                     Version 2, December 2004
    TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

             0. You just DO WHAT THE FUCK YOU WANT TO.

    more info at: http://www.wtfpl.net/about/
"""

def createParser():
    parser = ap.ArgumentParser(description="""
This software reads a yandex-tank phout_xy.log and creates a graphic of response 
times, and outputs basic statistics (such as mean, median, etc) of these 
response times.
 
""",
                         epilog="""


Disclaimer:
    This software is provided \"as is\" and
    is not granted to work in particular cases or without bugs. The author
    disclaims any responsability in case of data loss, computer damage or any
    other bad issue that could arise using this software.

    Author:
    Andrea Borghi, Swisstopo, Switzerland

    Date: May, 2016


Example:
   yandex-stats -t 1000 phout_whRoGN.log

    """,
        formatter_class=ap.RawDescriptionHelpFormatter)

    
    optionGroup = parser.add_argument_group('Program options')
    optionGroup.add_argument('-v', '--version', action='version', version="%(prog)s v0.1 Licence: WTFPL v2")
    optionGroup.add_argument('-l', '--license', dest='licenseYoN', nargs=0, action=PrintLicense, default=False, help="output license information")
    optionGroup.add_argument('-n', '--name', dest='testName', action='store', type=str, default='yandex-test', help="test name to be used in the formatted output and graphics, default is 'yandex-test'")
    optionGroup.add_argument('-o', '--output', dest='outFilePrefix', action='store', type=str, default='yandex-test', help="output file name prefix for figures, default is also 'yandex-test'")
    optionGroup.add_argument('-t', '--max-time', dest='maxTime', action='store', type=int, default=500, help="max time to be used for the response time figure plot")
    return parser



if __name__ == '__main__':
    parser = createParser()
    options, other = parser.parse_known_args()
    if not other: # if there is no input, neither a file nor a stdin object, then exit
        parser.print_usage()
        sys.exit(0)   

    testName = options.testName
    outFileName = options.outFilePrefix
    
        
    print(other)    
    contents         = PhoutContents(other)
    mask200          = contents.values['proto_code'] == 200
    maskHttpError    = contents.values['proto_code'] >= 400
    maskNetworkError = contents.values['net_code'] != 0


    plotval = (contents.values['interval_real'][mask200]) /1000.0
    stats = {"mean" : np.mean(plotval),
             "median" : np.median(plotval),
             "std" : np.std(plotval), 
             "percentile90" : np.percentile(plotval,90),
             "percentile95" : np.percentile(plotval,95),
             "min-max-range" : np.ptp(plotval),
             "percentage-of-http-200" : float(np.sum(mask200)) / float(np.size(mask200)) * 100.0 ,
             "percentage-of-http-errors" : float(np.sum(maskHttpError)) / float(np.size(maskHttpError)) * 100.0 ,
             "percentage-of-network-errors" : float(np.sum(maskNetworkError)) / float(np.size(maskNetworkError)) * 100.0}

    print("response time [ms] statistics for test : '{0}' ".format(testName))
    for x in sorted(stats):
        print("{what} : {qty}".format(what=x, qty=stats[x]))
        
    plt.ioff()
    plt.title("response time [ms] test : '{0}' ".format(testName))
    
    mybins = [x*10 for x in range(0,int(options.maxTime/10)+1)] # for histogram, bins from 0 to maxTime, in 10ths of ms
    n, bins, patches = plt.hist(plotval , facecolor = 'green', bins = mybins)
    plt.xlabel('response time [ms]', fontsize=14)
    plt.ylabel('normalized responses', fontsize=14)
    plt.xlim(0, max(mybins))
    plt.draw()
    plt.savefig(outFileName + '-response-time.png',dpi=300)
    plt.close()

    returnCodes = np.unique(contents.values['proto_code'])
    httpStatusCounter = [sum(contents.values['proto_code'] == r ) for r in returnCodes]
    httpStatusStr     = [str(int(s)) for s in returnCodes]
    
    colors = []
    for i in np.arange(len(returnCodes)):
        if returnCodes[i] == 200 : 
            colors.append('green')
        elif returnCodes[i] == 0 :
            colors.append('blue')
        else:
            colors.append('red')
            
    plt.ioff()
    plt.title("HTTP return status : '{0}' ".format(testName))
    fig, ax = plt.subplots()
    bar_width = 0.35
    ind = np.arange(len(returnCodes))
    rects1 = plt.bar(ind,  httpStatusCounter, bar_width, color=colors)
    plt.xlabel('http status')
    plt.ylabel('nb request (total = {0})'.format(len(contents.values['proto_code'])))
    plt.xticks(ind - (bar_width/2.0) + bar_width, httpStatusStr)
    plt.draw()
    plt.savefig(outFileName + 'http-status.png',dpi=300)
    plt.close()
    


    
