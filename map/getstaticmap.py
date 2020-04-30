#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# """
# Created on Wed Aug  8 17:55:11 2018
#
# @author: spirro00
# """


def getstaticmap(url=None,
                 checkexisting=True,
                 savemap=False,
                 filename='',
                 info=False):

    if url is None or info:
        print('*'*10, 'HELP for mapurl', '*'*10)
        print('This file return the static image map for the url generated',
              'from mapurl so it can be used as basemap')
        print('E.g.\n',
              'from mcr.map.mapurl import mapurl\n',
              'url = mapurl(lat=47.56169689110803,lon=7.58050247629464)\n',
              'img = getstaticmap(url)\n',
              'should deliver a google maps map from Basel')

        if url is None:
            return False

    import requests
    import io
    from matplotlib.image import imread

    pxpos = url.index('&size=')

    # get parameter in url
    px = url[pxpos+6:]
    # remove other parameters
    px = px[:px.index('&')]
    # contains widht x height
    px = [int(i) for i in px.split('x')]

    response = requests.get(url)
    response.raw.decode_content = True

    if savemap:
        if filename is None:
            filename = 'defaults.png'
        else:
            if not filename.lower().endswith('png'):
                print('Are you sure the webservice delivered not a PNG?')
                print('Writing file anyway but be warned that some viewer',
                      'may have trouble if the fileextension does ',
                      'not match imageheader')
        with open(filename, 'wb') as fo:
            fo.write(response.content)

    try:
        staticmap = imread(io.BytesIO(response.content))
        return staticmap
    except ValueError:
        print('Failure to read mapfile. Answer by server was:')
        return response


if __name__ == '__main__':
    print('*'*10, 'HELP for mapurl', '*'*10)
    print('This file return the static image map for the url generated',
          'from mapurl so it can be used as basemap')
    print('E.g.\n',
          'from mcr.map.mapurl import mapurl\n',
          'url = mapurl(lat=47.56169689110803,lon=7.58050247629464)\n',
          'img = getstaticmap(url)\n',
          'should deliver a google maps map from Basel')
