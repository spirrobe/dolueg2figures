#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# """
# Created on Fri Nov 30 15:53:26 2018
#
# @author: spirro00
# """


def linear(data,
           meta,
           fig=None,
           lineopt=None,
           figopt=None,
           ):

    import datetime
    import html
    import matplotlib.pyplot as plt
    import numpy as np
    from plot.dolueg2plots.gropt import defaultfigopt, defaultlineopt, \
                                        acceptedopt, extendopt, updateopt, \
                                        baseround, unituppercase, \
                                        autoranger, autotimeaxis, \
                                        basefinder

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
    if _figopt['type'] == 'xy':
        _lineopt = extendopt(deflineopt,
                             data.columns.tolist()+[data.index.name])
    else:
        _lineopt = extendopt(deflineopt, data.columns)

    # update the specific codes now
    _lineopt = updateopt(_lineopt, lineopt)

    primcodes, seccodes = [], []

    nbar = len([c for c in data.columns if c in _figopt['barcodes']])
    if nbar:
        aday = datetime.timedelta(hours=24)
        dts = (data.index[1:]-data.index[:-1])
        mindt = min(dts[dts > datetime.timedelta()])
        aday = datetime.timedelta(hours=24)
        barspacing = _figopt['bartotalwidth']
        # this is the whole distance we get to plot into! Divided by two to go forward and backward
        fullbarspace = mindt * barspacing
        halfbarspace = fullbarspace/2
        # this is how much one bar will be and also the distance we go back
        barwidth = fullbarspace / nbar
    else:
        halfbarspace = datetime.timedelta()

    barnotaccepted = ['marker', 'markersize',
                      'markercolor', 'markerfacecolor',
                      'markeredgecolor']
    linenotaccepcted = ['edgecolor', 'secondaryaxis'
                        'bar', ]
    leghandles, leglabels, ibar = [], [], 0

    for c in data.columns:
        if c in _figopt['secondaryaxis']:
            seccodes.append(c)
        else:
            primcodes.append(c)
            _z = data[c]#.dropna(how='all')

            if _figopt['ylog']:
                _z[_z.le(0)] = np.nan

            if c in _figopt['barcodes']:

                # bar doesnt accept quite the same options
                for na in barnotaccepted:
                    if na in _lineopt[c]:
                        _lineopt[c].pop(na)

                if not _figopt['baredge']:
                    if 'edgecolor' in _lineopt[c]:
                        _lineopt[c].pop('edgecolor')
                if 'ls' in _lineopt[c]:
                    _lineopt[c].pop('ls')
                if 'linestyle' in _lineopt[c]:
                    _lineopt[c].pop('linestyle')

                _ = ax.bar(_z.index-halfbarspace+barwidth*ibar,
                           _z,
                           barwidth/aday,
                           align='edge',
#                           edgecolor='k',
                           **_lineopt[c],
                           zorder=1,
                           )
                ibar += 1
                leghandles.append(_[0]), leglabels.append(_lineopt[c]['label'])
            else:
                for na in linenotaccepcted:
                    if na in _lineopt[c]:
                        _lineopt[c].pop(na)

                if _lineopt[c]['ls'] == 'steps':
                    _lineopt[c].pop('ls')

                    _ = ax.step(_z.index, _z,  zorder=1, **_lineopt[c])
                else:

                    _ = ax.plot(_z.index, _z,  zorder=1, **_lineopt[c])

                leghandles.append(_[0]), leglabels.append(_lineopt[c]['label'])

    if _figopt['ylog']:
        ax.set_yscale('log')

    if seccodes:
        ax2 = ax.twinx()


        for c in seccodes:
            _z = data[c]#.dropna(how='all')

            for na in linenotaccepcted:
                if na in _lineopt[c]:
                    _lineopt[c].pop(na)
            if _lineopt[c]['ls'] == 'steps':
                _lineopt[c].pop('ls')
                _ = ax2.step(_z.index, _z, **_lineopt[c], zorder=1)
            else:
                _ = ax2.plot(_z.index, _z, **_lineopt[c], zorder=1)


            leghandles.append(_[0]), leglabels.append(_lineopt[c]['label'])

    if _figopt['secondaryylog']:
        ax2.set_yscale('log')

    if  _figopt['ylabel']:
        ytitle = _figopt['ylabel']
    else:
        ylabels = np.unique([html.unescape(meta[c]['variablename']+
                            ' ['+unituppercase(meta[c]['unit'])+']')
                             for c in primcodes])
        ytitle = '\n'.join((ylabels))

    ax.set_ylabel(ytitle, )

    if type(_figopt['yrange']) == list:
        _yr = _figopt['yrange']

        _eyr = list(ax.get_ylim())
        if _yr[0] > -9999:
            _eyr[0] = _yr[0]
        if _yr[1] > -9999:
            _eyr[1] = _yr[1]

        if _figopt['ylog']:
            _yr = np.round(np.log10([i if j <= -9999 else j
                                     for i,j in zip(_eyr, _yr)]))
            _eyr = np.round(np.log10(_eyr))
            _base = 1
        else:
            _base = basefinder(_eyr[0], _eyr[-1])

        if _yr[0] <= -9999:
            _yr[0] = autoranger(_eyr[0], base=_base, down=True)
        if _yr[1] <= -9999:
            _yr[1] = autoranger(_eyr[1], base=_base, up=True)

        if _yr[0] == _yr[1]:
            _yr[1] += 1

        if _figopt['yticks'] is None:
            yticks= np.arange(_yr[0], _yr[1]+_base, _base) #_figopt['yticks']))
        else:
            yticks = np.linspace(_yr[0],_yr[1], _figopt['yticks'])

        if _figopt['ylog']:
            _yr = 10**_yr
            yticks = 10**yticks

        # rather dont add too many ticks and keep any possibly ugly ones
        if len(yticks) >= 10:
            pass
        else:
            ax.set_yticks(yticks)
        ax.set_ylim(_yr)

    if seccodes:


        if  _figopt['secondaryylabel']:
            ytitle2 = _figopt['secondaryylabel']
        else:
            ylabels2 = np.unique([html.unescape(meta[c]['variablename']+
                            '['+unituppercase(meta[c]['unit'])+']')
                             for c in seccodes])
            ytitle2 = '\n'.join([html.unescape(c)
                                 for c in ylabels2])

        ax2.set_ylabel(html.unescape(ytitle2))

        if type(_figopt['secondaryaxisyrange']) == list:
            _yr2 = _figopt['secondaryaxisyrange']
            _eyr2 = ax2.get_ylim()
            _base = basefinder(_eyr2[0], _eyr2[1])

            if _yr2[0] <= -9999:
                _yr2[0] = autoranger(_eyr2[0], base=_base, down=True)
            if _yr2[1] <= -9999:
                _yr2[1] = autoranger(_eyr2[1], base=_base, up=True)

            if _figopt['secondaryyaxissamescale']:
                _yr2 = ax.get_ylim()
                ax2.set_ylim(_yr2)
            else:
                ax2.set_ylim(_yr2)



            if _figopt['secondaryaxisticks']:
                ax2.set_yticks(np.linspace(_yr2[0], _yr2[1], _figopt['secondaryaxisticks']))

            else:
                plt.draw()
                #ax2.set_yticks(np.linspace(_yr2[0], _yr2[1], len(ax.get_yticks())))
                _yst = (_yr2[1]-_yr2[0])  / _base
                if _yst % len(ax.get_yticks()) == 0:
                    #ax2.set_yticks(np.arange(_yr2[0], _yr2[1], len(ax.get_yticks())))
                    ax2.set_yticks(np.arange(_yr2[0], _yr2[1]+_base, _base))
                else:
                    ax2.set_yticks(np.linspace(_yr2[0], _yr2[1], len(ax.get_yticks())))

            if _figopt['secondaryaxislabels']:
                ax2.set_yticklabels(_figopt['secondaryaxislabels'][:len(ax2.get_yticks())])



    if _figopt['type'] == 'xy':
        xlabel = meta[data.index.name]['variablename']
        xunits = unituppercase(meta[data.index.name]['unit'])
        xtitle = html.unescape(xlabel+' ['+xunits+']')

        ax.set_xlabel(xtitle)


    else:
        ax.set_xlabel(_figopt['xlabel'])

    if not _figopt['suppressaxiscolor'] and len(np.unique([_lineopt[i]['color'] for i in primcodes])) == 1:
        primcol = _lineopt[primcodes[0]]['color']
        ax.spines["left"].set_edgecolor(primcol)
        ax.tick_params(axis='y', colors=primcol)

    if seccodes and not _figopt['suppressaxiscolor'] and len(np.unique([_lineopt[i]['color'] for i in seccodes])) == 1:
        seccol = _lineopt[seccodes[0]]['color']
        ax2.spines["right"].set_edgecolor(seccol )
        ax2.tick_params(axis='y', colors=seccol )


    if type(_figopt['xrange']) == list and _figopt['type'] == 'xy':
        _xr = _figopt['xrange']
        _exr = ax.get_xlim()

        if _xr[0] <= -9999:
            _xr[0] = autoranger(_exr[0], base=_base, down=True)
        if _xr[1] <= -9999:
            _xr[1] = autoranger(_exr[1], base=_base, up=True)

        _base = basefinder(_exr[0], _exr[1])

        if _xr[0] <= -9999:
            _xr[0] = autoranger(_exr[0], base=_base, down=True)
        if _xr[1] <= -9999:
            _xr[1] = autoranger(_exr[1], base=_base, up=True)

        ax.set_xlim(_xr)
        if _figopt['yticks'] is None:
            ax.set_xticks(np.arange(_xr[0], _xr[1]+_base, _base)) #_figopt['yticks']))
        else:
            ax.set_xticks(np.linspace(_xr[0],_xr[1], _figopt['xticks']))
        # ax.set_xticks(np.linspace(_xr[0],_xr[1], _figopt['xticks']))

    else:
        # trick the autoranger to use the second index since we needed that one
        # initially to make the plot, but not for the autoranging
        autotimeaxis(data.index[1:], ax, extraspace=halfbarspace)

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


    legtitle = _figopt['legtitle']
    if not _figopt['suppresslegend']:
        if seccodes:
            lax = ax2
        else:
            lax = ax
        leg = lax.legend(leghandles, leglabels,
                         title=legtitle,
                         fontsize=_figopt['legfontsize'],
#                         mode='expand',
                         loc='upper left',
                         framealpha=_figopt['legalpha'],
                         numpoints=2,
                         )
        leg._legend_box.align = "left"
        leg.set_zorder(3)

    return fig, ax


if __name__ == '__main__':
    print('*'*10, 'HELP for linear', '*'*10)
    print('Creates a linear plot of passed in data time series')
