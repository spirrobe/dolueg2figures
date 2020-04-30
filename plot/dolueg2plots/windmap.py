#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# """
# Created on Fri Nov 30 15:52:51 2018
#
# @author: spirro00
# """

import numpy as np
import matplotlib.pyplot as plt


def windmap(lats,
            lons,
            data,
            fig=None,
            lineopt=None,
            figopt=None,
            offset=None,
            sectorsize=15,
            # how much lighter the map should look
            mapalpha=0.85,
            # how much lighter the stations/windroses should look
            stationalpha=0.8,
            # how much space surrounding the inner border should be protected
            reservedspace=0.1,
            quiet=True,
            maptype=1,
            windspeedcodes=None,
            winddircodes=None,
            meta=None,
            fontsize=15,
            mapfullscreen=False,
            **kwargs
            ):

    import numpy as np

    from scipy.spatial import distance

    from map.mapurl import mapurl
    from map.getstaticmap import getstaticmap
    from map.webmapextent import webmapextent
    from map.webmapresolution  import webmapresolution
    from plot.dolueg2plots.windrose import windrose

    from plot.dolueg2plots.gropt import defaultfigopt, defaultlineopt, \
                                        updateopt, \
                                        baseround, \
                                        defaultct, \
                                        autoranger, autotimeaxis, \
                                        acceptedopt, extendopt

    _figopt = defaultfigopt()
    if figopt is not None:
        for i in figopt:
            _figopt[i] = figopt[i]



    if fig is None:
        squaredfig = [max(_figopt['figsize'])]*2
        fig, ax = plt.subplots(figsize=squaredfig,
                               dpi=_figopt['figdpi']
                               )
    elif len(fig) == 2:
        fig, ax = fig
    else:
        ax = fig.gca()

    # ensure squared
    if fig.get_figwidth() != fig.get_figheight():
        fmax = max([fig.get_figwidth(), fig.get_figheight()])
        fig.set_figwidth(fmax)
        fig.set_figheight(fmax)

#    ax.set_aspect('equal')

    # mapurl takes care of calculation the extent/zoom/lons/lats
    url = mapurl(lat=lats, lon=lons, maptype=maptype)

    # nothing else to pass in
    mapimg = getstaticmap(url)
    extent = webmapextent(url)
    resolution = webmapresolution(url)

    aspect = (extent[1]-extent[0])/(extent[3]-extent[2])
    aspect = abs(aspect)

    if type(mapimg) == np.ndarray:
        pass
    else:
        mapimg=np.zeros((640, 480, 3), dtype=np.int)

    ax.imshow(np.flip(mapimg,axis=0),
              aspect=aspect,#'equal',
              origin='auto',
              zorder=10,
              vmin=0, vmax=255,
              interpolation='None',
              alpha=mapalpha,
              extent=extent,
              rasterized=True,
              )
    if mapfullscreen:
        ax.axis('off')
    else:
        plt.tick_params(axis='both',
                        right='on',
                        left='on',
                        labelright='on',
                        labelleft='on',
                        bottom='on',
                        top='on',
                        labelbottom='on',
                        labeltop='on')

    if winddircodes is None and meta:
        winddircodes = [m for m in meta
                        if meta[m]['variable'].upper() == 'WDA'
                        or meta[m]['name'].upper() == 'WIND DIRECTION']
    elif winddircodes:
        pass
    else:
        winddircodes = [c for c in data.columns if 'WDA' in c.upper()]

    if winddircodes is None and meta:
        windspeedcodes = [m for m in meta
                          if meta[m]['variable'].upper() != 'WVA'
                          and meta[m]['name'].upper() != 'WIND SPEED']
    elif windspeedcodes:
        pass
    else:
        windspeedcodes = [c for c in data.columns if 'WVA' in c.upper()]

    if windspeedcodes and winddircodes:
        pass
    else:
        print('No wind direction / wind speed codes found, please adjust',
              ' the database entires to the proper default')
        return fig


    if len(windspeedcodes) != len(winddircodes):
        print('Unequal amount of wind direction and wind speed codes')
        return fig

    data = data.copy().dropna(how='all')
    dirdata = data[winddircodes]
    speeddata = data[windspeedcodes]

    ax.grid(zorder=12, color='k')

    xtl = [str(round(i,3))+'° W' if i < 0 else str(round(i,3))+'° E' for i in ax.get_xticks()]
    ytl = [str(round(i,3))+'° S' if i < 0 else str(round(i,3))+'° N' for i in ax.get_yticks()]
    if mapfullscreen:
        plt.margins(0, 0)
        ax.set_axis_off()
        fig.subplots_adjust(top = 1,
                            bottom = 0,
                            right = 1,
                            left = 0,
                            hspace = 0,
                            wspace = 0)
    else:
        ax.set_yticklabels(ytl,
                           fontsize=fontsize*0.75)
        ax.set_xticklabels(xtl,
                           rotation=90,
                           fontsize=fontsize*0.75)
    fig.tight_layout()
    plt.draw()
    xlim, ylim = extent[:2], extent[2:]

    # calculate positions of stations in imagecoordinates ( 0-1, 0-1)
    imgcoord = [[(x-extent[0])/(extent[1]-extent[0]),
                (y-extent[2])/(extent[3]-extent[2])]
                for x, y in zip(lons, lats)]

    imgcoord = [[x, y] for x, y in zip(lons, lats)]

    if len(lats) == 1 or len(lons) == 1:
        # since its only once station, the minimumdistance is 1, i.e. whole map
        # as we always should be in the middle of the map but give some space
        # for the labels with *0.9
        mindist = np.nanmin([np.diff(xlim), np.diff(ylim)]) * 0.9
        # if mindist > 0.1:
        #     mindist = 0.05
    else:
        dists = distance.cdist(imgcoord, imgcoord, )

        mindist = np.min(dists[dists>0])

    # ensure this mindist wont result in touching any of the sides of the figure
    # by making sure there is at least 0.05 space around the sides of the map
    halfmindist = mindist / 2

    windroseaxes = []

    plt.draw()

    for xy, d, s in zip(imgcoord, dirdata, speeddata,):
        x, y = xy

        tr1 = ax.transData.transform([(x-halfmindist, y-halfmindist),
                                      (x+halfmindist, y+halfmindist)])
        tr2 = fig.transFigure.inverted().transform(tr1)

        data2figcoord = [tr2[0, 0],
                         tr2[0, 1],
                         tr2[1, 0]-tr2[0, 0],
                         tr2[1, 1]-tr2[0, 1],]

        windroseaxes.append(fig.add_axes(data2figcoord,
                                         projection='polar',
                                         anchor ='C',
                                         frameon=True))

        # ct = defaultct()
        # import matplotlib.colors as colors
        # new_cmap = colors.LinearSegmentedColormap.from_list('dolueg2', ct)
        #if 'speedstep' in kwargs:
        #    speedstep = speedstep
        #@   kwargs.pop('speedstep')
        #else:
        #    speedstep = 1
        p = windrose(dirdata[d],
                     speeddata[s],
                     ringofsums=True,
                     ringlegend=False,
                     #speedstep=speedstep,
                     maxspeed=np.ceil(speeddata.max().max()*2)//2,
#                     makeleg=False,
                     legendlocation=[0.5,0.1],
                     sectorsize=sectorsize,
                     legloc='center',
                     addwatermark=False,
                     cmap2='Greys',
                     figure=fig,
                     fontsize=fontsize,
                     outerlabelcolor='k',
                     savefigas=False,
                     axes=windroseaxes[-1],
                     xlabel=None,
                     makeleg=xy==imgcoord[0],
                     coloremptybackground=True,
                     **kwargs)

        windroseaxes[-1].set_facecolor([1, 1, 1, stationalpha])

    # cornercoordinates of rectangle in the topleft corner
    topleftscale = 0.1
    topleftscale *= fontsize/15
    topleft = [[xlim[0],
               xlim[0]+(xlim[1]-xlim[0])*topleftscale,
               xlim[0]+(xlim[1]-xlim[0])*topleftscale,
               xlim[0], ],
               [ylim[1]-(ylim[1]-ylim[0])*topleftscale * 1.25,
                ylim[1]-(ylim[1]-ylim[0])*topleftscale * 1.25,
                ylim[1], ylim[1], ],
               ]

    # cornercoordinates of rectangle in the topright corner
    toprightwidth, toprightheight = 0.125, 0.125
    toprightwidth *= fontsize/15
    toprightheight*= fontsize/15

    topright = [[xlim[1]-(xlim[1]-xlim[0])*toprightwidth,
                 xlim[1], xlim[1], xlim[1]-(xlim[1]-xlim[0])*toprightwidth,
                 ],
               [ylim[1]-(ylim[1]-ylim[0])*toprightheight,
                ylim[1]-(ylim[1]-ylim[0])*toprightheight,
                ylim[1], ylim[1],
                ],
               ]

    # roll so we can use the same logic for the frame below
    topright = np.roll(topright, 1, axis=1)

    # create boxes in corners for information
    ax.fill(topleft[0], topleft[1], 'k', zorder=15,  alpha=0.75)
    ax.plot(topleft[0][:3], topleft[1][:3], 'w', lw=1.5, zorder=15,  alpha=1)

    ax.fill(topright[0], topright[1], 'k', zorder=15, alpha=0.75)
    ax.plot(topright[0][:3], topright[1][:3], 'w', lw=1.5, zorder=15, alpha=1)

    # N letter for North with small arrow behind it
    # resolution is the full map width/height
    thisres = topleftscale * resolution * mapimg.shape[0]

    if thisres <= 1500:
        roundfact = 100
    else:
        roundfact = 1000

    roundedres = np.floor(thisres/roundfact)*roundfact

    # ensure everything fits into the box with some space
    while roundedres / thisres >= 0.9:
        roundedres -= roundfact


    # width/heigth of the box as boxunits
    bu = [max(topleft[0])-min(topleft[0]),
          max(topleft[1])-min(topleft[1])]

    # could use ax.arrow, but its a headache getting it right
    arrowtopoffset = [0.5*(max(topleft[0])-min(topleft[0]))+min(topleft[0]),
                   min(topleft[1])+0.8*(max(topleft[1])-min(topleft[1]))]

    arrowbotoffset = [0.5*(max(topleft[0])-min(topleft[0]))+min(topleft[0]),
                      min(topleft[1])+0.525*(max(topleft[1])-min(topleft[1]))]

    arrowtop = [[0, 0, -bu[0] * 0.075, 0, bu[0] * 0.075 ],
                [0, bu[1]*0.125, bu[1]*0.05, bu[1]*0.125, bu[1]*0.05], ]
    arrowbottom = [[0, 0, ],
                   [0, bu[1]*0.05, ], ]

    arrowtoppart = [[i+arrowtopoffset[0] for i in arrowtop[0]],
                    [i+arrowtopoffset[1] for i in arrowtop[1]], ]

    arrowbotpart = [[i+arrowbotoffset[0] for i in arrowbottom[0]],
                    [i+arrowbotoffset[1] for i in arrowbottom[1]], ]

    ax.plot(arrowtoppart[0],
            arrowtoppart[1],
            color='w',
            zorder=17,
            alpha=1,
            lw=1.2,
            )

    ax.plot(arrowbotpart[0],
            arrowbotpart[1],
            color='w',
            zorder=17,
            alpha=1,
            lw=1.2,
            )


    scalewidth = bu[0] * roundedres / thisres
    scaleheight = bu[1] * 0.1

    scaleoffset = [0.5*bu[0]+min(topleft[0]),
                   min(topleft[1])+0.15*bu[1]]

    scalebar = [[-scalewidth/2, -scalewidth/2, -scalewidth/2, # left part
                 scalewidth/2, scalewidth/2, scalewidth/2, # right part
                 ],
                [-scaleheight/2, scaleheight/2, 0,0,scaleheight/2, -scaleheight/2],
                ]

    scalebar = [[i+scaleoffset[0] for i in scalebar[0]],
                [i+scaleoffset[1] for i in scalebar[1]],]

    ax.plot(scalebar[0],
            scalebar[1],
            color='w',
            zorder=17,
            alpha=1,
            lw=1.2,
            )

    ax.text(np.mean(topleft[0][:2]),
            (arrowtoppart[1][0] + arrowbotpart[1][-1])/2,
            'N',
            fontsize=fontsize,
            color='w',
            ha='center',
            va='center',
            zorder=18,
            alpha=1,
            )

    ax.text(np.mean(topleft[0][:2]),
            scalebar[1][2]+0.075*bu[1],
            str(int(roundedres))+' m',
            fontsize=fontsize,
            color='w',
            ha='center',
            va='bottom',
            zorder=18,
            alpha=1,
            )


    tf = '%d.%m.%Y'
    ax.text(np.mean(topright[0]),
            np.mean(topright[1]),
            'Timerange:\n'+data.index[0].strftime(tf)+'\nto\n'+data.index[-1].strftime(tf),
            fontsize=fontsize-2,
            color='w',
            ha='center',
            va='center',
            zorder=18,
            alpha=1,
            )

    return fig

if __name__ == '__main__':
    print('*'*10, 'HELP for main', '*'*10)
    print('Describe shortly what this is supposed to do')
    print('Maybe help out a bit with keyword to make it clearer for people',)

    # from mcr.sql.util import getmetatables, getdata
#    metatables = getmetatables('fognetdb', metas='sdt')['sdt']
#    lons, lats, names = [], [], []
#    coords = []
#
#    for stat in metatables:
#        coords.append([round(i, 2) for i in stat[4:6]])
#        names.append(stat[1]+' ('+stat[0]+')')
#
#    coor = np.array(coords)
#    coor_tuple = [tuple(x) for x in coor]
#    unique_coor = sorted(set(coor_tuple), key=lambda x: coor_tuple.index(x))
#    unique_count = [coor_tuple.count(x) for x in unique_coor]
#    unique_index = [coor_tuple.index(x) for x in unique_coor]
#    names = [i for no, i in enumerate(names) if no in unique_index]
#
#    lons = [i[1] for i in unique_coor]
#    lats = [i[0] for i in unique_coor]


#     lons = [7.58050247629464]
#     lats = [47.56169689110803]
#     data, meta = getdata(['BKLIWVA1','BKLIWDA1','BLEOWVA1','BLEOWDA1'],
#                          t0='*-307', t1='*-120',) # t1='*-300')
#     data[data['BKLIWDA1'].eq(0)] = np.nan

#     lats = [meta[k]['lat'] for k in data][::2]
#     lons = [meta[k]['lon'] for k in data][::2]

#     lons[0] = 7.580496
#     lats[0] = 47.561607
#     b = windmap(lats, lons, data,)
# #    b = windmap([lats[0]], [lons[0]], data[data.columns[:2]],)
# #    b = stationmap(lats, lons, ['Bla',)
# #    main()

# lats = [47.53666645]
# lons = [7.60790033]
# codes = ['UFBCWWD', 'UFBCWWV']
# t0, t1, dt ='*-31', '*', '1Min'
# d, m = getdata(codes, t0=t0, t1=t1, dt=dt,)
# b = windmap(lats, lons, d,
#             winddircodes=['UFBCWWD',],
#             windspeedcodes=['UFBCWWV',],
#             mapfullscreen=True,
#             stationalpha=0.5)

