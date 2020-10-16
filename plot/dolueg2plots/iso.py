#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# """
# Created on Fri Nov 30 15:53:19 2018
#
# @author: spirro00
# """


#from mcr.sql.util import getdata
#
#if 'data' not in locals():
#	data, meta = getdata(['BLERDTA1', 'BBINDTA7'])
#

def iso(data,
        fig=None,
        lineopt=None,
        figopt=None,
        step=1,
        makemesh=True,
        smoothdata=True,
        overlaycontour=False,
        contourstep=2,
        contouralpha=0.8,
        contourcolor=['w','k'],
        # valuerange='auto',
        noagg=True,
        cmap='RdBu_r',
        #title='Values',
        #figtitle='Isopleths',
        **kwargs,
        ):

    import datetime
    import matplotlib.dates as mdates
    import numpy as np
    import matplotlib.pyplot as plt
    import scipy.signal as sc
    import matplotlib as mpl
    import pandas as pd


    from plot.dolueg2plots.gropt import defaultfigopt, defaultlineopt, \
                                        acceptedopt, extendopt, updateopt, \
                                        baseround, basefinder, \
                                        autoranger, autotimeaxis


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

    cax = fig.add_axes([axpos[2]+0.01, axpos[1],
                        0.03,
                        axpos[3]-axpos[1]])


    if type(data) != pd.DataFrame:
        data = data.to_frame()

    if len(data.columns) > 1:
        print('Please pass in a single column dataframe.',
              'Defaulting to first columns')
        _data = data[data.columns[0]].to_frame()
        data = _data.copy()


    if noagg:
        # print(data.index.drop_duplicates())
        data = data[data.index == data.index.drop_duplicates()]
        _x = np.unique(data.index.date)
        _y = np.unique(data.index.time)
        shp = [_x.shape[0], _y.shape[0]]
        dts = data.index[1:] - data.index[:-1]
        dts = min(dts[dts > datetime.timedelta()])
        _z = data.resample(dts, closed = 'right', label = 'right').bfill()

        if len(_z[_z.index.date == _x[0]]) != 144:
            _z = _z[_x[0] + datetime.timedelta(days = 1):]
            _z = _z.tail(len(_z) - 1)
            shp[0] -= 1

        if len(_z[_z.index.date == _x[-1]]) != 144:
            _z = _z[:_x[-1] - datetime.timedelta(days = 1)]

        _x = np.unique(_z.index.date)[:-1]
        shp = (_x.shape[0], _y.shape[0])

        _z = np.reshape(_z.values, shp).T

        basedate = datetime.datetime(2004, 1, 1, 0, 0, 0)
        _y = [datetime.datetime.combine(basedate.date(), i) for i in _y]
        _y.append(_y[-1] + datetime.timedelta(minutes = 10))
        _z = np.vstack((_z, _z[0, :]))
        if smoothdata:
            _z = sc.medfilt2d(_z, kernel_size = [3, 5])
    else:

        z = data.groupby(by = [data.index.dayofyear,
                            data.index.time]).mean()
        shp = (z.index.levels[0].shape[0], z.index.levels[1].shape[0])
        basedate = datetime.datetime(2004, 1, 1, 0, 0, 0)

        _x = z.index.levels[0].tolist()
        _x = [basedate + datetime.timedelta(days = i - 1) for i in _x]
        _x.append(_x[-1] + datetime.timedelta(days = 1))

        _y = z.index.levels[1].tolist()
        _y = [datetime.datetime.combine(basedate.date(), i) for i in _y]
        _y.append(_y[-1] + datetime.timedelta(minutes = 10))

        _z = np.reshape(z.values, shp).T
        _z = sc.medfilt2d(_z, kernel_size = 3)
        _z = np.vstack((_z, _z[0, :]))
        _z = np.hstack((_z, _z[:, 0][np.newaxis].T))

    vmin, vmax = -np.ceil(np.abs(_z).max()), np.ceil(np.abs(_z).max())

    if type(_figopt['zrange']) == list:
        _zr = _figopt['zrange']

        _ezr = [vmin, vmax]
        if _zr[0] > -9999:
            _ezr[0] = _zr[0]
        if _zr[1] > -9999:
            _ezr[1] = _zr[1]

        _base = basefinder(_ezr[0], _ezr[-1])

        if _zr[0] <= -9999:
            _zr[0] = autoranger(_ezr[0], base=_base, down=True)
        if _zr[1] <= -9999:
            _zr[1] = autoranger(_ezr[1], base=_base, up=True)


        if _zr[0] == _zr[1]:
            _zr[1] += 1

        if _figopt['zticks'] is None:
            cbticks = np.arange(_zr[0], _zr[1]+_base, _base)
        else:
            cbticks = np.linspace(_zr[0],_zr[1], _figopt['zticks'])

        # adjust vmin/vmax accordingly
        vmin, vmax = _zr[0], _zr[1]

    else:
        if _figopt['zticks'] is None:
            _base = basefinder(vmin, vmax)
            cbticks = np.arange(vmin, vmax + _base, _base)
        else:
            cbticks = np.linspace(vmin, vmax, _figopt['zticks'])

        # do not adjust vmin/vmax but we still need the colorbarticks
        cbticks = np.linspace(vmin, vmax, cbticks)

    if _figopt['zlog']:
        norm = mpl.colors.LogNorm(vmin=vmin, vmax=vmax)
        _z[_z <= 0] = np.nan
    else:
        norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)

    if noagg:
        rto, xform = autotimeaxis(data.index,)
        yaxisformat = mdates.DateFormatter('%H:%M')
#        xaxisformat = mdates.DateFormatter('%d.%m\n%Y')
        xaxisformat = mdates.DateFormatter(xform)
    else:
        yaxisformat = mdates.DateFormatter('%H:%M')
        xaxisformat = mdates.DateFormatter('%d.%m')

    _z = np.ma.masked_array(_z, mask=(np.isnan(_z)))
    _x = [mdates.date2num(i) for i in _x]

    if makemesh:
        mesh = ax.pcolormesh(_x, _y, _z, cmap = cmap,
                             vmin=vmin,
                             vmax=vmax,
                             norm=norm,
                             shading='flat',
                             edgecolors='face',
                             rasterized=True)
    else:
        if _figopt['zlog']:
            # in case of the default 1 step but a log value range autoadjust
            if step == 1 and np.log10(vmax/vmin) < 5:
                step *= 10
            levels = np.geomspace(vmin,
                                  vmax,
                                  # equal to expoenents of vmax - vmin
                                  int((np.log10(vmax/vmin))/step+1),
                                  )
        else:
            levels = np.arange(vmin, vmax + step, step)
        mesh = ax.contourf(_x, _y, _z,
                           cmap=cmap,
                           levels=levels,
                           norm=norm,
                           rasterized=True)

    if overlaycontour:
        if _figopt['zlog']:
            clevels = np.geomspace(vmin,
                                  vmax,
                                  # equal to expoenents of vmax - vmin
                                  int((np.log10(vmax/vmin))/contourstep+1),
                                  )
        else:
            clevels = np.arange(vmin, vmax + step, step)
        for i, c in enumerate(contourcolor):
            ax.contour(_x,
                       _y,
                       _z,
                       colors=c,
                       levels=clevels,
                       alpha=contouralpha,
                       linewidths=len(contourcolor)-i)


    ax.xaxis.set_major_formatter(xaxisformat)
    ax.yaxis.set_major_formatter(yaxisformat)

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


    plt.colorbar(mesh,
                 orientation='vertical',
                 cax=cax,
                 pad=0.025,
                 aspect=40,
                 ticks=cbticks,
                 label=_figopt['ylabel'])


    ax.set_xlabel('Day of year')
    ax.set_ylabel('Time of day')

    legx = ax.get_xlim()
    legx = legx[0]+0.025*(legx[1]-legx[0])

    legy = ax.get_ylim()
    legy = legy[0]+0.975*(legy[1]-legy[0])
    legtext = ''

    if _figopt['figtitle']:
        legtext += _figopt['figtitle']

    if _figopt['legtitle']:
        if legtext:
            legtext += '\n'
        legtext += _figopt['legtitle']

    ax.text(legx, legy,
            legtext,
            ha='left',
            va='top',
            # framealpha=_figopt['legalpha'],
            fontsize=_figopt['legfontsize'],
            bbox = dict(boxstyle='round,pad=0.6',
                        fc="w",
                        ec="w",
                        alpha=_figopt['legalpha'],
                        )
              )

    return fig, ax

if __name__ == '__main__':
	print('*' * 10, 'HELP for main', '*' * 10)
	print('Describe shortly what this is supposed to do')
	print('Maybe help out a bit with keyword to make it clearer for people', )
#    iso(data['BKLIDTA1'] - data['BLERDTA1'],
#        simple=False,
#        noagg=False,
#        step=0.1,
#        contourstep = 0.5,
#        figtitle = 'UHI effect in Basel (City - Rural)',
#        title = 'Temperature Difference [°C]',
#        valuerange=[-8,8],
#        makemesh=True,
#        )

#iso(data['BBINDTA7'] - data['BLERDTA1'],
#    simple = True,
#    noagg = False,
#    step = 0.1,
#    figtitle = 'UHI effect in Basel (City - Rural)',
#    title = 'Temperature Difference [°C]',
#    #    makemesh=True,
#    )
## iso(data['BKLIDTA1']-data['BLERDTA1'], simple=True, noagg=True, makemesh=True,valuerange=[-5,5])
# iso(data['BKLIDTA1']-data['BLERDTA1'], simple=True, noagg=False,)
