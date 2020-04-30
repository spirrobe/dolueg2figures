#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# """
# Created on Wed Jul  4 12:33:55 2018
#
# @author: spirro00
# """


def watermark(fig=None,
              righttext='\u00A9 MCR Lab University of Basel',
              lefttext='creationtime',
              rpos=0.99,
              lpos=0.01,
              ypos=0.01,
              fontsize=8,
              middle=False,
              frame=True,
              ):

    import matplotlib.pyplot as plt
    import datetime

    if fig is None:
        thefig = plt.gcf()
    else:
        thefig = fig

    if lefttext == 'creationtime':
        now = datetime.datetime.utcnow().isoformat().split('.')[0].split('T')
        leftcorner = 'Created on ' + ' '.join(now) + ' UTC'

    if frame:
        bbox = dict(boxstyle='round,pad=0.6', fc="w", ec="w",)
    else:
        bbox = None

    if middle:
        thefig.text((rpos+lpos)/2, ypos,
                    '\n'.join([leftcorner, righttext]),
                    ha='center',
                    va='bottom',
                    fontsize=fontsize,
                    bbox=bbox,
                    )

    else:
        thefig.text(lpos, ypos,
                    leftcorner,
                    fontsize=fontsize,
                    va='top',
                    ha='left',
                    bbox=bbox,
                    )

        thefig.text(rpos, ypos,
                    righttext,
                    ha='right',
                    va='top',
                    fontsize=fontsize,
                    bbox=bbox,
                    )
