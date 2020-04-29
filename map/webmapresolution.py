#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# """
# Created on %(date)s
#
# @author: %(username)s
# """


def webmapresolution(zoom_or_url,
                     # the default scale when used with the getstaticurl
                     scale=2,
                     # mean earth radius in meters
                     earth_radius=6378137):
    import numpy as np

    if type(zoom_or_url) == str:
        zoom = zoom_or_url.split('zoom=')[1].split('&')[0]

        if 'scale' in zoom_or_url:
            scale = zoom_or_url.split('scale=')[1].split('&')[0]
        else:
            scale = '1'

        zoom, scale = float(zoom), float(scale)
    elif type(zoom_or_url) in [int, float]:
        zoom = zoom_or_url
        if scale == 2:
            print('Warning, if you passed the zoom directly, make sure the',
                  ' scale is correct (default is 2 due to usage of staticmap')
        pass
    else:
        print('Pass in either URL or the zoom and scale directly')
        return False

    resolution = (2*np.pi*earth_radius)/(256*2**(zoom)) / scale
    return resolution


if __name__ == '__main__':
    print('*'*10, 'HELP for webmapresolution', '*'*10)
    print('Calculates the resolution in meters of one pixel of a webmap')
    print('Requires knowledge of the zoomlevel',)
