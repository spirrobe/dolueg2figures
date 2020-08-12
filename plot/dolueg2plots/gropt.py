#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# Created on Fri Feb  8 16:55:06 2019
#
# @author: spirro00
"""

def colorscaler(color,
                scale=0.9):
    import matplotlib as mpl
    mplcolors = mpl.colors.get_named_colors_mapping()
    if type(color) == str and '#' in color:
        # hexcolor
        rgb = color[1:3], color[3:5], color[5:]
        rgb = '#'+''.join([hex(int(int(i, 16)*scale))[2:].zfill(2) for i in rgb])
    elif type(color) == str:
        if color in mplcolors:
            rgb = colorscaler(mplcolors[color], scale=scale)
        else:
            print('Unknown color:', color)
            print('Returning black')
            rgb = 'k'

    elif type(color) == list and len(color) == 3:
        # rgb float triple
        rgb = [i*scale for i in color]

    return rgb


def unituppercase(x, quiet=True):
    if '$^{-' in x:
        if not quiet:
            print('String with units already latex converted')
        return x

    ec = [' ', '/', '*', '(',]
    # x = x.strip().replace('-', '$^{-').replace('+', '$^{')
    out, openbracket = '', False
    for _, i in enumerate(x):
        if i == '{':
            openbracket = True
        if i == '}':
            openbracket = False

        if openbracket == False and i.isnumeric() and out[-1] not in ec:

            # just a number, do not uppercase it
            # if out[-1] in [' ', '/', '*']
            #     pass

            openbracket = True
            if out[-1] == '-':
                out = out[:-1]+ '$^{-'
            elif out[-1] == '+':
                if i == '1' and not x[_+1].isnumeric():
                    i = ''
                    out = out[:-1]
                    openbracket = False
                else:
                    out = out[:-1] + '$^{'
            else:
                out += '$^{'


        if openbracket and i.isalpha():
            out += '}$'
            openbracket = False

        out += i

    if openbracket:
        if out[-1] in [')', ']']:
            out = out[:-1] + '}$' + out[-1]
        else:
            out += '}$'

    return out


def basefinder(lower, upper=None):
    import numpy as np

    if upper is None:
        diff = lower
    else:
        diff = upper - lower


    # no difference at all, return 1
    if diff == 0:
        return 1

    # find the lower 10 base
    exp = np.log10(abs(diff)) // 1
    # get the actual number that we are interested in
    leftover = diff // (10 ** exp)

    if leftover >= 5:
        x = 2
    elif leftover >= 2:
        x = 1
    else:
        x = 0.5

    _base = x * 10 ** exp

    return _base


def baseround(x, base=None, up=False, down=False):
    if base is None:
        base = 5
    if up:
        return x//base*base + base
    elif down:
        return x//base*base
    else:
        return int(base * round(float(x)/base))


# takes a value or list of values and rounds it (1 value) or floor/ceils it
#def autoranger(_v, base=None, **kwargs):
def autoranger(_v, **kwargs):

    if type(_v) == list:
        return baseround(_v[0], down=True, **kwargs), \
               baseround(_v[1], up=True, **kwargs)
    else:
        return baseround(_v, **kwargs)


def autotimeaxis(timeindex,
                 ax=None,
                 extraspace=0,
                 majorinterval=1,
                 minorinterval=1,
                 quiet=True,
                 ):
    import datetime
    import pandas as pd
    import matplotlib.dates as mdates
    aday = 24*60*60
    diff = (max(timeindex)-min(timeindex)).total_seconds()
    diff /= aday

    if diff >= 800:
        roundto, xformat, xminortickformat = 'Y', '%-d.%b\n%Y', '%-d.%-m'
        major = mdates.YearLocator()
        minor = mdates.MonthLocator(bymonth=range(1,12+minorinterval,minorinterval))
    elif diff >= 300:
        roundto, xformat, xminortickformat = 'M', '%-d.%b\n%Y', '%-d.%b'
        major = mdates.YearLocator()
        minor = mdates.MonthLocator(bymonth=range(1,12+minorinterval,minorinterval))
    elif diff >= 150:
        roundto, xformat, xminortickformat = '12D', '\n%-d.%b\n%Y', '%-d'
        major = mdates.MonthLocator(bymonth=range(1,12+majorinterval,majorinterval))
        minor = mdates.MonthLocator(bymonthday=range(7,31,7*minorinterval))
    elif diff >= 90:
        roundto, xformat, xminortickformat = '14D', '\n%-d.%b\n%Y', '%-d'
        major = mdates.MonthLocator(bymonth=range(1,12+majorinterval,majorinterval))
        minor = mdates.DayLocator(interval=3*minorinterval)
    elif diff >= 35:
        roundto, xformat, xminortickformat = '7D', '\n%-d.%b\n%Y', '%-d'
        major = mdates.MonthLocator(bymonth=range(1,12+majorinterval,majorinterval))
        minor = mdates.DayLocator(interval=2*minorinterval)
    elif diff >= 14:
        roundto, xformat, xminortickformat = '3D', '%-d.%b\n%Y', '%-d'
        major = mdates.DayLocator(interval=7*majorinterval)
        minor = mdates.DayLocator(interval=minorinterval)
    elif diff >= 6:
        roundto, xformat, xminortickformat = '1D', '%-d.%b\n%Y', '%H'
        major = mdates.DayLocator(interval=majorinterval)
        minor = mdates.HourLocator(byhour=range(0,24+6,6), )
    elif diff >= 2:
        roundto, xformat, xminortickformat = '3H', '%-d.%b\n%Y', '%H'
        major = mdates.DayLocator(interval=majorinterval)
        minor = mdates.HourLocator(byhour=range(0,24+4,4), )
    elif diff >= 0.75:
        roundto, xformat, xminortickformat = 'H', '%-d.%b', '%H:%M'
        major = mdates.DayLocator(interval=majorinterval)
        minor = mdates.HourLocator(byhour=range(0,24+2,2), )
#    elif diff >= 0.75:
#        roundto, xformat = '3H', '%H:%M'
#        major = mdates.HourLocator(interval=3)
#        minor = mdates.MinuteLocator(interval=30)
    elif diff >= 0.25:
        roundto, xformat, xminortickformat = 'H', '%H:%M', '%M'
        major = mdates.HourLocator(byhour=range(0, 24+1, 1), )
        if minorinterval <= 15:
            if not quiet:
                print('Minorlimit autoincreased')
            minorinterval = 15
        minor = mdates.MinuteLocator(byminute=range(0, 60+15, 15))
    else:
        roundto, xformat, xminortickformat = 'H', '%H:%M', '%M'
        major = mdates.HourLocator(byhour=range(0, 24+1, 1), )
        if minorinterval <= 15:
            if not quiet:
                print('Minorlimit autoincreased')
            minorinterval = 15
        minor = mdates.MinuteLocator(byminute=range(0, 60+5, 5))

    if ax is not None:

        xlim = [timeindex.min(),
               timeindex.max()]
        if 'M' in roundto:
            xlim = [i.normalize() for i in xlim]
            nmo = roundto.split('M')[0]
            if nmo:
                pass
            else:
                nmo = 1
            xlim = [xlim[0]-pd.offsets.MonthBegin()*int(nmo),
                    xlim[1]+pd.offsets.MonthBegin()*int(nmo)]
        elif 'Y' in roundto:
            xlim = [i.normalize() for i in xlim]
            nmo = roundto.split('Y')[0]
            if nmo:
                pass
            else:
                nmo = 1
            xlim = [xlim[0]-pd.offsets.YearBegin()*int(nmo),
                    xlim[1]+pd.offsets.YearBegin()*int(nmo)]
        else:
            xlim = [xlim[0].floor(roundto), xlim[1].ceil(roundto)]

        if extraspace:
            xlim = [xlim[0]-extraspace, xlim[1]+extraspace]
        ax.set_xlim(xlim)

        ax.xaxis.set_major_locator(major)
        ax.xaxis.set_minor_locator(minor)
        xaxisformat = mdates.DateFormatter(xformat)
        ax.xaxis.set_major_formatter(xaxisformat)
        ax.tick_params(axis='x', which='major', pad=5, length=10)

#        if diff <=6:
        ax.tick_params(which='minor', pad=3, length=5)
        xaxisminorformat = mdates.DateFormatter(xminortickformat)
        ax.xaxis.set_minor_formatter(xaxisminorformat)

    return roundto, xformat


def defaultfigopt():
    return {'figsize': [24/2, 9.6/2],
            'figdpi': 200,

            'yrange': [-9999, -9999],
            'yticks': None,
            'ylabel': '',

            'xrange': [-9999, -9999],
            'xticks': None,
            'xlabel': 'UTC',

            'zrange': [-9999, -9999],
            'zticks': None,
            'zlabel': '',

            'zeroline': True,
            'zerolinecolor': '#000000',
            'zerolinewidth': 1,

            'grid': True,
            'gridxlinestyle': '-',
            'gridylinestyle': ':',
            'gridlinewidth': 0.25,
            'gridlinecolor': 'k',

            'secondaryaxis': [],
            'secondaryylabel': '',
            'secondaryaxisyrange': [-9999, -9999],
            'secondaryaxisticks': None,
            'secondaryaxislabels': None,
            'secondaryyaxissamescale': False,

            'barcodes': [],
            'bartotalwidth': 0.85,

            'cumulativecodes': [],

            'suppressaxiscolor': True,
            'suppresslegend': False,

            'legtitle': None,
            'leglabel': [],
            'legfontsize': 10,
            'legposition': 10,
            'legendbox': True,
            'legalpha': 0.5,

            'figtitle': None,

            'fontsize': 10,

            'zeroline': True,
            'zerolinecolor': '#000000',

            'sunlines': True,
            'sunlinescolor': '#bcbcbc',
            'sunlinesisocolor': '#000000',
            'sunlineswidth': 1.5,
            'sunlinestextcolor': '#333333',

            'marktropicalnight': False,
            'tropicalnightscolor': '#111111',
            'tropicalnightsedgecolor': '#000000',
            'tropicalnightsedgewidth': 1,

            # only applied to mesh/iso plots
            'zlog': False,
            # only applied to linear plots
            'ylog': False,
            'secondaryylog': False,

            # only applied to linear bar plots
            'baredge': False,

            # mapalpha
            'mapalpha': 0.85,
            # 'stationalpha': 0.5,
            }

def sunpos(pandasindex, lat, lon,):
    import datetime
    from pysolar.solar import get_altitude_fast
    import numpy as np

    # converts this index to UTC
    tzinfo = pandasindex.tzinfo
    if tzinfo is not None:
        pandasindex = pandasindex.copy().tz_convert(None)

    # add the local timezone as fixed offset
    localtz, localutc = datetime.datetime.now(), datetime.datetime.utcnow()
    dttz = round((localutc - localtz).total_seconds() / 3600)
    pandasindex = pandasindex.copy() + datetime.timedelta(hours=dttz)

    alt = get_altitude_fast(lat, lon, pandasindex)
    alt = np.where(alt >= 0 , True, False)
    return alt

def defaultlineopt(keys=None):
    import matplotlib as plt

    defaultcolors = defaultct()[2:]

    if keys is None:
        return {'color': defaultcolors[0],
                'ls': '-',
                'lw': 1.5,
#                'marker': 'o',
                'marker': None,
                'markersize': 5,
                'markerfacecolor': defaultcolors[0],
                'markeredgecolor': '#000000',
                'alpha': 0.85,
                'label': '',
                }
    else:
        return {key: {'color': defaultcolors[keyno % len(defaultcolors)],
                      'ls': '-',
                      'lw': 1.5,
#                      'marker': 'o',
                      'marker': None,
                      'markersize': 5,
                      'markerfacecolor': defaultcolors[keyno % len(defaultcolors)],
                      'markeredgecolor': '#000000',
                      'edgecolor': '#000000',
                      'alpha': 0.85,
                      'label': '',
                      }
                for keyno, key in enumerate(keys)}


def extendopt(gropt, columns, check=False):
    if check:
        extendedgropt = {c: gropt.copy() for c in columns if c in gropt}
    else:
        extendedgropt = {c: gropt.copy() for c in columns}
    return extendedgropt


def updateopt(toupdate,
              updatewith=None,
              overwritecolor=True):
    toupdate = toupdate.copy()

    # if there are some options given, overwrite them now
    if updatewith is not None:
        todokeys = []

        for key in updatewith.keys():
            if type(updatewith[key]) == dict:
                # if key in data.columns or key == data.index.name:
                # it exists as a data series and the option should thus only
                # only apply for this one
                todokeys.append(key)
            else:
                # general options
                for subkey in toupdate.keys():
                    toupdate[subkey][key] = updatewith[key]
                    if 'color' == key and overwritecolor == True:
                        if 'markerfacecolor' in toupdate[subkey]:
                            toupdate[subkey]['markerfacecolor'] = toupdate[subkey]['color']

        for key in todokeys:
            if key in toupdate:
                toupdate[key].update(updatewith[key])
                if 'color' in updatewith[key] and overwritecolor == True:
                        if 'markerfacecolor' in toupdate[key]:
                            toupdate[key]['markerfacecolor'] = updatewith[key]['color']


    return toupdate


def acceptedopt(gropt=None, which='linear'):
    # the matplotlib accepted options for the lineoptions
    options = {'linear': ['color', ],
               'windmap': ['color', ],
               'iso': ['color', ],
               'profile': ['color', ],
               'stationmap': ['color', ],
               }

    if gropt is None and which in options.keys():
        # gropt is empty but which is in the options, return just the matching
        return options[which]
    elif gropt is None and not which:
        # gropt is empty and which isnt in the options, return everything
        return options
    elif which in options.keys():
        # which is in the options, and gropt is given, return a filtered dict
        return {gropt[i] for i in gropt.keys() if i in options.keys()}
    else:
        # which is not in the options but gropt is given, filter out the
        # keywords that exists across all options, this should not be used
        # too many times and is mainly here for completeness

        # make a list with everything that exists which we will filter
        alloptions = []
        for i in options.keys():
            alloptions += options[i]

        # what we will have in the end
        filteredoptions = []
        count = len(options.keys())
        for i in alloptions:
            # append if occurs as many times as there are plottypes
            # but only if its not in there already
            if alloptions.count(i) == count and i not in filteredoptions:
                filteredoptions.append(i)

        # return a dict to be consistent with the other returns
        return {'all': filteredoptions}

def defaultwindcolor(reverse=False):
    colors = ['#F37021',
              # '#FD9D6F',
              '#FEE378',
              '#97D6E8',
              '#4DB797',
              '#009900',
              '#6666FF',
              '#6251B5',
              '#2326AF',
              '#482671',
              '#cc0066',
              '#ff3300'


              ]
    return colors[::(-1)**int(reverse)]

def defaultct(reverse=False):
     colors  = [[0.0, 0.0, 0.0],
                [1.0, 1.0, 1.0],
                [1.0, 0.0, 0.0],
                [1.0, 0.0, 0.41568627450980394],
                [0.9176470588235294, 0.0, 1.0],
                [0.5019607843137255, 0.0, 1.0],
                [0.0, 0.08235294117647059, 1.0],
                [0.0, 0.6666666666666666, 1.0],
                [0.0, 1.0, 0.9176470588235294],
                [0.0, 1.0, 0.5019607843137255],
                [0.08235294117647059, 1.0, 0.0],
                [0.7529411764705882, 1.0, 0.0],
                [1.0, 1.0, 0.0],
                [1.0, 0.8352941176470589, 0.0],
                [1.0, 0.5843137254901961, 0.0],
                [1.0, 0.3333333333333333, 0.0],
                [1.0, 0.4980392156862745, 0.4980392156862745],
                [1.0, 0.4980392156862745, 0.7098039215686275],
                [0.9607843137254902, 0.4980392156862745, 1.0],
                [0.7490196078431373, 0.4980392156862745, 1.0],
                [0.4980392156862745, 0.5411764705882353, 1.0],
                [0.4980392156862745, 0.8352941176470589, 1.0],
                [0.4980392156862745, 1.0, 0.9607843137254902],
                [0.4980392156862745, 1.0, 0.7529411764705882],
                [0.5411764705882353, 1.0, 0.4980392156862745],
                [0.8784313725490196, 1.0, 0.4980392156862745],
                [1.0, 1.0, 0.4980392156862745],
                [1.0, 0.9176470588235294, 0.4980392156862745],
                [1.0, 0.792156862745098, 0.4980392156862745],
                [1.0, 0.6666666666666666, 0.4980392156862745],
                [0.5019607843137255, 0.0, 0.0],
                [0.5019607843137255, 0.0, 0.20784313725490197],
                [0.4588235294117647, 0.0, 0.5019607843137255],
                [0.25098039215686274, 0.0, 0.5019607843137255],
                [0.0, 0.0392156862745098, 0.5019607843137255],
                [0.0, 0.3333333333333333, 0.5019607843137255],
                [0.0, 0.5019607843137255, 0.4588235294117647],
                [0.0, 0.5019607843137255, 0.25098039215686274],
                [0.0392156862745098, 0.5019607843137255, 0.0],
                [0.3764705882352941, 0.5019607843137255, 0.0],
                [0.4980392156862745, 0.5019607843137255, 0.0],
                [0.5019607843137255, 0.41568627450980394, 0.0],
                [0.5019607843137255, 0.2901960784313726, 0.0],
                [0.5019607843137255, 0.16470588235294117, 0.0],
                [0.5019607843137255, 0.25098039215686274, 0.25098039215686274],
                [0.5019607843137255, 0.25098039215686274, 0.35294117647058826],
                [0.47843137254901963, 0.25098039215686274, 0.5019607843137255],
                [0.3764705882352941, 0.25098039215686274, 0.5019607843137255],
                [0.25098039215686274, 0.41568627450980394, 0.5019607843137255],
                [0.25098039215686274, 0.5019607843137255, 0.47843137254901963],
                [0.25098039215686274, 0.5019607843137255, 0.3764705882352941],
                [0.27058823529411763, 0.5019607843137255, 0.25098039215686274],
                [0.4392156862745098, 0.5019607843137255, 0.25098039215686274],
                [0.4980392156862745, 0.5019607843137255, 0.25098039215686274],
                [0.5019607843137255, 0.4588235294117647, 0.25098039215686274],
                [0.5019607843137255, 0.396078431372549, 0.25098039215686274],
                [0.5019607843137255, 0.3333333333333333, 0.25098039215686274],
                [0.8, 0.1568627450980392, 0.1568627450980392],
                [0.8, 0.1568627450980392, 0.42745098039215684],
                [0.7490196078431373, 0.1568627450980392, 0.8],
                [0.47843137254901963, 0.1568627450980392, 0.8],
                [0.1568627450980392, 0.21176470588235294, 0.8],
                [0.1568627450980392, 0.5882352941176471, 0.8],
                [0.1568627450980392, 0.8, 0.7490196078431373],
                [0.1568627450980392, 0.8, 0.47843137254901963],
                [0.21176470588235294, 0.8, 0.1568627450980392],
                [0.6392156862745098, 0.8, 0.1568627450980392],
                [0.8, 0.8, 0.1568627450980392],
                [0.8, 0.6941176470588235, 0.1568627450980392],
                [0.8, 0.5333333333333333, 0.1568627450980392],
                [0.8, 0.37254901960784315, 0.1568627450980392],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [1.0, 1.0, 1.0],
                [0.9921568627450981, 0.9921568627450981, 0.9921568627450981],
                [0.984313725490196, 0.984313725490196, 0.984313725490196],
                [0.9764705882352941, 0.9764705882352941, 0.9764705882352941],
                [0.9686274509803922, 0.9686274509803922, 0.9686274509803922],
                [0.9607843137254902, 0.9607843137254902, 0.9607843137254902],
                [0.9529411764705882, 0.9529411764705882, 0.9529411764705882],
                [0.9450980392156862, 0.9450980392156862, 0.9450980392156862],
                [0.9372549019607843, 0.9372549019607843, 0.9372549019607843],
                [0.9294117647058824, 0.9294117647058824, 0.9294117647058824],
                [0.9215686274509803, 0.9215686274509803, 0.9215686274509803],
                [0.9137254901960784, 0.9137254901960784, 0.9137254901960784],
                [0.9058823529411765, 0.9058823529411765, 0.9058823529411765],
                [0.8980392156862745, 0.8980392156862745, 0.8980392156862745],
                [0.8901960784313725, 0.8901960784313725, 0.8901960784313725],
                [0.8823529411764706, 0.8823529411764706, 0.8823529411764706],
                [0.8745098039215686, 0.8745098039215686, 0.8745098039215686],
                [0.8666666666666667, 0.8666666666666667, 0.8666666666666667],
                [0.8588235294117647, 0.8588235294117647, 0.8588235294117647],
                [0.8509803921568627, 0.8509803921568627, 0.8509803921568627],
                [0.8431372549019608, 0.8431372549019608, 0.8431372549019608],
                [0.8352941176470589, 0.8352941176470589, 0.8352941176470589],
                [0.8235294117647058, 0.8235294117647058, 0.8235294117647058],
                [0.8156862745098039, 0.8156862745098039, 0.8156862745098039],
                [0.807843137254902, 0.807843137254902, 0.807843137254902],
                [0.8, 0.8, 0.8],
                [0.792156862745098, 0.792156862745098, 0.792156862745098],
                [0.7843137254901961, 0.7843137254901961, 0.7843137254901961],
                [0.7764705882352941, 0.7764705882352941, 0.7764705882352941],
                [0.7686274509803922, 0.7686274509803922, 0.7686274509803922],
                [0.7607843137254902, 0.7607843137254902, 0.7607843137254902],
                [0.7529411764705882, 0.7529411764705882, 0.7529411764705882],
                [0.7450980392156863, 0.7450980392156863, 0.7450980392156863],
                [0.7372549019607844, 0.7372549019607844, 0.7372549019607844],
                [0.7294117647058823, 0.7294117647058823, 0.7294117647058823],
                [0.7215686274509804, 0.7215686274509804, 0.7215686274509804],
                [0.7137254901960784, 0.7137254901960784, 0.7137254901960784],
                [0.7058823529411765, 0.7058823529411765, 0.7058823529411765],
                [0.6980392156862745, 0.6980392156862745, 0.6980392156862745],
                [0.6901960784313725, 0.6901960784313725, 0.6901960784313725],
                [0.6823529411764706, 0.6823529411764706, 0.6823529411764706],
                [0.6745098039215687, 0.6745098039215687, 0.6745098039215687],
                [0.6666666666666666, 0.6666666666666666, 0.6666666666666666],
                [0.6588235294117647, 0.6588235294117647, 0.6588235294117647],
                [0.6509803921568628, 0.6509803921568628, 0.6509803921568628],
                [0.6431372549019608, 0.6431372549019608, 0.6431372549019608],
                [0.6352941176470588, 0.6352941176470588, 0.6352941176470588],
                [0.6274509803921569, 0.6274509803921569, 0.6274509803921569],
                [0.6196078431372549, 0.6196078431372549, 0.6196078431372549],
                [0.611764705882353, 0.611764705882353, 0.611764705882353],
                [0.6039215686274509, 0.6039215686274509, 0.6039215686274509],
                [0.596078431372549, 0.596078431372549, 0.596078431372549],
                [0.5882352941176471, 0.5882352941176471, 0.5882352941176471],
                [0.5803921568627451, 0.5803921568627451, 0.5803921568627451],
                [0.5725490196078431, 0.5725490196078431, 0.5725490196078431],
                [0.5647058823529412, 0.5647058823529412, 0.5647058823529412],
                [0.5568627450980392, 0.5568627450980392, 0.5568627450980392],
                [0.5490196078431373, 0.5490196078431373, 0.5490196078431373],
                [0.5411764705882353, 0.5411764705882353, 0.5411764705882353],
                [0.5333333333333333, 0.5333333333333333, 0.5333333333333333],
                [0.5254901960784314, 0.5254901960784314, 0.5254901960784314],
                [0.5176470588235295, 0.5176470588235295, 0.5176470588235295],
                [0.5098039215686274, 0.5098039215686274, 0.5098039215686274],
                [0.5019607843137255, 0.5019607843137255, 0.5019607843137255],
                [0.49019607843137253, 0.49019607843137253, 0.49019607843137253],
                [0.4823529411764706, 0.4823529411764706, 0.4823529411764706],
                [0.4745098039215686, 0.4745098039215686, 0.4745098039215686],
                [0.4666666666666667, 0.4666666666666667, 0.4666666666666667],
                [0.4588235294117647, 0.4588235294117647, 0.4588235294117647],
                [0.45098039215686275, 0.45098039215686275, 0.45098039215686275],
                [0.44313725490196076, 0.44313725490196076, 0.44313725490196076],
                [0.43529411764705883, 0.43529411764705883, 0.43529411764705883],
                [0.42745098039215684, 0.42745098039215684, 0.42745098039215684],
                [0.4196078431372549, 0.4196078431372549, 0.4196078431372549],
                [0.4117647058823529, 0.4117647058823529, 0.4117647058823529],
                [0.403921568627451, 0.403921568627451, 0.403921568627451],
                [0.396078431372549, 0.396078431372549, 0.396078431372549],
                [0.38823529411764707, 0.38823529411764707, 0.38823529411764707],
                [0.3803921568627451, 0.3803921568627451, 0.3803921568627451],
                [0.37254901960784315, 0.37254901960784315, 0.37254901960784315],
                [0.36470588235294116, 0.36470588235294116, 0.36470588235294116],
                [0.3568627450980392, 0.3568627450980392, 0.3568627450980392],
                [0.34901960784313724, 0.34901960784313724, 0.34901960784313724],
                [0.3411764705882353, 0.3411764705882353, 0.3411764705882353],
                [0.3333333333333333, 0.3333333333333333, 0.3333333333333333],
                [0.3254901960784314, 0.3254901960784314, 0.3254901960784314],
                [0.3176470588235294, 0.3176470588235294, 0.3176470588235294],
                [0.30980392156862746, 0.30980392156862746, 0.30980392156862746],
                [0.30196078431372547, 0.30196078431372547, 0.30196078431372547],
                [0.29411764705882354, 0.29411764705882354, 0.29411764705882354],
                [0.28627450980392155, 0.28627450980392155, 0.28627450980392155],
                [0.2784313725490196, 0.2784313725490196, 0.2784313725490196],
                [0.27058823529411763, 0.27058823529411763, 0.27058823529411763],
                [0.2627450980392157, 0.2627450980392157, 0.2627450980392157],
                [0.2549019607843137, 0.2549019607843137, 0.2549019607843137],
                [0.24705882352941178, 0.24705882352941178, 0.24705882352941178],
                [0.23921568627450981, 0.23921568627450981, 0.23921568627450981],
                [0.23137254901960785, 0.23137254901960785, 0.23137254901960785],
                [0.2235294117647059, 0.2235294117647059, 0.2235294117647059],
                [0.21568627450980393, 0.21568627450980393, 0.21568627450980393],
                [0.20784313725490197, 0.20784313725490197, 0.20784313725490197],
                [0.2, 0.2, 0.2],
                [0.19215686274509805, 0.19215686274509805, 0.19215686274509805],
                [0.1843137254901961, 0.1843137254901961, 0.1843137254901961],
                [0.17647058823529413, 0.17647058823529413, 0.17647058823529413],
                [0.16862745098039217, 0.16862745098039217, 0.16862745098039217],
                [0.1568627450980392, 0.1568627450980392, 0.1568627450980392],
                [0.14901960784313725, 0.14901960784313725, 0.14901960784313725],
                [0.1411764705882353, 0.1411764705882353, 0.1411764705882353],
                [0.13333333333333333, 0.13333333333333333, 0.13333333333333333],
                [0.12549019607843137, 0.12549019607843137, 0.12549019607843137],
                [0.11764705882352941, 0.11764705882352941, 0.11764705882352941],
                [0.10980392156862745, 0.10980392156862745, 0.10980392156862745],
                [0.10196078431372549, 0.10196078431372549, 0.10196078431372549],
                [0.09411764705882353, 0.09411764705882353, 0.09411764705882353],
                [0.08627450980392157, 0.08627450980392157, 0.08627450980392157],
                [0.0784313725490196, 0.0784313725490196, 0.0784313725490196],
                [0.07058823529411765, 0.07058823529411765, 0.07058823529411765],
                [0.06274509803921569, 0.06274509803921569, 0.06274509803921569],
                [0.054901960784313725, 0.054901960784313725, 0.054901960784313725],
                [0.047058823529411764, 0.047058823529411764, 0.047058823529411764],
                [0.0392156862745098, 0.0392156862745098, 0.0392156862745098],
                [0.03137254901960784, 0.03137254901960784, 0.03137254901960784],
                [0.023529411764705882, 0.023529411764705882, 0.023529411764705882],
                [0.01568627450980392, 0.01568627450980392, 0.01568627450980392],
                [0.00784313725490196, 0.00784313725490196, 0.00784313725490196],
                [0.8156862745098039, 0.8156862745098039, 0.8156862745098039],
                [1.0, 1.0, 1.0]]


     return colors[::(-1)**int(reverse)]
