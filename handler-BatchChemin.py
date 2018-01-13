# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 11:36:53 2016

@author: philippe
"""

import qxrd
import qxrdtools
import numpy as np
import csv
import plottool
import os
import os.path
import time
import matplotlib.pyplot as plt


def getminlist(phaselistfile):
    f = open(phaselistfile, 'r').readlines()
    minlist = []
    for i in range(1, len(f)):
        line = f[i]
        minname = line.split(',')[0].lower()
        minlist = minlist + [minname.lower(), ]
    return minlist


def getselectedphases(inventoryfile, minreslist):
    global notfound

    selectedphases = []
    namelist = []
    phaselist = open(inventoryfile, 'r').readlines()
    for i in range(1, len(phaselist)):
        name, code = phaselist[i].split('\t')
        name = name.lower()
        namelist = namelist + [name, ]
        code = int(code)
        for minname in minreslist:
            # print minname.lower(), ' vs ', name.lower()
            if minname.lower() == name.lower():
                selectedphases.append((name, code))
    for i in range(0, len(minreslist)):
        if not (minreslist[i] in namelist) and not (minreslist[i] in notfound):
            notfound = notfound + [minreslist[i], ]

    return selectedphases


def getselectedphasesfromfile(inventoryfile, phaselistfile):
    global notfound
    selectedphases = []
    codelist = []
    inventory = open(inventoryfile, 'r').readlines()
    phaselist = open(phaselistfile, 'r').readlines()
    for i in range(1, len(inventory)):
        name, code = inventory[i].split('\t')
        name = name.lower()
        code = int(code)
        inventory[i] = [name, code]
        codelist = codelist + [code, ]
    for i in range(1, len(phaselist)):
        name, code = phaselist[i].split('\t')
        name = name.lower()
        code = int(code)
        phaselist[i] = [name, code]

        if phaselist[i][1] in codelist:
            selectedphases.append(phaselist[i])
        else:
            notfound = notfound + [phaselist[i], ]

    return selectedphases


autoremove = False
BGstrip = True
InstrParams = {"Lambda": 0, "Target": 'Co', "FWHMa": 0.000, "FWHMb": 0.35}
allphases = False
plotindiv = True

# DBfilepath='/home/philippe/Documents/Projects/Python/quantdatavision/desktop/databases'
DBfilepath = 'databases'
DBname = "difdata_CheMin.txt"
difdata = open((os.path.join(DBfilepath, DBname)), 'r').readlines()

# folder='/home/philippe/Documents/Projects/Python/quantdatavision/desktop/XRD_data/Chemin-CSV'
folder = 'Chemin-CSV'
folderlist = os.listdir(folder)
'''
filelist is a list of ('XRDfile.csv', 'phaselist.csv')
'''
filelist = []

for filename in folderlist:
    filenamesplit = os.path.splitext(filename)
    if filenamesplit[0][13:16] == "rda" and filenamesplit[1] == ".csv":
        # search for mineral list file
        phaselistname = 'Phase_list_' + filenamesplit[0][37:] + '.csv'
        if phaselistname in folderlist:
            filelist = filelist + [[filename, phaselistname], ]

        else:
            filelist = filelist + [[filename, 'none'], ]

for i in range(0, len(filelist)):
    print filelist[i]

selectedphase = []
notfound = []

if allphases:
    phaselistname = 'difdata_CheMin_inventory.csv'
    selectedphases = []
    phaselist = open(os.path.join(DBfilepath, phaselistname), 'r').readlines()
    for i in range(1, len(phaselist)):
        name, code = phaselist[i].split('\t')
        code = int(code)
        selectedphases.append((name, code))

# for i in range(0, len(filelist)):
for i in range(0, 1):
    if filelist[i][1] != 'none':
        print "processing:", filelist[i][0]
        minlist = getminlist(os.path.join(folder, filelist[i][1]))
        if not allphases:
            selectedphases = getselectedphasesfromfile(os.path.join(
                DBfilepath, "difdata_CheMin_inventory.csv"), os.path.join(folder, filelist[i][1]))
        print 'Selectedphases: ', len(selectedphases)

        if len(selectedphases) > 0:
            t0 = time.time()
            XRD = os.path.join(folder, filelist[i][0])
            blob = open(XRD, 'r')
            userdata = qxrdtools.openXRD(
                blob, os.path.join(folder, filelist[i][0]))
            print selectedphases
            results, BG, calcdiff, mineralpat = qxrd.Qanalyze(
                userdata, difdata, selectedphases, InstrParams, autoremove, BGstrip)
            print results
            plot = plottool.overplotgraph(
                userdata, BG, calcdiff, results, mineralpat, plotindiv, os.path.splitext(filelist[i][0])[0])
            figname = '%s_Qanalyze.png' % (os.path.splitext(filelist[i][0])[0])
            plt.savefig(os.path.join(folder, figname))
            print "number of mineral refined: ", len(results)
            for i in range(1, len(selectedphases)):
                found = False
                for j in range(1, len(results)):
                    if selectedphases[i][1] == results[j][1]:
                        found = True
                if not found:
                    print "\tnot processed:%s" % selectedphases[i]
            print "Total computation  time = %.2fs" % (time.time() - t0)


print "notfound: ", notfound
# print plot, results
