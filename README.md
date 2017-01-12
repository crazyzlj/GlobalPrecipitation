# 全球尺度降水产品数据下载及入库
---------------------

## 1. 数据源列表

|数据名称及下载链接|源数据时段|时间分辨率|
|:--:|:--:|:--:|
|[TRMM_3B42_Daily.7](https://mirador.gsfc.nasa.gov/cgi-bin/mirador/presentNavigation.pl?tree=project&dataset=TRMM_3B42_Daily.7&project=TRMM&dataGroup=Gridded&version=7&CGISESSID=72fb61c358ddb99e5586f46a8e343934 "Daily TRMM and Others Rainfall Estimate (3B42 V7 derived)")|1998.1-|daily|
|[TRMM_3B43.7](https://mirador.gsfc.nasa.gov/cgi-bin/mirador/presentNavigation.pl?tree=project&dataset=3B43:%20Monthly%200.25%20x%200.25%20degree%20merged%20TRMM%20and%20other%20sources%20estimates&project=TRMM&dataGroup=Gridded&version=7&CGISESSID=72fb61c358ddb99e5586f46a8e343934 "3B43: Monthly 0.25 x 0.25 degree merged TRMM and other sources estimates ")|1998.1-|monthly|
|PERSIANN|1983-2016.10|3 hours|
|CMAP|1979-2016.11|daily|
|ERA-interim|1979-2016.11|daily|
|CHCN-D|1880-2016.3|daily|
|GLOBAL P and T|1900-2014.12|monthly|
|GPCP|1996-2015.11|daily|
|PREC-L|1948-2016.12|monthly|
|CH0.5|1951-2016.12|daily|

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


