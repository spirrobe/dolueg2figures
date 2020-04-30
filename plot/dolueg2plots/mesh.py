#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Created on %(date)s
#
# @author: %(username)s


def mesh(data,
         meta=None,
         y=None,
         yrange=None,
         zmaskrange=None,
         fig=None,
         zrange=None,
         lineopt=None,
         figopt=None,
         overlaycontour=False,
         contouralpha=0.9,
         contourstep=1,
         contourcolor=['w', 'k'],
         valuerange='auto',
         cmap='viridis',
         title=None,
         figtitle=None,
         **kwargs,
         ):

    import html
    # import datetime
    # import matplotlib.dates as mdates
    import matplotlib as mpl
    import numpy as np
    import matplotlib.pyplot as plt
    # import scipy.signal as sc
    # import matplotlib
    import pandas as pd

    from plot.dolueg2plots.gropt import defaultfigopt, defaultlineopt, \
                                        acceptedopt, extendopt, updateopt, \
                                        baseround, unituppercase, \
                                        autoranger, autotimeaxis, \
                                        basefinder

    if figtitle:
        if figopt is None:
            figopt = {'figtitle': figtitle}
        else:
            figopt['figtitle'] = figtitle

    if title:
        if figopt is None:
            figopt = {'zlabel': title}
        else:
            figopt['zlabel'] = title

    if yrange:
        if figopt is None:
            figopt = {'yrange': yrange}
        else:
            figopt['yrange'] = yrange

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

    axpos = ax.get_position().extents
    cax = fig.add_axes([axpos[2]+0.01,
                        axpos[1],
                        0.015,
                        axpos[3]-axpos[1]])

    if type(data) != pd.DataFrame:
        data = data.to_frame()

    _z = data.copy()

    # pcolormesh cant properly handle timezoneaware indexes, so convert to UTC
    # if the dataframe is timezoneaware and then drop it.
    if _z.index.tz is not None:
        _z = _z.tz_convert('UTC').tz_localize(None)

    if _figopt['zlog']:
        norm = mpl.colors.LogNorm()
        _z[np.isnan(_z)] = 0
        _z[_z <= 0] = 0
        _z = np.ma.masked_array(_z.values, mask=(_z.values == 0))

    else:
        norm = mpl.colors.Normalize()
        _z = _z.values

    if valuerange == 'auto':
        if _figopt['zlog']:
            vmin = 10**np.floor(np.log10(np.nanmin(np.abs(_z))))
            vmax = 10**np.ceil(np.log10(np.nanmax(np.abs(_z))))
        else:
            vmin = -np.ceil(np.nanmax(np.abs(_z)))
            vmax = np.ceil(np.nanmax(np.abs(_z)))

    else:
        if type(valuerange) == list:
            vmin, vmax = valuerange
        else:
            vmin, vmax = -valuerange, valuerange

    if y is None or len(y) != len(data.columns):
        if meta is None:
            _y = np.arange(len(data.columns))
        else:
            _y = [meta[i]['messhoehe'] for i in data.columns]
    else:
        _y = y

    #the proper naming of the timezone has to be done on the axis

    mesh = ax.pcolormesh(data.index.tz_localize(None),
                         _y, _z.T,
                         cmap=cmap,
                         vmin=vmin,
                         vmax=vmax,
                         norm=norm,
                         rasterized=True,
                         edgecolors='face',)

    if overlaycontour:
        if _figopt['zlog']:
            clevels = np.geomspace(vmin,
                                   vmax,
                                   # equal to expoenents of vmax - vmin
                                   int((np.log10(vmax/vmin))/contourstep+1),
                                   )
        else:
            clevels = np.arange(vmin, vmax + contourstep, contourstep)
        #the proper naming of the timezone has to be done on the axis
        if type(contourcolor) == str:
            contourcolor = [contourcolor]

        for i, c in enumerate(contourcolor):
            ax.contour(data.index.tz_localize(None),
                       _y, _z.T,
                       colors=c,
#                       colors=contourcolor,
                       levels=clevels,
                       alpha=contouralpha,
                       linewidths=len(contourcolor)-0.5-i*0.75)

    # trick the autoranger to use the second index since we needed that one
    # initially to make the plot, but not for the autoranging
    rto, xform = autotimeaxis(data.index[1:].tz_localize(None), ax=ax)
    # xaxisformat = mdates.DateFormatter(xform)
    # ax.xaxis.set_major_formatter(xaxisformat)
    # ax.grid(color='k', lw=0.5, axis='both', alpha=0.5)

    if _figopt['zlabel']:
        ztitle = _figopt['zlabel']
    else:
        if meta is None:
            ztitle = _figopt['zlabel']
        else:
            zlabels = np.unique([html.unescape(meta[c]['name'] +
                                                    ' ['+meta[c]['einheit']+']')
                                for c in data.columns])
            ztitle = '\n'.join((zlabels))

    ztitle = unituppercase(ztitle)

    ax.set_ylabel('Measurement height [m]', )

    if type(_figopt['yrange']) == list:
        _yr = _figopt['yrange']
        _eyr = ax.get_ylim()

        _base = basefinder(_eyr[0], _eyr[1])

        if _yr[0] <= -9999:
            _yr[0] = autoranger(_eyr[0], base=_base, down=True)
        if _yr[1] <= -9999:
            _yr[1] = autoranger(_eyr[1], base=_base, up=(_eyr[1] % _base != 0))

        if _yr[0] == _yr[1]:
            _yr[1] += 1

        ax.set_ylim(_yr)

        if _figopt['yticks'] is None:
            ax.set_yticks(np.arange(_yr[0], _yr[1]+_base, _base)) #_figopt['yticks']))
        else:
            ax.set_yticks(np.linspace(_yr[0],_yr[1], _figopt['yticks']))

            # ax.set_yticks(np.linspace(_yr[0],_yr[1], _figopt['yticks']))


    if _figopt['zlog']:
        cbarlevels = np.geomspace(vmin,
                                  vmax,
                                  # equal to expoenents of vmax - vmin
                                  int((np.log10(vmax/vmin))/contourstep)+1,
                                  )
    else:
        cbarlevels = np.arange(vmin, vmax + contourstep, contourstep)

    cbar = plt.colorbar(mesh,
                        orientation='vertical',
                        cax=cax,
                        # pad=0.025,
                        # aspect=40,
                        ticks=cbarlevels,
                        label=ztitle)

    ax.set_xlabel('Time (UTC)')

    if _figopt['figtitle']:
        ax.text(0.01 * np.diff(ax.get_xlim())+ax.get_xlim()[0],
                ax.get_ylim()[1] - 0.05 * np.diff(ax.get_ylim()),
                _figopt['figtitle'],
                ha='left', va='center',
                zorder=20, fontsize=_figopt['fontsize'],
                bbox=dict(boxstyle='round', fc="w", ec="k",),
                )

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
    print('*'*10, 'HELP for main', '*'*10)
    print('Describe shortly what this is supposed to do')
    print('Maybe help out a bit with keyword to make it clearer for people',)

#from mcr.sql.util import getdata
#
#bsheight = 1000
#bsoverlaprange = 50
#bsstep = 5
#ceilobscodes = ['bklibs' + str(i).zfill(4)
#                for i in range(bsoverlaprange//5, bsheight//5+1)]
#
#data, meta = getdata(ceilobscodes, t0='*-7', t1='*-1')

    #mesh(data,
    #     meta=meta,
    ##     y=[meta[i]['messhoehe'] for i in data.columns],
    ##     valuerange=[10**1,10**5],
    ##     figtitle='Backscatter',
    #     cmap='jet',
    #     overlaycontour=False,
    ##     yrange=[-50,1100],
    ##     title='Temperature Difference [°C]',
    #     )

