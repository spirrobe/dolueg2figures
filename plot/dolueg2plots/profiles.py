#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# """
# Created on Fri Nov 30 15:53:26 2018
#
# @author: spirro00
# """


def profiles(data,
             heights=None,
             fig=None,
             lineopt=None,
             figopt=None,
             offset=None,
             quiet=True,
             profileconnect=True,
             # for the assumed default of 1 day make 1 hour
             majorinterval=1,
             # for the assumed default of 1 day make 30 minutes
             minorinterval=2,
             label='',
             **kwargs
             ):

    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import datetime


    from plot.dolueg2plots.gropt import defaultfigopt, defaultlineopt, \
                                        updateopt,\
                                        baseround, \
                                        autoranger, autotimeaxis,\
                                        acceptedopt, extendopt


    if heights is None:
        if not quiet:
            print('Heights autoset to monotonic increasing range from 1 up.',
                  'Pass heights=[...] to set points correctly')
        heights = list(range(1, len(data.columns)+1))

    _figopt = defaultfigopt()
    if figopt is not None:
        for i in figopt:
            _figopt[i] = figopt[i]

    if fig is None:
        fig, ax = plt.subplots(figsize=_figopt['figsize'])
    elif len(fig) == 2:
        fig, ax = fig
    else:
        ax = fig.gca()

    # get the default options
    deflineopt = defaultlineopt()

    # make sure they are extended to all the codes
    _lineopt = extendopt(deflineopt, data.columns)

    # update the specific codes now
    _lineopt = updateopt(_lineopt, lineopt)

    sorted_heights = sorted([i for i in zip(heights, data.columns)])
    data = data[[i[1] for i in sorted_heights]]
    # ncols = len(data.columns)

    # get a maximum absolute difference that we use to scale according to time
    # maxdiff = np.ceil((data.max(axis=1)-data.min(axis=1)).abs().max())
    # print(data.max(axis=1), data.min(axis=1))

    maxdiff = np.ceil(data.max(axis=1)-data.min(axis=1)).abs().max()
    maxdiff = int(maxdiff)
    dt = min(data.index[1:] - data.index[:-1])

    if maxdiff == 0:
        print('Warning: Differences in data are non-existent.',
              'Code combination with problems:', data.columns.tolist())
        maxdiff = 1
    # because we go to both sides
    scaling = dt.total_seconds() / maxdiff * 8
    asecond = datetime.timedelta(seconds=1)

    diffs = data.diff(axis=1).fillna(0).cumsum(axis=1)

    timediffs = diffs * scaling * asecond

    profiledata = pd.DataFrame(data=timediffs,
                               columns=data.columns,
                               index=data.index)

    profiledata += np.reshape(np.tile(data.index,len(heights)),
                              (len(heights), len(data.index),)).T

    linenotaccepcted = ['edgecolor',
                        ]

    for na in linenotaccepcted:
        if na in _lineopt[data.columns[0]]:
            _lineopt[data.columns[0]].pop(na)

    if profileconnect:
        gropt_profcon = _lineopt[data.columns[0]].copy()
        gropt_profcon['ls'] = ':'
        gropt_profcon.pop('marker')

    for recno in range(len(profiledata)):
        ax.plot(profiledata.values[recno,:],
                heights,
                **_lineopt[data.columns[0]]
                )

        if profileconnect:
            ax.plot([profiledata.values[recno, -1],
                      profiledata.values[recno, -1]],
                    [heights[0]] + [heights[-1]],
                    **gropt_profcon
                    )

            ax.plot(profiledata.values[recno, -1],
                    heights[0],
                    **gropt_profcon,
                    marker='x',
                    )

    autotimeaxis(data.index, ax,
                 extraspace=dt,
                 majorinterval=majorinterval,
                 minorinterval=minorinterval)

    ylim = [baseround(min(heights), down=True),
            baseround(max(heights), up=True)]

    ax.set_ylim(ylim)

    ap = dict(arrowstyle="<->, head_width=0.6, head_length=1")
    ax.annotate("",
                xy=(data.index[0], ylim[-1]-(ylim[-1]-heights[-1])/2),
                xytext=(data.index[0]+dt*4, ylim[-1]-(ylim[-1]-heights[-1])/2),
                arrowprops=ap,)

    if '[' in label:
        label = str(maxdiff)+' '+label.lstrip()
    else:
        label = str(maxdiff)+' ['+label+']'

    ax.text(data.index[0]+dt*2,
            ylim[-1]-0.5*(ylim[-1]-heights[-1])/2,
            label,
            ha='center', va='center',
            fontdict={'fontsize': 14, 'fontweight': 'normal'}
            )

    ax.set_yticks(np.arange(ylim[0], ylim[1]+5, 5))
    ax.set_ylabel('Height [m]')
    ax.set_xlabel(_figopt['xlabel'])

    if _figopt['grid']:
        ax.grid(c=_figopt['gridlinecolor'],
                ls=_figopt['gridylinestyle'],
                lw=2*_figopt['gridlinewidth'],
                which='major',
                axis='y')

        ax.grid(c=_figopt['gridlinecolor'],
                ls=_figopt['gridylinestyle'],
                lw=0.5*_figopt['gridlinewidth'],
                which='minor',
                axis='y')

        ax.grid(c=_figopt['gridlinecolor'],
                ls=_figopt['gridxlinestyle'],
                lw=0.5*_figopt['gridlinewidth'],
                which='minor',
                axis='x')
        ax.grid(c=_figopt['gridlinecolor'],
                ls=_figopt['gridxlinestyle'],
                lw=2*_figopt['gridlinewidth'],
                which='major',
                axis='x')

    return fig, ax


if __name__ == '__main__':
    print('*'*10, 'HELP for profiles', '*'*10)
    print('Creates profiles according to measurement height')
    print('Maybe help out a bit with keyword to make it clearer for people',)
