# 全球尺度降水产品数据下载及入库
---------------------

## 1. 数据源列表

|数据名称及下载链接|源数据时段|时间分辨率|
|:--:|:--:|:--:|
|[TRMM_3B42_Daily.7](https://mirador.gsfc.nasa.gov/cgi-bin/mirador/presentNavigation.pl?tree=project&dataset=TRMM_3B42_Daily.7&project=TRMM&dataGroup=Gridded&version=7&CGISESSID=72fb61c358ddb99e5586f46a8e343934 "Daily TRMM and Others Rainfall Estimate (3B42 V7 derived)")|1998.1-|daily|
|[TRMM_3B43.7](https://mirador.gsfc.nasa.gov/cgi-bin/mirador/presentNavigation.pl?tree=project&dataset=3B43:%20Monthly%200.25%20x%200.25%20degree%20merged%20TRMM%20and%20other%20sources%20estimates&project=TRMM&dataGroup=Gridded&version=7&CGISESSID=72fb61c358ddb99e5586f46a8e343934 "3B43: Monthly 0.25 x 0.25 degree merged TRMM and other sources estimates ")|1998.1-|monthly|
|[PERSIANN](http://chrsdata.eng.uci.edu/ "PERSIANN")|1983-Present|1, 3, 6 hourly, daily, monthly|
|[CMAP](https://www.esrl.noaa.gov/psd/data/gridded/data.cmap.html "CMAP")[^ref1]|1979-2016.11|monthly|
|[ERA-interim](http://apps.ecmwf.int/datasets/data/interim-full-daily/levtype=sfc/ "ERA-interim")|1979.1-2016.10|sub-daily, daily, monthly|
|[GHCN-D](https://www.ncdc.noaa.gov/oa/climate/ghcn-daily/ "GHCN-D")|1880-2016.3|daily|
|GLOBAL P and T (**NOT FOUND**)|1900-2014.12|monthly|
|[GPCP](https://www1.ncdc.noaa.gov/pub/data/gpcp/daily-v1.2/)|1996-2015.10|daily|
|[PREC-L](https://www.esrl.noaa.gov/psd/data/gridded/data.precl.html)|1948-2016.12|monthly|
|[CH0.5](http://rcg.gvc.gu.se/)|1951-2010|daily|

[^ref1]: ftp://ftp.cpc.ncep.noaa.gov/precip/cmap 
## 2. 工作流分解

### 2.1 分别下载不同类型的降水数据

### 2.2 数据提取及入库
针对不同格式的数据进行数据提取，并存入SQL数据库（以小巧的SQLite为例）。

[NetCDF4Excel](https://github.com/NetCDF4Excel/project)

### 2.3 数据读取
设计几种通用的数据读取格式。

## 3. 应用案例

数据读取范围：

空间范围： 30 ~ 43 N; 94 ~ 116 E

时间范围： 2002.1.1~2015.12.31

读取格式： CSV文件，按时间序列和网格点序列排列


