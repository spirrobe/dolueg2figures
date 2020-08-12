#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# """
# Created on Fri Nov 30 15:53:02 2018
#
# @author: spirro00
# """

#
# import numpy as np
# import matplotlib.pyplot as plt
# from mpl_toolkits.basemap import Basemap

# be aware that since we do not use basemap or cartopy
# our projection is somewhat limited in the extent we can show and still
# be correct (approximately) to the position of stations
# we do not use the two to make it more accessible (and basemap is outdated?)

def stationmap(lats,
               lons,
               names,
               fig=None,
               lineopt=None,
               figopt=None,
               offset=None,
               mapalpha=0.75,
               stationalpha=0.85,
               fontsize=18,
               markersize=24,
               quiet=True,
               **kwargs,
               ):


    import numpy as np
    import matplotlib.pyplot as plt

    from map.mapurl import mapurl
    from map.getstaticmap import getstaticmap
    from map.webmapextent import webmapextent
    from map.webmapresolution  import webmapresolution
    from plot.dolueg2plots.watermark import watermark
    from plot.dolueg2plots.windrose import windrose
    from plot.dolueg2plots.watermark import watermark

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
        fig, ax = plt.subplots(figsize=squaredfig)
    elif len(fig) == 2:
        fig, ax = fig
    else:
        ax = fig.gca()

    # ensure squared
    if fig.get_figwidth() != fig.get_figheight():
        fmax = max([fig.get_figwidth(), fig.get_figheight()])
        fig.set_figwidth(fmax)
        fig.set_figheight(fmax)


    ax.set_aspect('equal')

    # mapurl takes care of calculation the extent/zoom/lons/lats
    url = mapurl(lat=lats, lon=lons,)

    # nothing else to pass in
    mapimg = getstaticmap(url)
    extent = webmapextent(url)
    resolution = webmapresolution(url)

    aspect = (extent[1]-extent[0])/(extent[3]-extent[2])
    aspect = abs(aspect)

    ax.imshow(np.flip(mapimg, axis=0),
              aspect=aspect,
              origin='auto',
              zorder=10,
              vmin=0, vmax=255,
              interpolation='None',
              alpha=mapalpha,
              extent=extent
              )

    plt.tick_params(axis='both',
                    right='on',
                    left='on',
                    labelright='on',
                    labelleft='on',
                    bottom='on',
                    top='on',
                    labelbottom='on',
                    labeltop='on',
                    # fontsize=fontsize,
                    )

    plt.autoscale(False)

    lt = _figopt['legtitle'] #'Stationlist\n'
    if lt:
        lt += '\n'
    else:
        lt = ''

    uniquelocs, uniquenumbers = [], []
    for no, xyn in enumerate(zip(lons, lats, names)):
        if xyn[:2] in uniquelocs:
            uniquenumbers[uniquelocs.index(xyn[:2])] += ','+str(no+1)
        else:
            ax.plot(xyn[0], xyn[1] + (extent[-1]-extent[-2])*0.001,
                    marker='o',
                    markerfacecolor='w',
                    markeredgecolor='k',
                    markersize=markersize,
                    zorder=15)
            # append the coordinates
            uniquelocs += [xyn[:2]]
            uniquenumbers += [str(no+1)]
            # print(xyn[:2],uniquelocs)
            # uniquelocs.index(xyn[:2]))

        if len(names) >= 10 and no < 9:
            spacer = '  '
        else:
            spacer = ''
        lt += str(no+1)+': '+spacer+xyn[2]+'\n'


    for xyn in zip(uniquelocs, uniquenumbers):
        if ',' in xyn[1]:
            ax.text(xyn[0][0], xyn[0][1], xyn[1], color='k',
                    ha='center', va='center',
                    zorder=20, fontsize=fontsize,
                    bbox=dict(boxstyle='round', fc="w", ec="k",
                              alpha=stationalpha)
                    )
        else:
            ax.text(xyn[0][0], xyn[0][1], xyn[1], color='k',
                    ha='center', va='center',
                    zorder=20, fontsize=fontsize,
                    # bbox=dict(boxstyle='round', fc="w", ec="k",
                    #           alpha=stationalpha)
                    )

    plt.tick_params(labeltop=True, labelright=True)

    ax.grid(zorder=12, color='k')

    xtl = [str(round(i,3))+'° W' if i < 0 else str(round(i,3))+'° E'
           for i in ax.get_xticks()]
    ytl = [str(round(i,3))+'° S' if i < 0 else str(round(i,3))+'° N'
           for i in ax.get_yticks()]

    ax.set_yticklabels(ytl,
                       fontsize=fontsize*0.75)

    ax.set_xticklabels(xtl,
                        rotation=90,
                        fontsize=fontsize*0.75)

    fig.tight_layout()

    lt = lt[:-1]
    # legend
    ax.text((extent[1]-extent[0])*0.03+extent[0],
            extent[3]-(extent[3]-extent[2])*(0.035),
            lt,
            color='k',
            ha='left', va='top',
            zorder=20,
            fontsize=fontsize,
            bbox=dict(boxstyle='round,pad=0.6', fc="w", ec="k",
                      alpha=_figopt['legalpha'],)
            )

    # cornercoordinates of rectangle in the topright corner
    toprightwidth, toprightheight = 0.1, 0.1
    toprightwidth *= fontsize/15
    toprightheight *= fontsize/15


    xlim, ylim = extent[:2], extent[2:]
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

    ax.fill(topright[0], topright[1], 'k', zorder=15, alpha=0.75)
    ax.plot(topright[0][:3], topright[1][:3], 'w', lw=1.5, zorder=15, alpha=1)

    thisres = toprightwidth * resolution * mapimg.shape[0]

    if thisres <= 1500:
        roundfact = 100
    else:
        roundfact = 1000

    roundedres = np.floor(thisres/roundfact)*roundfact

    # ensure everything fits into the box with some space
    while roundedres / thisres >= 0.9:
        roundedres -= roundfact

    # width/heigth of the box as boxunits
    bu = [max(topright[0])-min(topright[0]),
          max(topright[1])-min(topright[1])]

    # could use ax.arrow, but its a headache getting it right
    arrowtopoffset = [0.5*(max(topright[0])-min(topright[0]))+min(topright[0]),
                   min(topright[1])+0.8*(max(topright[1])-min(topright[1]))]

    arrowbotoffset = [0.5*(max(topright[0])-min(topright[0]))+min(topright[0]),
                      min(topright[1])+0.525*(max(topright[1])-min(topright[1]))]

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

    scaleoffset = [0.5*bu[0]+min(topright[0]),
                   min(topright[1])+0.15*bu[1]]

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

    ax.text(np.mean(topright[0][1:3]),
            (arrowtoppart[1][0] + arrowbotpart[1][-1])/2,
            'N',
            fontsize=fontsize,
            color='w',
            ha='center',
            va='center',
            zorder=18,
            alpha=1,
            )

    if roundedres <= 1000:
        ax.text(np.mean(topright[0][1:3]),
                scalebar[1][2]+0.075*bu[1],
                str(int(roundedres))+' m',
                fontsize=fontsize,
                color='w',
                ha='center',
                va='bottom',
                zorder=18,
                alpha=1,
                )
    else:
        ax.text(np.mean(topright[0][1:3]),
                scalebar[1][2]+0.075*bu[1],
                str(int(roundedres/1000))+' km',
                fontsize=fontsize,
                color='w',
                ha='center',
                va='bottom',
                zorder=18,
                alpha=1,
                )



    return fig

if __name__ == '__main__':
    print('*'*10, 'HELP for main', '*'*10)
    print('Describe shortly what this is supposed to do')
    print('Maybe help out a bit with keyword to make it clearer for people',)

#     from mcr.sql.util import getmetatables
#     import numpy as np

# #     metatables = getmetatables('messnetzdb', metas='sdt')['sdt']
# #     lons, lats, names = [], [], []
# #     coords = []

# #     for stat in metatables:
# #         if stat[0] not in ['BKLI','BLEO']:
# #             continue
# #         coords.append([round(i, 5) for i in stat[4:6]])
# #         names.append(stat[1]+' ('+stat[0]+')')

# #     coor = np.array(coords)
# #     coor_tuple = [tuple(x) for x in coor]
# #     unique_coor = sorted(set(coor_tuple), key=lambda x: coor_tuple.index(x))
# #     unique_count = [coor_tuple.count(x) for x in unique_coor]
# #     unique_index = [coor_tuple.index(x) for x in unique_coor]
# #     names = [i for no, i in enumerate(names) if no in unique_index]

# #     lons = [i[1] for i in unique_coor]
# #     lats = [i[0] for i in unique_coor]


# # #    lons[0] = 7.580496
# # #    lats[0] = 47.561607

# #     b = stationmap(lats, lons, names,)

#     metatables = getmetatables('fognetdb', metas='sdt')['sdt']
#     lons, lats, names = [], [], []
#     coords = []

#     for stat in metatables:
#         coords.append([round(i, 2) for i in stat[4:6]])
#         names.append(stat[1]+' ('+stat[0]+')')

#     coor = np.array(coords)
#     coor_tuple = [tuple(x) for x in coor]
#     unique_coor = sorted(set(coor_tuple), key=lambda x: coor_tuple.index(x))
#     unique_count = [coor_tuple.count(x) for x in unique_coor]
#     unique_index = [coor_tuple.index(x) for x in unique_coor]
#     names = [i for no, i in enumerate(names) if no in unique_index]

#     lons = [i[1] for i in unique_coor]
#     lats = [i[0] for i in unique_coor]

#     b = stationmap(lats, lons, names, fontsize=18)
