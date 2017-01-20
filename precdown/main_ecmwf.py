#! /usr/bin/env python
# coding=utf-8
# Author: Liangjun Zhu
# Date  : 2017-1-8
# Email : zlj@lreis.ac.cn
# Blog  : zhulj.net
from Utils import *
from Download import download_precipitation

if __name__ == '__main__':
    DOWN_PATH = currentPath()
    # download ECMWF data
    product = "ECMWF"
    subproduct = 'interim'
    startdate = [2002, 2, 1]  # year, month, day, [mm, ss]
    enddate = [2016, 10, 31]
    download_precipitation(product, subproduct = subproduct,
                           startdate = list2datetime(startdate),
                           enddate = list2datetime(enddate),
                           workspace = DOWN_PATH)