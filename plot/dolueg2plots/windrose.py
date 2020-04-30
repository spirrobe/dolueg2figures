#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 17 21:26:15 2017

@author: spirro00
"""
import numpy as np

def windrose(dirdata,
             speeddata,
             figure=None,
             axes=None,
             sectorsize=15,
             speedstep=1,
             minspeed=0,
             maxspeed=None,
             speedbins=None,
             ringofsums=True,
             ringofsumagg='sum',
             ringlegend=True,
#             ringofsumagg=np.nansum,
             sumringdist=3,
             hideempty=True,
             coloremptybackground=False,
             normalize=True,
             midoffset=0.1,
             figsize=(7, 7),
             xlabel='Wind direction [°]',
             cmap='nipy_spectral',
             cmap2='RdGy_r',
             middletext=None,
             truncate_cmap=[0.2, 1],
             outerlabelcolor='black',
             innerlabelcolor='black',
             fontsize=8,
             edgecolor='white',
             labelposition='auto',
             bigsumring=True,
             azoffset=0,
             savefigas='/media/spirro00/Data/unibas/phd/python/windrose.png',
             asdeg=True,
             azoffsetasdeg=True,
             seperatebars=True,
             barwidth=0.9,
             makeleg=True,
             legendlocation=(1, 0.0),
             legloc='right',
             realcount=None,
             freqlim='auto',
             legcol='auto',
             showlabel=False,
#             istalk=False,
             addwatermark=True,
             **kwargs
             ):

    # import the libraries we need
    import matplotlib.pyplot as plt
    from plot.dolueg2plots.watermark import watermark
    import numpy as np
    import os
    import matplotlib.colors as colors

#    if istalk:
#        import seaborn as sns
#        sns.set_context('talk')

    def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=200):
        new_cmap = colors.LinearSegmentedColormap.from_list(
            'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name,
                                                a=minval,
                                                b=maxval),
            cmap(np.linspace(minval, maxval, n)))
        return new_cmap

#    plt.figure()

    if azoffset:
        if not azoffsetasdeg:
            azoffset = np.rad2deg(azoffset)
        if azoffset < 0:
            azoffset += 360

    if not cmap2:
        cmap2 = cmap
    else:
        cmap2 = plt.get_cmap(cmap2)
        cmap2 = truncate_colormap(cmap2, truncate_cmap[0], truncate_cmap[-1])

    if type(cmap) == str:
        cmap = plt.get_cmap(cmap)
    else:
        cmap = cmap

    # cmap = truncate_colormap(cmap, truncate_cmap[0], truncate_cmap[-1])
    if figure is None:
        fig, ax = plt.subplots(ncols=1,
                               nrows=1,
                               figsize=figsize,
                               subplot_kw={'projection': 'polar',
                                           'aspect': 1},
                               )
    else:
        fig = figure
        if axes is None:
            ax = fig.gca()
        else:
            ax = axes

    ax.set_theta_direction(-1)
    ax.set_theta_offset(0.5 * np.pi)

    if speedbins is None:
        if minspeed is None:
            minspeed = np.nanmin(speeddata)
            if minspeed < 1 or np.isnan(minspeed):
                minspeed = 0

            minspeed = np.floor(minspeed)

        if maxspeed is None:
            maxspeed = np.ceil(np.nanmax(speeddata)/5)*5
            maxspeed = np.ceil(np.nanmax(speeddata)/speedstep)*speedstep

            #if maxspeed % 2:
            #    maxspeed += 1

            if maxspeed > 50:
                maxspeed = np.ceil(np.nanmax(speeddata)/10)*10

        if np.isnan(maxspeed):
            maxspeed = 5
        else:
            maxspeed = int(maxspeed)

    else:
        maxspeed = int(np.ceil(max(speedbins)))
        minspeed = int(np.floor(min(speedbins)))

    speedbins = np.arange(minspeed, maxspeed+speedstep, speedstep)

    if len(speedbins) < 4:
        speedstep = speedstep / 2
        speedbins = np.arange(minspeed, maxspeed+speedstep, speedstep)

    print(speedbins)

    mindir = np.nanmin(dirdata)

    if mindir is np.nan:
        mindir = 0

    if mindir < 0:
        mindir = -180
    else:
        mindir = 0

    maxdir = np.nanmax(dirdata)

    if maxdir is np.nan:
        maxdir = 360

    if maxdir > 180:
        maxdir = 360
    else:
        maxdir = 180

    # in case we dont have enough data to find the full range
    if mindir == 0 and maxdir == 180:
        maxdir = 360
    elif mindir == -180 and maxdir == 360:
        maxdir == 180


    if (360 % sectorsize) != 0:
        sectorsize = np.round(sectorsize)

    while (360 % sectorsize) != 0:
        sectorsize += 1

    # birbins is the leftedge
    dirbins = np.arange(mindir, maxdir+sectorsize, sectorsize)
    halfsector = sectorsize / 2
    dirbins = dirbins - halfsector


    # work on a copy to not alter other things
    dirdata_tmp = dirdata.copy()
    # wrap the direction north plus minus halfsector around
    dirdata_tmp[dirdata_tmp > (maxdir-halfsector)] -= 360

    freq, speedloc, dirloc = np.histogram2d(speeddata,
                                            dirdata_tmp,
                                            bins=[speedbins, dirbins])

    if hideempty:
        ofreq = freq.copy()
        freq[freq == 0] = np.nan
        ofreq[ofreq != 0] = np.nan

    if normalize:
        if realcount is None:
            freq = freq / np.nansum(freq) * 100
        else:
            freq = freq / realcount * 100

    freqsum = np.nancumsum(freq, axis=0)

    if midoffset < 1:
        midoffset = np.nanmax(freqsum) * midoffset

#    maximumamount = np.nansum(freqsum,)
    added2legend = []

    if barwidth != 1:
        brsc = (1-barwidth)/2
    else:
        brsc = 0

    for directionno, direction in enumerate(dirloc[:-1]):
        this = freqsum[:, directionno]

        for i, ii in enumerate(this):

            if i == 0:
                zero = 0
            else:
                zero = this[i-1]

            theta = np.arange(dirloc[directionno],
                              dirloc[directionno+1],
                              0.05)

            if brsc:
                theta = theta[int(brsc*len(theta)):-int(brsc*len(theta))]

            theta = np.deg2rad(np.concatenate((theta, theta[::-1])))

            r = np.zeros(theta.shape)
            r[:r.shape[0]//2] = ii
            r[r.shape[0]//2:] = zero

            if type(cmap) == list:
                thecolor = cmap[i % len(cmap)]
            else:
                thecolor = cmap(int(i/len(this) * cmap.N))

            patch = ax.fill(theta, r,
                             '_',
                             linewidth=0,
                             alpha=1,
                             zorder=10,
                             color=thecolor,
                             edgecolor='#000000')

            if speedbins[i] not in added2legend:

                added2legend.append(speedbins[i])
                thislabel = speedbins[i]

                if speedbins[i] == speedbins[-1]:
                    patch[0].set_label(str(thislabel) + ' - ' + str(thislabel + speedstep))
                else:
                    patch[0].set_label(str(thislabel) + ' - ' + str(speedbins[i+1]))

            if seperatebars:
                if ii != zero:

                    magseperator = ax.plot(theta[:theta.shape[0]//2],
                                            r[:r.shape[0]//2],
                                            '-',
                                            color='#ffffff',
                                            alpha=0.8,
                                            zorder=11,
                                            linewidth=0.6,
                                            )
        if seperatebars:
            if np.sum(this):
                magseperator[0].set_linestyle('-')
                magseperator[0].set_linewidth(0.5)
                magseperator[0].set_color('#000000')

            for t in [np.min(theta), np.max(theta)]:
                ax.plot([t, t],
                        [0, max(r)],
                        color='#000000',
                        linewidth=1,
                        linestyle='-',
                        zorder=11)
            ax.plot(theta[:theta.shape[0]//2],
                    r[:theta.shape[0]//2],
                    color='#000000',
                    linewidth=1,
                    linestyle='-',
                    zorder=11)

    if freqlim == 'auto':
        ymax = np.ceil(np.nanmax(freqsum)/5)*5

        if ymax <= 0 or ymax is np.nan:
            ymax = midoffset

        ax.set_ylim(-midoffset,
                    ymax+1.5*midoffset)
    else:
        ax.set_ylim(-midoffset,
                    freqlim)

    if legcol == 'auto':
        legcol = int(np.ceil(len(added2legend)/4))

    if makeleg:
        leg = ax.legend(title='Windspeed (ms$^{-1}$)',
                        bbox_to_anchor=legendlocation,
                        loc=legloc,
                        framealpha=0.8,
                        ncol=legcol,
                        fontsize=fontsize,
                        )
        # round the corners
        leg.get_frame().set_boxstyle(boxstyle='round')


        leg.set_zorder(12)
    ax.fill_between(np.deg2rad(dirloc),
                    np.repeat(-midoffset, dirloc.size),
                    y2=0,
                    color='#ffffff',
                    zorder=5,)

    if middletext is not None:
        fig.text(0.5,
                 0.5,
                 middletext,
                 fontsize=fontsize,
                 color='0',
                 va='bottom',
                 ha='center',
                 zorder=15,)


    ax.plot(np.deg2rad(dirloc),
            np.repeat(0, dirloc.size),
            color='k',
            lw=1.5,
            zorder=10,)

    freqsum = np.nansum(freq, axis=0)

    if labelposition == 'auto':
        helpfreq, helpspeedloc, helpdirloc = np.histogram2d(speeddata,
                                                            dirdata,
                                                            bins=[speedbins,
                                                                  np.arange(mindir, maxdir+45, 45)])
        helpsum = np.nansum(helpfreq, axis=0)
        ss = int(360 // 45)
        shape = (ss, helpsum.size//ss)

        goodpos = np.nansum(np.reshape(helpsum, shape), axis=1)
        # if we made a legend, it will interfere with the labels
        if makeleg:
            rellegpos = [i-0.5 for i in legendlocation]
            anglelegpos = np.rad2deg(np.arctan2(rellegpos[0], rellegpos[1]))
            rellegposix = int((anglelegpos % 360) / 45)
            # ensure all these positions are bad!
            goodpos[rellegposix] += max(goodpos)
            goodpos[(rellegposix+1) % len(goodpos)] += max(goodpos)
            goodpos[(rellegposix-1) % len(goodpos)] += max(goodpos)
        labelposition = np.argmin(goodpos) * (360/ss)



    label = ['Number of occurance (#)',
             'Frequency$_{sector}$ (%)']
    label = label[normalize*1]
    label += ' (N: '+str(len(speeddata))+')'

    if (ringofsums is not False and ringofsums is not None):

        if isinstance(ringofsums, bool):
            sumfreq = freqsum[np.newaxis, :]

            speedlocsum = ax.get_ylim()[-1]
            speedlocsum = [speedlocsum-0.5*midoffset,
                           speedlocsum+0.5*midoffset]
            vmin=0
            vmax = np.ceil(freqsum.max())
            ticks = np.linspace(vmin, vmax, 5)

        else:
            # since we sum it up the range doesn't actually matter

            ringofsums = ringofsums.to_frame()
            ringofsums['_dir_'] = np.floor(((dirdata+sectorsize)%maxdir)/sectorsize)

            this = ringofsums.groupby(by='_dir_').agg(ringofsumagg)

            sumfreq = freqsum[np.newaxis, :]
            sumfreq[:,this.index.astype(np.int)] = this.values.T

            speedlocsum = ax.get_ylim()[-1]
            speedlocsum = [speedlocsum-0.5*midoffset,
                           speedlocsum+0.5*midoffset]
            vmin = np.floor(sumfreq.min())
            vmax = np.ceil(sumfreq.max()/5)*5
#            ticks = np.linspace(vmin, vmax, 5)
            label = label.split(' (')
            if callable(ringofsumagg):
                fname = str(ringofsumagg).split(' ')[1]
            else:
                fname = ringofsumagg

            if fname.startswith('nan'):
                fname = fname[3:]

            label[0] = ringofsums.columns[0]+'$_{'+fname.capitalize()+'}$'
            label = ' ('.join(label)

        mesh = ax.pcolormesh(np.deg2rad(dirloc),
                             speedlocsum,
                             sumfreq,
                             cmap=cmap2,
                             edgecolor=edgecolor,
                             lw=1,
                             zorder=10,
                             vmin=vmin,
                             vmax=vmax,
                             )
        if ringlegend:
            cb = plt.colorbar(mesh,
                              orientation='horizontal',
                              cmap=cmap2,
                              fraction=0.03,
                              pad=0.1,
                              aspect=30,
    #                          ticks=ticks,
                              label=label
                              )

    ax.grid(zorder=1, lw=0.5, color='k')
    if addwatermark:
        watermark(fig=fig)

    yticks = ax.get_yticks()
    ylabels = yticks.copy()
    ylabels[0] = ''

    if xlabel is not None:
        ax.set_xlabel(xlabel)

    ax.set_yticklabels([' ' for _ in ylabels],
                       color='#000000',
                       zorder=15,
                       fontsize=fontsize,
                       horizontalalignment='center',
                       verticalalignment='center')

    for yt, yl in zip(yticks[1:-1:], ylabels[1:-1:]):

        if (yt % 1) == 0:
            yl = int(yl)
        else:
            continue

        ax.text(np.deg2rad(labelposition),
                yt, str(yl)+' %',
                ha='center',
                va='center',
                fontsize=fontsize,
                color=innerlabelcolor,
                zorder=20,
                rotation=(45-(labelposition)) % 180 - 45,
                bbox=dict(color='#ffffff', alpha=0.85, boxstyle='round', zorder=12),
                )

    offset_speedlabel = [-12, 12, ][1*(labelposition % 270 > 90)]

    labelrotation = {0: 90,
                     45: 45,
                     90: 0,
                     135: -45,
                     180: -90,
                     215: -45,
                     270: 0,
                     315: 45,
                     }
    if showlabel:
        ax.text(np.deg2rad(labelposition-offset_speedlabel),
                np.mean(yticks),
                'Frequency [%]',
                ha='center', va='center',
                rotation=labelrotation[labelposition],
                zorder=12,
                fontsize=fontsize,
                bbox=dict(boxstyle='round', fc="w", ec="k", alpha=0.75, zorder=12),
                )

    xticks = np.rad2deg(ax.get_xticks().copy())
    dirs = {0: 'N', 90: 'E', 180: 'S', 270: 'W'}

    xlabels = [str(int(_))+'°' if _ not in dirs else dirs[_] for _ in xticks]

    if azoffset != 0:
        ax.plot([azoffset*np.pi/180, azoffset*np.pi/180],
                 [0, ax.get_ylim()[-1]],
                 color='#000000', linestyle='-')

        xlabels.append('N$_{True}$\n'+'{:.1f}'.format(azoffset) + '°')

        if azoffset < 0:
            azoffset += 360

        xticks = np.append(xticks, azoffset)

    rots = [90 - (i % 180) if i % 90 != 0.0 else 0 for i in xticks]

    for labelno, label in enumerate(xlabels):
        if xticks[labelno] in dirs:
            if xticks[labelno] in ['N','S']:
                va = ['bottom', 'top'][xticks[labelno] == 'N']
            else:
                va = 'center'
            if xticks[labelno] in ['E','W']:
                ha = ['left', 'right'][xticks[labelno] == 'E']
            else:
                ha = 'center'

            if ringofsums:
                f = 2
            else:
                f = 1.2
        else:
            ha = ['right', 'left'][(xticks[labelno] < 180)*1]
            va = ['top', 'bottom'][((xticks[labelno] % 270) < 90) * 1]
            f = 0.5

        ax.text(np.deg2rad(xticks[labelno]),
                ax.get_ylim()[-1] + f * midoffset,
                label,
                ha=ha,
                va=va,
                fontsize=fontsize,
                color=outerlabelcolor,
                rotation=rots[labelno],
                bbox=dict(boxstyle='round', fc="w", ec="k",
                          alpha=0.75, zorder=12)
               )

    ax.set_xticklabels([' ' for i in ax.get_xticklabels()])

    if savefigas:
        fig.tight_layout()
        if savefigas.endswith(os.sep):
            figuredir = savefigas
            filename = 'windrose.png'

        else:
            figuredir = savefigas.split(os.sep)
            filename = figuredir[-1]
            figuredir = os.sep.join(figuredir[:-1])
            figuredir = os.sep + figuredir + os.sep

        if not os.path.exists(figuredir):
            os.makedirs(figuredir)

        fig.savefig(figuredir+filename)

    return fig, ax

if __name__ == '__main__':

    print('*'*10, 'HELP for windrose', '*'*10)
    print('Makes a windrose, i.e. a histogram of wind speed and direction',
          'by calculating frequency and using it as radius (cumulative)',
          'This follows the standard wind rose usage with the drawback',
          'that small classes might be hard to see\n',
          'Its also possible to set ringofsums to True which will'
          'show the total frequency of a sector\n',
          'For further keyword see method call')

#     from mcr.sql.util import getdata
#     import datetime
#     t1 = datetime.datetime.utcnow()
#     t0 = t1 - datetime.timedelta(days=20)
#     t0 = datetime.datetime(2017, 9, 11, 12, 0)
#     t1 = datetime.datetime(2017, 10, 2, 12, 0)
#     stat='GB'
#     codes = ['FN'+stat+'WDA1', 'FN'+stat+'WVA1', 'FN'+stat+'FGT3']

#     data, meta = getdata(codes, t1=t1, t0=t0, )
#     data[data['FNGBWDA1'] == 0] = np.nan
#     x = windrose(data[codes[0]],
#                  data[codes[1]],
#                  speedstep=1,
#                  sectorsize=5,
#                  ringofsums=data[codes[2]],
# #                 ringofsumagg=np.nanmin,
# #                 cmap2='terrain',
#                  )

