#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# """
# Created on %(date)s
#
# @author: %(username)s
# """


def baseround(x, base=5):
    return int(base * round(float(x)/base))


if __name__ == '__main__':
    print('*'*10, 'HELP for baseround', '*'*10)
    print('Round to a specified base, like 5 or 10 to make plots more useful')
