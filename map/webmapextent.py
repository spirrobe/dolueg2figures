#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# """
# Created on %(date)s
#
# @author: spirro00
# """


def webmapextent(url,
                 re=6378137):

    import numpy as np
    from map.webmapresolution import webmapresolution

    # what the middle point of the map
    clat, clon = url.split('center=')[-1].split('&')[0].split(',')
    clat, clon = float(clat), float(clon)

    # do we have some higher resolution map or not?
    # it doesnt affect the calculations below though, here for safekeeping
    if 'scale' in url:
        scale = float(url.split('scale=')[-1].split('&')[0])
    else:
        scale = 1.0

    # this many pixel are available
    px = url.split('size=')[-1].split('&')[0].split('x')
    px = [float(i)*scale for i in px]

    # zoom = float(url.split('zoom=')[-1].split('&')[0])
    # F = (256 / (2 * np.pi)) * 2 ** zoom

    adeg = 2 * np.pi * re / 360

    # the next two functions take the lat/lon in degrees directly
    def lon2x(lon):
        return adeg * lon

    def lat2y(lat):
        return np.rad2deg(np.log(np.tan(np.deg2rad(90 + lat)/2))) * adeg

    def x2lon(x):
        return x * 1 / adeg

    def y2lat(y):
        return np.arctan(np.exp(y * np.pi/180/adeg)) * 360 / np.pi - 90

    xycenter = [lon2x(clon), lat2y(clat)]
    resolution = webmapresolution(url)

    xy_leftbottom = [xycenter[0]-px[0]/2*resolution,
                     xycenter[1]-px[1]/2*resolution]
    xy_righttop = [xycenter[0]+px[0]/2*resolution,
                   xycenter[1]+px[1]/2*resolution]

    lonlat_leftbottom = x2lon(xy_leftbottom[0]), y2lat(xy_leftbottom[1])
    lonlat_righttop = x2lon(xy_righttop[0]), y2lat(xy_righttop[1])

    extent = [lonlat_leftbottom[0], lonlat_righttop[0],
              lonlat_leftbottom[1], lonlat_righttop[1],
              ]

    return extent


if __name__ == '__main__':
    print('*'*10, 'HELP for webmapextent', '*'*10)
    print('Calculates the extent in degrees (WGS84) of a webmap')
    print('Requires the url used to get the webmap',)

