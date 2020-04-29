#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Created on %(date)s
#
# @author: %(username)s

import os
import datetime

from plot.dolueg2plots.plot import plot
from plot.dolueg2plots.gropt import colorscaler

# red and orange for defaulttemperatures
tempcol = ['#ffaa00', '#ff5a00', '#ff0000',
           '#cc0000', '#990000', '#660000',
           '#330000', '#000000', '#ff4d4d',
           '#ff8080']
redcol = ['#ff0000']


humcol = ['#0000ff', '#00A6ff', '#00ffff',
          '#00B2B2', '#006666', '#003333', '#99ccff']
# 2*red,2*blue,2*black
# for longwave down, longwave up, shortwavedown, shortwave up, net radiation
# with the linestyles ['-', ':', '-', ':', ':-']
radlinestyles = ['-', ':', '-', ':', '-', ':']
radcol = ['#FF0000', '#FF0000', '#0000FF',
          '#0000FF', '#000000', '#000000']

soilcol = ['#ffff00']

for i in range(1, 11):
    soilcol.append(colorscaler(soilcol[i-1], scale=0.7))

soilcol[1:] = soilcol[:0:-1]

batcol = ['#660000', '#66008C', '#6600CC',
          '#6600FF', '#C985FF', '#FFCCFF']

#8 colors, from blue to red
colbr = ['#4575b4', '#74add1', '#abd9e9', '#e0f3f8',
         '#fee090', '#fdae61', '#f46d43', '#d73027']

#8 colors, from red to blue
colrb = colbr[::-1]

#10 small rainbowcolors
colrainbow=['#ff0008', '#ff0000', '#ff8000', '#ffff00',
            '#00ff00', '#00ffff', '#0080ff', '#0000ff',
            '#8000ff', '#ff00ff']

#10 rainbow inverted 
colrainbowr=colrainbow[::-1]


def move2webserver(infolder=None,
                   serverpath='ENTER_THE_PATH_OF_YOUR_WEBSERVER',
                   serverfolder='html/dolueg2/',
                   subfolder='',
                   autosubfolder=True,
                   ext='.svg',
                   removenonrefreshed=True,
                   quiet=True,
                   dryrun=True,
                   ensurecleanup=True,
                   ):
    
    if not infolder:
        print('Need an path to look for files as infolder=....')
        return

    import sys
    import shutil
    import os

    if 'win' in sys.platform:
        print('Windows is not supported. Please use Linux')
        return

    if not os.path.exists(infolder):
        print('Given in path does not exist, exiting')
        return

    # infolder remove duplicates (that we might have added ourselves before)
    infolder = os.sep + os.path.abspath(infolder) + os.sep
    infolder = infolder.replace(os.sep*2, os.sep)
    # contains just the filenames, not the path
    graphs2move= [f for f in os.listdir(infolder)
                  if os.path.isfile(os.sep.join([infolder, f]))
                  and f.endswith(ext)]


    outfolder = serverpath+serverfolder+subfolder
    outfolder = os.sep + os.path.abspath(outfolder) + os.sep
    outfolder = outfolder.replace(os.sep*2, os.sep)

    if not os.path.exists(outfolder):
        print('Could not find the needed outfolder:', outfolder)
        os.makedirs(outfolder)

    # contains just the filenames, not the path
    existinggraphs = [f for f in os.listdir(outfolder)
                      if os.path.isfile(os.sep.join([outfolder, f]))
                      and f.endswith(ext)]

    if removenonrefreshed:
        toremove = [f for f in existinggraphs
                    if f not in graphs2move]
        for f in toremove:
            if dryrun:
                print('Would remove', outfolder+f, )
            else:
                print('Removing:\n', outfolder+f)
                os.remove(outfolder+f)

    if graphs2move:
        srcpath, destpath = infolder, outfolder
        for f in graphs2move:
            if dryrun:
                print('Would move', srcpath+f, 'to', destpath+f)
            else:
                try:
                    shutil.copy(srcpath+f, destpath+f)
                    os.remove(srcpath+f)
                except FileNotFoundError:
                    print('Could not move:\n', srcpath+f, '\n', destpath+f)

        if not quiet:
            print('Moved', len(graphs2move), 'files from',
                  infolder, 'to', outfolder)
    else:
        if not quiet:
            print('No files to move')

    if ensurecleanup:
        for f in graphs2move:
            # should have been moved so it should no longer exist
            # just rechecking
            if os.path.exists(srcpath+f):
                os.remove(srcpath+f)

    return

def definetimes():
    import datetime
    import calendar

    now = datetime.datetime.now()
    aday = datetime.timedelta(days=1)
    # the days the month before had, just so we dont overflow at the end
    # of the month
    mday = calendar.monthrange(now.year, ((now.month-1+11) % 12)+1 )

    times = {'0day': [now-aday, now],
             '1week': [now - 7*aday, now],
             # take a year back if the month is january
             '2month': [datetime.datetime(now.year-int(now.month == 1),
                                          ((now.month-1+11) % 12)+1,
                                          min(now.day, mday[1]),
                                          now.hour,
                                          now.minute,
                                          now.second),
                      now],
             '3year': [datetime.datetime(now.year-1,
                                         now.month,
                                         now.day,
                                         now.hour,
                                         now.minute,
                                         now.second),
                      now],
             }

    timesteps = {'0day': '30Min',
                 '1week': '30Min',
                 '2month': '2H',
                 '3year': '1D',
                 }

    return times, timesteps

def example(timespans=[],
            outdir='',
            prefix='example'):

    times, timesteps = definetimes()

    for timeno, timespan in enumerate(timespans):

        if timespan in times and timespan in timesteps:
            t0, t1, dt = *times[timespan], timesteps[timespan]

            if not outdir:
                outdir = os.curdir

            projectdir = outdir + os.sep + prefix + os.sep + timespan + os.sep
            projectdir = projectdir.replace(os.sep*2, os.sep)

            if not os.path.exists(projectdir):
                os.makedirs(projectdir)

            projectprefix = projectdir + prefix

        else:
            print('Unknown timespan given', timespan)
            continue

        # as small example plot as shown in the text 
        plot(['BKLIDTA1', 'BLERDTA7', 'B2091WT0'],
                 t0=t0, t1=t1, dt=dt,
                 outfile=projectprefix+'_temp_overview.svg',
                 lineopt={'BKLIDTA1': {'color': '#b30000', 'marker': 'o'},
                          'BLERDTA7': {'color': '#008000', 'marker': 'o'},
                          'B2091WT0': {'color': '#3399ff', 'marker': 'o'},
                          },
                 figopt={'secondaryaxis': ['B2091WT0'],
                         'marktropicalnights': True,
                         # 'secondaryyaxissamescale': True,
                         'suppressaxiscolor': False,
                         # 'legalpha': 0.8,
                         },
                 minvalue=-999,
                 )

        # move files to webserver of this timestep
        move2webserver(projectdir,
                       subfolder='projects/'+prefix+'/plots/'+timespan,
                       removenonrefreshed=True,
                       dryrun=False,
                       )


def dolueg2(project=[],
            timespan=[],
            outpurdir='~/dolueg2plots/',
            quiet=True):

    defaultprojects = ['example',
                      ]

    if project:
        if type(project) == str:
            projects = [project]
        else:
            projects = project
    else:
        projects = defaultprojects

    projects = [project if project in defaultprojects else
                print(timespan, 'not defined.',
                      ' please add to projects in dolueg2 python function')
                for project in projects]

    defaulttimespans = ['0day',
                        '1week',
                        '2month',
                        '3year']

    if timespan:
        if type(timespan) == str:
            timespans = [timespan]
        else:
            timespans = timespan
    else:
        timespans = defaulttimespans


    timespans = [timespan if timespan in defaulttimespans else
                print(timespan, 'not defined.',
                      ' please add to timespans in dolueg2 python function(',
                      timespans,')')
                for timespan in timespans]

    for project in projects:
        if not quiet:
            print('Starting ', project, 'for timespans:', timespans)


        globals()[project](timespans=timespans,
                           outdir=outdir)


if __name__ == '__main__':
    print('*'*10, 'HELP for dolueg2', '*'*10)
    print('A list of the different projects/plots that can be created, ',
          'for the dolueg2 homepage. including the moving to the webserver')


    import datetime

    now = datetime.datetime.now()
    print('Running at', now )
    #now = now.replace(hour=0)
    # runs at midnight/every 24 hours, do everything for long timespans
    if now.hour in [0]:
        dolueg2(project=['example', ],
                timespan=['2month', '3year'])

    # runs every six hours do many things
    elif now.hour in list(range(0, 24+6, 6)):
        dolueg2(project=['example'],
                timespan=['1week', '2month'])
        dolueg2(project=['example',],
                timespan=['0day', '1week', '2month'])
    # runs every 3 hours, do a bit
    elif now.hour in list(range(0, 24+3, 3)):
        print('Running all projects, 0day and 1week')
        dolueg2(project=['example',],
                timespan=['0day', '1week',])
    # runs every hour except the ones above, do mainly your main project
    else:
        dolueg2(project=['example', ],
                timespan=['0day', '1week',])
