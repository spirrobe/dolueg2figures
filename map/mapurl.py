#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# """
# Created on Wed Aug  8 17:12:23 2018
#
# @author: spirro00
# """

# creates the url to use with getmap


def mapurl(lat=None,
           lon=None,
           zoom=None,
           info=False,
           maptype={'google': 1, 'osm': 0},
           mapprovider='osm',
           googleapikey=None,
           googlescale=1,
           # mean earth radius in meters
           earth_radius=6378137,
           ):

    if isinstance(lat, float) or isinstance(lat, int):
        lat = [lat]

    if isinstance(lon, float) or isinstance(lon, int):
        lon = [lon]

    mapmaxpixels = {'google': 640, 'osm': 1024}


    if mapprovider == 'google' and googleapikey is None:
        print('Function mapurl: Google requires a valid API key for static map usage see here:',
              'https://developers.google.com/maps/documentation/maps-static/get-api-key',
              '\n Defaulting to openstreetmap for now')
        mapprovider = 'osm'

    if type(maptype) != dict:
        maptype = maptype
    else:
        maptype = maptype[mapprovider]



    maptypes = {'google': ['roadmap',
                           'satellite',
                           'terrain',
                           'hybrid'],
                'osm': ['mapnik',
                        'topo',
                        'osmarenderer',
                        'osma',
                        'cycle',
                        'piste'],
                }

    if info or lat is None or lon is None:
        print('This function creates a url to use with',
              'the function getstaticmap()')
        print('For this to work the url has to be setup,',
              'and for this a mapprovider has to be chosen')
        print('There may be others available, but here you can choose',
              'between google maps and open street map')
        print('As such there are several types available for each:')
        print('#'*20)

        for i in maptypes.keys():
            print('#'*10, i, '#'*10)
            print(maptypes[i])

        print('#'*20)
        print('You can choose the mapprovider by either supplying the name')
        print('You have to input longitude and latitude, both are needed!')
        print('If not set, the function will return False')
        if lon is None or lat is None:
            return False

    import numpy as np

    if isinstance(lat,list):
        lat = np.asarray(lat)

    if isinstance(lon,list):
        lon = np.asarray(lon)

    extent = np.asarray([lat.max(), lon.max(), lat.min(), lon.min()])

    maxextent = max([extent[0]-extent[2], extent[1]-extent[3]])
    maxextent = maxextent / 360 * (np.pi * earth_radius * 2)

    if maxextent == 0:
        maxextent = 500.
        extent[2:] -= maxextent/2
        extent[:2] += maxextent/2

    #  map = map_proj_init(105, semiMAJOR_AXIS=6378137.0, SEMIMINOR_AXIS=
#    6356752.31414 , CENTER_LONGITUDE=mean(LONGITUDE,/nan), $
    #                      limit=[extent[0,0],extent[1,0],extent[1,0],
#    extent[1,1]])

    # to find the zoomlevel we look at the max extent in meter
    # so we have slightly (10%) more border, ceil later on zoom helps too
    # this maxextent is to be diviced by the amount of pixels we can get
    # this is the scale we are looking for,
    # i.e. scale=(2D*!PI*earth_radius)/(256*2D^zoom)
    # thus, (2D*!PI*earth_radius)  / maxextent = (256*2D^zoom)
    # and further alog( (2D*!PI*earth_radius)/maxextent/256D ))=alog(2D)*zoom

    px = mapmaxpixels[mapprovider]
    earth_radius = 6378137

    # 15 is a good max zoom, more does not show more
    if zoom is None:
        zoom = np.log((2* np.pi * earth_radius) / (maxextent / px) / 256 )
        zoom = np.floor(zoom / np.log(2))

    # keep zoom within sensible bounds
    if zoom > 16:
        zoom = 16
    elif zoom <= 0:
        zoom = 1

    zoom = int(zoom)

    clat, clon = np.mean(lat), np.mean(lon)

    if mapprovider == 'google':
        url = "https://maps.googleapis.com/maps/api/staticmap?center="
        url += str(clat)+","+str(clon)
        url += "&zoom=" + str(zoom-1) + "&scale="+str(int(googlescale))+"&size="
        url += str(px) + "x" + str(px)
        url += '&maptype='+maptypes[mapprovider][maptype]+'&format=PNG32'
        url += '&key=' + googleapikey
    else:
        url = 'https://staticmap.openstreetmap.de/staticmap.php?'
        url += 'center=' + str(clat) + ',' + str(clon)
        url += '&zoom=' + str(zoom-1)
        url += '&size='+str(px)+'x'+str(px)
        url += '&layers=CN&maptype='+maptypes[mapprovider][maptype]

    return url

if __name__ == '__main__':
    print('*'*10, 'HELP for mapurl', '*'*10)
    print('This file contains an url generator for a static background map')
    print('it can either be chosen from google or osm',)
    print('and different maptypes can be choosen according to provider',)
    print('set info=True to see which are available for a chosen provider',)
    res = mapurl(info=True)
    print('A basel map would be something like this',
          'url = mapurl(lat=47.56169689110803,lon=7.58050247629464)')

