#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# """
# Created on Fri Nov 30 15:54:52 2018
#
# @author: spirro00
# """


def plot(codes,
         t0='min',
         t1='max',
         dt=None,
         how={},
         plottype='linear',
         outfile='',
         indexcode=None,
         quiet=True,
         fig=None,
         figsize=[7, 5.25],
         figopt=None,
         lineopt=None,
         colors=None,
         offset=[],
         multiplier=[],
         minvalue=None,
         maxvalue=None,
         zlog=False,
         returnfig=False,
         slope=False,
         **kwargs):

    import numpy as np
    import datetime
    import pandas as pd
    import matplotlib as mpl
    import html

    mpl.use('Agg')
    from sql.util import getdata
    from plot.dolueg2plots.windmap import windmap
    from plot.dolueg2plots.stationmap import stationmap
    from plot.dolueg2plots.iso import iso
    from plot.dolueg2plots.profiles import profiles
    from plot.dolueg2plots.mesh import mesh
    from plot.dolueg2plots.linear import linear

    from plot.dolueg2plots.watermark import watermark
    from plot.dolueg2plots.gropt import defaultfigopt, defaultlineopt, \
                                        acceptedopt, extendopt, updateopt, \
                                        sunpos, defaultct, defaultwindcolor, \
                                        unituppercase

    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    from pandas.plotting import register_matplotlib_converters
    register_matplotlib_converters()

    if figopt is None:
        _figopt = defaultfigopt()
    else:
        _figopt = defaultfigopt()
        for key in figopt:
            if type(figopt[key]) in [dict, list]:
                _figopt[key] = figopt[key].copy()
            else:
                _figopt[key] = figopt[key]

    if fig is None and figsize:
        fig = plt.subplots(figsize=_figopt['figsize'],
                           dpi =_figopt['figdpi']
#                           constrained_layout=True,
                           )

        fig[0].tight_layout()

    if zlog:
        _figopt['zlog'] = zlog

    plottype = plottype.lower()

    types = [['xy', 'timeseries', 'linear'],
             ['profile', 'profiles'],
             ['iso', 'ispohypses', 'isolines'],
             ['wind', 'windrose', 'windmap'],
             ['stationnetwork', 'stationnetworks', 'station', 'stationmap'],
             ['contour', 'mesh', ],
             ]

    # windmap / stationnetwork
    if plottype in types[3] or plottype in types[4]:
        if fig[0].get_figwidth() != fig[0].get_figheight():
            fmax = max([fig[0].get_figwidth(), fig[0].get_figheight()])
            fig[0].set_figwidth(fmax)
            fig[0].set_figheight(fmax)

    if plottype in types[5]:# or plottype in types[2]:
        includestart = True
    else:
        includestart = False


    if type(codes) == str:
        codes = [codes]

    data, meta = getdata(codes,
                         t0=t0,
                         t1=t1,
                         dt=dt,
                         how=how,
                         includestart=includestart,)

    if not (data is None or data is False) and _figopt['ylog']:
        data[data.le(0)] = np.nan

    # need at lost some data to decide on the barwidth, if this is not give
    # report missing data (only for barcodes!)
    if not (data is None or data is False):


        missingbarcodes = [c for c in _figopt['barcodes'] if c not in data.columns]
        if missingbarcodes:
            print('These barcodes were given wrong in the call and have been removed',
                  missingbarcodes)
        _figopt['barcodes'] = [c for c in _figopt['barcodes'] if c in data.columns]

        if _figopt['barcodes'] and len(data[_figopt['barcodes']].dropna(how='all').index) <= 2:
            data[data.columns] = np.nan

        # too few data to be sensible, forget it
        if _figopt['barcodes'] and len(data[_figopt['barcodes']].dropna(how='all').index) <= 3:
            print('Not enough data for barcodes plot. Parameters were:')
            print(t0, t1, dt, codes)
            data = None

    # check that we didnt get invalid data
    if data is None or data is False or meta is None or data.dropna(how='all').empty:
        if data is None or data is False or data.dropna(how='all').empty:
            errormsg = 'NO VALID VALUES YET IN DATABASE FOR \n'
            for code in codes:
                errormsg += code
                if meta and code in meta:
                    errormsg  += ' in ' + meta[code]['sqldb'] + '\n'
                else:
                    errormsg  += ' does not exist in the database\n'
            errormsg += '\nTimestamp t0:'+ str(t0) + '\n'
            errormsg += 'Timestamp t1:'+ str(t1)
        else:
            print('Passed codes do not exist, please fix your call:', codes)
            errormsg = 'CODES DO NOT EXIST \n\n'
            errormsg += '\n'.join(codes)

        if data is None or data is False:
            pass
        else:

            errormsg += '\n\nGiven parameters were\n'
            errormsg += 'Timestamp t0: ' + data.index[0].strftime('%d %b %Y %H:%M:%S')+'\n'
            errormsg += 'Timestamp t1: ' + data.index[-1].strftime('%d %b %Y %H:%M:%S')+'\n'

        fig[0].text(0.5, 0.5, errormsg, ha='center', va='center', fontsize=16)
        plt.axis('off')
        if outfile:
            fig[0].savefig(outfile, rasterized=True)

        if returnfig:
            return fig
        else:
            plt.close(fig[0])
            return

    localtz = datetime.datetime.now().astimezone().tzinfo
    datatz = str(data.tz_convert(localtz).index.tzinfo)
    data = data.tz_convert(localtz).tz_localize(None)

    origcodes = codes.copy()
    if sorted(codes) == sorted(data.columns.tolist()):
        pass
    else:
        codes = data.columns

        if figopt is None:
            pass
        else:
            figremove = []
            for newcode in codes:
                if newcode.split('_')[0] in figopt:
                    figopt[newcode] = figopt[newcode.split('_')[0]]
                    figremove.append(newcode.split('_')[0])
            if figremove:
                for i in figremove:
                    if i in figopt:
                        del figopt[i]

        if lineopt is None:
            pass
        else:
            lineoptremove = []

            for newcode in codes:
                if '_' in newcode and newcode.split('_')[0] in lineopt:
                    lineopt[newcode] = lineopt[newcode.split('_')[0]]
                    lineoptremove.append(newcode.split('_')[0])

            if lineoptremove:
                for i in lineoptremove:
                    if i in lineopt:
                        del lineopt[i]

    if minvalue:
        data[data.lt(minvalue)] = np.nan

    if maxvalue:
        data[data.gt(maxvalue)] = np.nan

    if _figopt['cumulativecodes']:
        misscumulativecodes = []
        for code in _figopt['cumulativecodes']:
            # several aggregations chosen
            if code in data:
                data[code] = data[code].cumsum()
            else:
                misscumulativecodes.append(code)
        if misscumulativecodes:
            print('These cumulative codes were given but are non existing in the selected data',
                  misscumulativecodes )

    if slope:
        data = data.diff(axis=1)

    _lineopt = defaultlineopt(keys=data.columns)

    if lineopt is None:
        pass
    else:
        # update the specific codes now
        _lineopt = updateopt(_lineopt, lineopt)

    if colors is not None:
        if type(colors) is dict:
            for c in colors:
                if c in _lineopt:
                    _lineopt[c]['color'] = colors[c]
        elif type(colors) is list:
            for cno, c in enumerate(origcodes):
                if c in _lineopt:
                    _lineopt[c]['color'] = colors[cno % len(colors)]
        elif type(colors) == str and '#' in colors:
            for c in origcodes:
                if c in _lineopt:
                    _lineopt[c]['color'] = colors
        elif type(colors) in [int, float]:
            for c in origcodes:
                if c in _lineopt:
                    _lineopt[c]['color'] = colors

    # in case we did a mathoperation, the meta will contain all codes
    # which makes sense despite the operation, i.e. urban - rural
    # but we have to limit it to be the same length, this may cause problems

    if sorted(list(meta.keys())) != sorted(codes):
        newmeta = {}
        for codeno, code in enumerate(codes):
            ops = ['+', '-', '/', '*']
            opword = {'+': 'sum',
                      '-': 'difference',
                      '/': 'ratio',
                      '*': 'product'}
            for op in ops:
                _code = code.split(op)
                if len(_code) > 1:
                    break

            if code in meta and len(_code) == 1:
                newmeta[code] = meta[code].copy()
            elif _code[0] in meta and _code[1] in meta:
                # both are found, combine relevant information
                # i.e. what we need for legend, consisting of
                # the below, excluding the numeric types
                # 'messhoehe', 'lat', 'lon'
                # as it doesnt make sense to have two coordinates when
                # math opeation took place


                newmeta[code] = meta[_code[0]]
                newmeta[code]['variable'] += ' '+opword[op]
                newmeta[code]['name_sdt'] += ' and '+ meta[_code[1]]['name_sdt']
                newmeta[code]['geraet'] += ' and '+ meta[_code[1]]['geraet']
                newmeta[code]['aggregation'] += ' and '+ meta[_code[1]]['aggregation']
                if meta[_code[1]]['einheit'] != meta[_code[0]]['einheit']:
                    newmeta[code]['einheit'] += ' '+opword[op]+' ' + meta[_code[1]]['einheit']


            elif _code[0] in meta or _code[1] in meta:
                # just take whichever we found at least
                if _code[0] in meta:
                    newmeta[_code[0]] = meta[_code[0]]
                else:
                    newmeta[_code[1]] = meta[_code[1]]
            else:
                print(code, 'not in meta')
            if len(newmeta) == len(codes):
                break
        meta = newmeta


    if _lineopt is not None:
        # ensure we handle indexed colors
        defaultcolors = defaultct()#[2:]
        checkcol = ['markerfacecolor',
                    'color',
                    ]
        for code in codes:
            for ccol in checkcol:
                if type(_lineopt[code][ccol]) in [int, float]:
                    _lineopt[code][ccol] = defaultcolors[_lineopt[code][ccol] % len(defaultcolors)]
                elif type(_lineopt[code][ccol]) == list and len(_lineopt[code][ccol]) == 1:
                    _lineopt[code][ccol] = defaultcolors[_lineopt[code][ccol][0] % len(defaultcolors)]
                if mpl.colors.is_color_like(_lineopt[code][ccol]):
                    pass
                else:
                    print('Not a valid color code for',
                          code, _lineopt[code][ccol],
                          'fallback to black')
                    _lineopt[code][ccol] = '#000000'


    if offset:
        if type(offset) == list:
            if len(offset) != len(codes) and not len(offset) == 1:
                print('Ignoring offset as it\'s length is not matching the codes')
                print(codes, offset)

            else:
                if len(offset) == 1:
                    offset = offset * len(codes)
                for codeno, code in enumerate(codes):
                    data[code] += offset[codeno]
        else:
            data += offset


    if multiplier:
        if type(multiplier) == list:
            if len(multiplier) != len(codes) and not len(multiplier) == 1:
                print('Ignoring offset as it\'s length is not matching the codes')
                print(codes, multiplier)

            else:
                if len(multiplier) == 1:
                    multiplier = multiplier * len(codes)
                for codeno, code in enumerate(codes):
                    data[code] *= multiplier[codeno]
        else:
            data *= multiplier

    if dt is None:
        dt = min(data.index[1:]-data.index[:-1])

    _dt = pd.to_timedelta(dt).total_seconds()

    if _dt >= datetime.timedelta(days=1).total_seconds():
        strdt = _dt / datetime.timedelta(days=1).total_seconds()
        strunit = ' Days'

    elif _dt >= datetime.timedelta(hours=1).total_seconds():
        strdt = _dt / datetime.timedelta(hours=1).total_seconds()
        strunit = ' Hours'
    else:
        strdt = _dt / datetime.timedelta(minutes=1).total_seconds()
        strunit = ' Minutes'
    if strdt % 1 == 0:
        strdt = int(strdt)
    else:
        strdt = round(strdt, 2)

    strdt = str(strdt) + strunit
    possiblelegtitle = np.unique([meta[key]['name'] for key in data.columns])

    if len(possiblelegtitle) == 1:
        _figopt['legtitle'] = possiblelegtitle[0] + ', '
        onetitle = True
    else:
        _figopt['legtitle'] = ''
        onetitle = False

    if plottype not in types[4]:
        _figopt['legtitle'] += 'Agg. to '  + strdt
    else:
        _figopt['legtitle'] += 'Stations:'

    uniqstats = np.unique([meta[key]['name_sdt'] for key in data.columns])
    if len(uniqstats) == 1:
        onestat = True
        _figopt['legtitle'] = uniqstats[0] +' ' + _figopt['legtitle']
    else:
        onestat = False

    for key in data.columns:
        if not onestat:
            _lineopt[key]['label'] = meta[key]['name_sdt']+' '

        if onetitle:
            pass
        else:
            _lineopt[key]['label'] += ' ' + meta[key]['name']
            _lineopt[key]['label'] += ' ('

        _lineopt[key]['label'] += key+ ' with ' + meta[key]['geraet']

        _lineopt[key]['label'] += ', '
        if meta[key]['messhoehe'] != -9999:
            if meta[key]['messhoehe'] < 0:
                word = ' m below ground'
            elif meta[key]['messhoehe'] > 0:
                word = ' m above ground'
            else:
                word = 'on the ground'

            if meta[key]['messhoehe'] % 1 == 0:
                number = str(int(meta[key]['messhoehe']))
            else:
                number = str(np.round(meta[key]['messhoehe'],2))

            _lineopt[key]['label'] += number + ' ' + word + ', '

        _lineopt[key]['label'] += meta[key]['aggregation']

        # only add the closing brackets if its onetitle
        if onetitle:
            pass
        else:
            _lineopt[key]['label'] += ')'



    # some warning for user in case there is no secondaryaxis set and
    # we have "non-matching" timeseries in a strict sense (unequal units, names)


    primcodes = [c for c in codes if c not in _figopt['secondaryaxis']]
    seccodes = [c for c in codes if c in _figopt['secondaryaxis']]

    if _figopt['secondaryylabel']:
        pass
    else:
        for i, c in enumerate(seccodes):
            _figopt['secondaryylabel'] = meta[key]['name']
            _figopt['secondaryylabel'] += ' ['+unituppercase(meta[key]['einheit'])+']\n'
            _figopt['secondaryylabel'] = _figopt['secondaryylabel'].rstrip()

    _figopt['secondaryylabel'] = html.unescape(unituppercase(_figopt['secondaryylabel']))

    if _figopt['ylabel']:
        pass
    else:
        if len(np.unique([meta[key]['name'] for key in primcodes])) == 1:
            _figopt['ylabel'] = meta[primcodes[0]]['name']
            _figopt['ylabel'] += ' ['+unituppercase(meta[primcodes[0]]['einheit'])+']'
        elif len(np.unique([meta[key]['einheit'] for key in primcodes])) == 1:
            _figopt['ylabel'] = ' ['+unituppercase(meta[primcodes[0]]['einheit'])+']'
        else:
            if plottype not in types[3]+types[4] and 'secondaryaxis' not in _figopt:
                print('Neither variable name nor units in database match.',
                      'Are you sure you want to plot them on the same axis?')
            pass
    _figopt['ylabel'] = html.unescape(_figopt['ylabel'])
    # localtz, localutc = datetime.datetime.now(), datetime.datetime.utcnow()
    # dttz = round((localutc - localtz).total_seconds() / 3600)
    _figopt['xlabel'] = 'Time (' + datatz + ')'
    # _figopt['xlabel'] = 'Time (' + str(datetime.datetime.now().astimezone().tzinfo) + ')'




    if len(codes) < 2 and plottype == 'xy':
        print('For an xy plot, at least two timeseries code have to be given')
        plottype = 'timeseries'

    if plottype in types[0]:

        if plottype == types[0][0]:
            if indexcode is None:
                if not quiet:
                    print('Autoselecting first code as new index')
                indexcode = 0

            data.index = data[codes[indexcode % len(codes)]]
            data = data.drop(columns=codes[indexcode % len(codes)])
            _figopt['type'] = 'xy'
            _figopt['xlabel'] = meta[codes[indexcode]]['name']
            _figopt['xlabel'] += ' ['+unituppercase(meta[codes[indexcode]]['einheit'])+']'
            _figopt['xlabel'] = html.unescape(_figopt['xlabel'])
            _figopt['sunlines'] = False
        else:
            _figopt['type'] = 'timeseries'

        fig = linear(data, meta, fig=fig, lineopt=_lineopt, figopt=_figopt)
        #fig[1].set_xlim(data.index[0], data.index[-1])
        if plottype == types[0][0]:
            fig[1].set_xlim(_figopt['xrange'])
        elif type(t0) == datetime.datetime and type(t1) == datetime.datetime:
            fig[1].set_xlim(t0, t1) # data.index[0], data.index[-1])
        else:
            fig[1].set_xlim(data.index[0], data.index[-1])
            # _xr = datetime.datetime.now(data.index[0], data.index[-1]))
        fig[0].tight_layout()

    elif plottype in types[1]:

        heights = [meta[i]['messhoehe'] for i in meta.keys()]

        fig = profiles(data,
                       fig=fig,
                       heights=heights,
                       lineopt=_lineopt,
                       figopt=_figopt,
                       label=html.unescape(meta[data.columns[0]]['einheit']),
                       **kwargs,
                       )
        fig[0].tight_layout()

    elif plottype in types[2]:
        fig[0].subplots_adjust(bottom=0.12, left=0.08, right=0.90,)
        fig = iso(data,
                  fig=fig,
                  lineopt=_lineopt,
                  figopt=_figopt,
                  simple=True,
                  **kwargs,
                  )

    elif plottype in types[3] or plottype in types[4]:
        data.columns = [d.upper() for d in data.columns]
        # ensure winddata at 0 (which is faulty) is removed
        if plottype in types[4]:
            lats = [meta[k]['lat'] for k in meta]
            lons = [meta[k]['lon'] for k in meta]
            names = [meta[k]['name_sdt'] for k in meta]
            fig = stationmap(lats, lons, names,
                             fig=fig,
                             lineopt=_lineopt,
                             figopt=_figopt,
                             mapalpha=_figopt['mapalpha'],
                             **kwargs)
        else:
            winddircodes = [m for m in meta
                            if meta[m]['variable'].upper() == 'WDA'
                            or meta[m]['name'].upper() == 'WIND DIRECTION']

            windspeedcodes = [m for m in meta
                              if meta[m]['variable'].upper() != 'WDA'
                              and meta[m]['name'].upper() != 'WIND DIRECTION']

            if len(winddircodes) != len(windspeedcodes):
                fig = fig[0]
                print('Unequal length of wind direction and wind speed codes!')
            else:
                # check for erraneous amount of 0 winddirection in data

                for wdir, wsp in zip(winddircodes, windspeedcodes):
                    chk = data[data[wdir].eq(0)].index
                    data.loc[chk, [wdir, wsp]] = np.nan

                if data.dropna(how='all').empty:

                    errormsg = 'NO VALID WINDVALUES LEFT AFTER CONTROL \n\n'
                    errormsg += '\n\nGiven parameters were\n'
                    errormsg += 'Timestamp t0: ' + data.index[0].strftime('%d %b %Y %H:%M:%S')+'\n'
                    errormsg += 'Timestamp t1: ' + data.index[-1].strftime('%d %b %Y %H:%M:%S')+'\n'

                    fig[0].text(0.5, 0.5, errormsg, ha='center', va='center', fontsize=16)
                    plt.axis('off')
                    if outfile:
                        fig[0].savefig(outfile)

                    if returnfig:
                        return fig
                    else:
                        plt.close(fig[0])
                        return

                lats = [meta[k]['lat'] for k in winddircodes]
                lons = [meta[k]['lon'] for k in winddircodes]

                if lats and lons:
                    fig = windmap(lats, lons, data,
                                  fig=fig,
                                  lineopt=_lineopt,
                                  figopt=_figopt,
                                  windspeedcodes=windspeedcodes,
                                  winddircodes=winddircodes,
                                  cmap=defaultwindcolor(),
                                  mapalpha=_figopt['mapalpha'],
                                  **kwargs,
                                  )
                else:
                    fig = fig[0]
                    print('Latitude and/or longitude could not be found automatically')


        # return values of windmap/stationmap are figures but not also axes
        # like in other figures as this would lead to even more complicated
        # keeping track of things
        fig = [fig, None]
    elif plottype in types[5]:

        measurementheight = [meta[i]['messhoehe'] for i in data.columns]
        _figopt['zlabel'] = html.unescape(_figopt['ylabel'])
        data.columns = [d.upper() for d in data.columns]

        fig[0].subplots_adjust(bottom=0.15, left=0.08, right=0.92)

        fig = mesh(data,
                   y=measurementheight,
                   fig=fig,
                   lineopt=_lineopt,
                   figopt=_figopt,
                   **kwargs,
                   )
        #fig[1].set_xlim(data.index[0], data.index[-1])
        fig[1].set_xlim(t0, t1) #data.index[0], data.index[-1])
    else:
        print('Plottype not known, please use of the following:', types)

    # override user behaviour
#    if (data.index[-1] - data.index[0]) >= datetime.timedelta(days=14):
#        _figopt['sunlines'] = False

    # valid option only for timeseries, profiles and isoplots
    if _figopt['sunlines'] and plottype in types[0][1:]+types[1]+types[2]+types[5]:

        # isoplot, handle sunlines differently
        if plottype in types[2]:
            _xi = [mdates.num2date(i) for i in fig[1].get_xlim()]
            #print(_xi)
            # use a (likely) higher resolution array to calculate the usnposition
            # as the data.index may be of lower frequency and thus "falsify"
            # the sunposition
            sunindex = pd.date_range(_xi[0],
                                     _xi[1]+datetime.timedelta(days=1),
                                     freq='1Min')[1:]
            sundown = sunpos(sunindex,
                             meta[codes[0]]['lat'],
                             meta[codes[0]]['lon'],
                             )
            # reshape to the 2D field we have get the elements that are >= 0
            # (implicit by np.where, i.e. when the sun is up
            sundown = np.reshape(sundown, (len(sundown)//60//24, 24*60))
            ylim = fig[1].get_ylim()
            ys = np.linspace(ylim[0], ylim[1], 24*60)
            fig[1].contour(np.unique(sunindex.date)[:-1],
                           ys,
                           sundown.T,
                           # the level doesnt matter except being between 0 and 1
                           # to surpress the user warning that would appear
                           # at either 0 or 1 directly
                           levels=[0.5],
                           colors=_figopt['sunlinesisocolor'],
                           linewidths=_figopt['sunlineswidth'],
                           )
            # calulcate string position for sunset/sunrise text
            dayindex = 2
            strpos = np.nonzero(sundown[dayindex, :].ravel())

            strpos = [strpos[0][0], strpos[0][-1]]
            text = [' Sunrise', 'Sunset ']
            for i, p in enumerate(strpos):
                fig[1].text(sunindex[dayindex],
                            ys[p],
                            text[i],
                            rotation=-90,
                            color=_figopt['sunlinestextcolor'],
                            fontsize=10,
                            ha='left',
                            va=['top', 'bottom'][i],
                            bbox=dict(boxstyle='round', pad=0.1, fc="w", ec="w", alpha=0.2),
                            )

        # linearplots
        else:

            _xi = [mdates.num2date(i) for i in fig[1].get_xlim()]
            # dont draw sunlines unless explicitly stated in figopt
            if (_xi[1] - _xi[0]) > datetime.timedelta(days=60):
                if figopt is not None and 'sunlines' in figopt and figopt['sunlines']:
                    pass
                else:
                    _figopt['sunlines'] = False
                    _figopt['marktropicalnight'] = False



            sunindex = pd.date_range(_xi[0], _xi[1], freq='1Min')
            sundown = sunpos(sunindex,
                             meta[codes[0]]['lat'],
                             meta[codes[0]]['lon'],
                             )
            # use a (likely) higher resolution array to calculate the
            # usnposition as the data.index may be of lower frequency and
            # thus "falsify" the sunposition
            ylim = fig[1].get_ylim()
            if _figopt['sunlines']:
                fig[1].fill_between(sunindex,
                                    ylim[0], ylim[1],
                                    zorder=0,
                                    where=~sundown,
                                    color=_figopt['sunlinescolor'])

            if _figopt['zeroline']:
                if fig[1].get_ylim()[0] <=0 and fig[1].get_ylim()[1] > 0:
                    fig[1].plot(fig[1].get_xlim(),
                                [0,0],
                                color=_figopt['zerolinecolor'],
                                lw=_figopt['zerolinewidth'])

            if _figopt['marktropicalnight']:
                if ylim[1] > 20 and ylim[0] < 20:
                    fig[1].fill_between(sunindex,
                                        20 - 0.005 * (ylim[1] - ylim[0]),
                                        20 + 0.005 * (ylim[1] - ylim[0]),
                                        # 19.9, 20.1,
                                        zorder=0,
                                        where=~sundown,
                                        color=_figopt['tropicalnightscolor'],
                                        edgecolors=_figopt['tropicalnightsedgecolor'],
                                        linewidth=_figopt['tropicalnightsedgewidth']
                                        )
    # windmap / stationnetwork
    if plottype in types[3:5]:
        if 'mapfullscreen' in kwargs:
            watermark(fig[0], ypos=0.02, fontsize=8)
        else:
            watermark(fig[0], ypos=0.0, fontsize=8)
    else:
        watermark(fig[0], ypos=0.025, fontsize=10)

    if outfile:
        fig[0].savefig(outfile)

    if returnfig:
        return fig
    else:
        plt.close(fig[0])
        return


if __name__ == '__main__':
    print('*'*10, 'HELP for main', '*'*10)
    print('The equivalent to aml_plt_ps from the AML IDL library')
    print('Creates plots from passed in codes and time spans,',
          'properties (color, linestyle etc.) can be set accordingly')
#
#    x = plot(['BKLIDTA1', 'BKLIRHA1'], t1='*', t0='*-7',dt='30Min',
#             plottype='timeseries',
#             lineopt={'ls': '-',
#                      'alpha': 1,
##                      'color': '#00ff00',
#                      'BKLIDTA1': {'color': '#3333ff', 'markersize': 3,},
#                      'BKLIRHA1': {'color': '#ff9933', 'marker': 'None',}
#                      },
#             figopt={'secondaryaxis': 'BKLIRHA1',
#                     'secondaryaxisyrange': [0,100],},
#             )
#    y = plot(['BKLIDTA1', 'BKLIWVA1', 'BKLIWDA1'], t1='*', t0='*-7',
#             lineopt={'ls': 'none', 'BKLIWDA1': {'color': 'red',},},
#             figopt={'secondaryaxis': 'BKLIWDA1',
#                     'secondaryaxisyrange': [0,360],
#                     'yrange': [0,20],
#                     'figsize': [11, 11],
#                     'suppressaxiscolor': False,
#                     },)
#    z = plot(['BBINPCT4','BKLBPCT2','BKLIPCT2','BLEOPCT1','BBINPCT1'], t1='*', t0='*-7', dt = '1H',
#             plottype='timeseries',
#             lineopt={#'BBINPCT4': {'color': 'red',},
#                      'BBINPCT1': {'ls': 'steps',},},
#             figopt={'barcodes': ['BBINPCT4','BKLBPCT2','BKLIPCT2','BLEOPCT1','BBINPCT1'],
##                     'secondaryaxisyrange': [0,360],
##                     'yrange': [0,20],
##                     'figsize': [7, 7],
#                     'suppressaxiscolor': False,
#                     },)
#    xx = plot(['BKLIDTA7','BKLIDTA8', 'BKLIDTA9'], t1='*', t0='*-1', dt='2H', plottype='profile',
#              offset=[0.0392,0.0882,0.1372], #lineopt={'color': 'orange', 'markerfacecolor': 'orange'},
#              )
##
##
##    b = plot(['BKLIWVA1','BKLIWDA1','BLEOWVA1','BLEOWDA1',], t1='*', t0='*-7',
##             plottype='wind', )
##
##    c = plot(['FNCMBVA1','FNVFWVA1','FNGBWVA1','FNS8WDA1'], t1='*', t0='*-7',
##             plottype='stationmap', )
#
#    d = plot(['BKLIDTA1-BLERDTA1'], t1='*-1', t0='*-365',
##             dt='1H',
#             plottype='iso',
#             makemesh=True,
#             overlaycontour=False,
#             valuerange=[-4,4],
#             )

#    s = plot(['BBINPCT4','BKLBPCT2','BKLIPCT2','BLEOPCT1','BBINPCT1'], t1='*', t0='*-7', dt = '24H',
#             plottype='timeseries',
#             lineopt={'ls': 'none', 'BKLIWDA1': {'color': 'red',},},
#             figopt={'barcodes': ['BBINPCT4','BKLBPCT2','BKLIPCT2','BLEOPCT1','BBINPCT1'],
##                     'secondaryaxisyrange': [0,360],
##                     'yrange': [0,20],
##                     'figsize': [7, 7],
# #                     'suppressaxiscolor': False,
# #                     },)


#     bsoverlaprange, bsheight, bsstep = 50, 3000, 5
#     ceilobscodes = ['bklibs' + str(i).zfill(4)
#                     for i in range(bsoverlaprange//5, bsheight//5+1)]

#     data, meta = getdata(ceilobscodes, t0='*-7', t1='*-1')

#     s = plot(ceilobscodes,
#             t1='*',
#             t0='*-7',
#             dt='30Min',
#             how={i:'max' for i in ceilobscodes},
#             cmap='jet',
#             plottype='mesh',
#             figopt={'zlog': True},
#             # zlog=True,
#             minvalue=25,
#             valuerange=[10**1, 10**4],
#             overlaycontour=False,
#             contourcolor=['k'],
#             returnfig=True,
#             # slope=True,
#             )
