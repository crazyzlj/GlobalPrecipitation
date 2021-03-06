#! /usr/bin/env python
# coding=utf-8
# Author: Liangjun Zhu
# Date  : 2017-1-8
# Email : zlj@lreis.ac.cn
# Blog  : zhulj.net

from Utils import *
import urllib2
from sendmail import send_mail
from bs4 import BeautifulSoup


def chunk_report(mbytes_so_far, total_size):
    if total_size > 0:
        percent = float(mbytes_so_far) / total_size
        percent = round(percent * 100, 2)
        sys.stdout.write("Downloaded %.3f of %.3f Mb (%0.2f%%)\r" %
                         (mbytes_so_far, total_size, percent))
        if mbytes_so_far >= total_size:
            sys.stdout.write('\n')
    else:
        pass  # currently, do nothing


def chunk_read(response, chunk_size = 8192, savepath = None, report_hook = None):
    try:
        total_size = response.info().getheader('content-length').strip()
        total_size = float(total_size) / 1024. / 1024.
    except AttributeError:
        total_size = 0.
    bytes_so_far = 0

    while True:
        chunk = response.read(chunk_size)
        bytes_so_far += len(chunk) / 1024. / 1024.
        if not chunk:
            break
        if savepath is not None:
            savedata2file(chunk, savepath)
        if report_hook:
            report_hook(bytes_so_far, total_size)
    return bytes_so_far


def downNASAEarthdata(productname, **kwargs):
    from cookielib import CookieJar
    TRMM_DAILY = False
    TRMM_MONTH = False
    if StringMatch(productname, "TRMM_3B42_Daily"):
        TRMM_DAILY = True
    elif StringMatch(productname, "TRMM_3B43"):
        TRMM_MONTH = True
    usrname = ''
    pwd = ''
    startdate = datetime.datetime.today()
    enddate = datetime.datetime.today()
    outpath = ''
    # try to get the required key-values, or throw exception
    try:
        usrname = kwargs["usrname"]
        pwd = kwargs["pwd"]
        startdate = kwargs["startdate"]
        enddate = kwargs["enddate"]
        outpath = kwargs["workspace"]
    except KeyError:
        print ("downNASAEarthdata function must have the usrname, pwd, startdate, and enddate args.")
    # try to get optional key-values
    logfile = None
    if 'log' in kwargs.keys():
        logfile = kwargs['log']
        delfile(logfile)

    authorizeUrl = "https://urs.earthdata.nasa.gov"
    # Create a password manager to deal with the 401 response that is returned from authorizeUrl
    password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_manager.add_password(None, authorizeUrl, usrname, pwd)
    # Create a cookie jar for storing cookies. This is used to store and return
    # the session cookie given to use by the data server (otherwise it will just
    # keep sending us back to Earthdata Login to authenticate).  Ideally, we
    # should use a file based cookie jar to preserve cookies between runs. This
    # will make it much more efficient.
    cookie_jar = CookieJar()
    # Install all the handlers.
    opener = urllib2.build_opener(
        urllib2.HTTPBasicAuthHandler(password_manager),
        # urllib2.HTTPHandler(debuglevel=1),    # Uncomment these two lines to see
        # urllib2.HTTPSHandler(debuglevel=1),   # details of the requests/responses
        urllib2.HTTPCookieProcessor(cookie_jar))
    urllib2.install_opener(opener)

    downUrl = "http://disc2.gesdisc.eosdis.nasa.gov/"
    if TRMM_DAILY:
        downUrl += "data//TRMM_L3/TRMM_3B42_Daily.7/%s/%s/3B42_Daily.%s.7.nc4"
    elif TRMM_MONTH:
        downUrl += "opendap/TRMM_L3/TRMM_3B43.7/%s/%s/3B43.%s.7.HDF.nc"
    tmpdate = startdate
    while tmpdate <= enddate:
        if TRMM_DAILY:
            tmpUrl = downUrl % (tmpdate.strftime('%Y'), tmpdate.strftime('%m'),
                                tmpdate.strftime('%Y%m%d'))
            deltadays = 1
        elif TRMM_MONTH:
            # get the first day of current month
            tmpdate = tmpdate.replace(day = 1)
            tmpUrl = downUrl % (tmpdate.strftime('%Y'), str(doy(tmpdate)).zfill(3),
                                tmpdate.strftime('%Y%m%d'))
            deltadays = GetDayNumber(tmpdate.year, tmpdate.month)
        saveName = tmpUrl.split("/")[-1]
        tmpfile = outpath + os.sep + saveName

        print2log("  -- %s, saved as %s\n" % (tmpdate.strftime('%Y%m%d'), saveName),
                  logfile = logfile)
        if isfileexist(tmpfile):
            tmpdate += datetime.timedelta(days = deltadays)
            continue
        while True:
            # Create and submit the request.
            try:
                print2log(tmpUrl, logfile = logfile)
                request = urllib2.Request(tmpUrl)
                response = urllib2.urlopen(request)
                chunk_read(response, savepath = tmpfile, report_hook = chunk_report)
                break
            except urllib2.HTTPError or urllib2.URLError, e:
                # print e.code
                if e.code == 404 and TRMM_MONTH:
                    tmpUrl = tmpUrl.replace('7.HDF.nc', '7A.HDF.nc')
                    continue
                else:
                    break
        tmpdate += datetime.timedelta(days = deltadays)


def read_url(url):
    url = url.replace(" ", "%20")
    req = urllib2.Request(url)
    a = urllib2.urlopen(req).read()
    soup = BeautifulSoup(a, 'html.parser')
    x = (soup.find_all('a'))
    allurl = []
    for i in x:
        file_name = i.extract().get_text()
        url_new = url + file_name
        url_new = url_new.replace(" ", "%20")
        # if file_name[-1] == '/' and file_name[0] != '.':
        #     read_url(url_new)
        # print(url_new)
        allurl.append(url_new)
    return allurl


def downHTTPSannoymous(productname, **kwargs):
    try:
        url = kwargs["baseurl"]
        outpath = kwargs["workspace"]
        downurls = read_url(url)
        for singleurl in downurls:
            #  if the singleurl is directory, the create new folder
            if singleurl[-1] == '/' and singleurl[0] != '.':
                subdir = outpath + os.sep + os.path.split(str(singleurl)[:-1])[1]
                mkdir(subdir)
                downHTTPSannoymous(productname, baseurl = singleurl, workspace = subdir)
            elif os.path.splitext(singleurl)[1] != '':  # download file
                try:
                    tmpfile = outpath + os.sep + os.path.basename(str(singleurl))
                    print ("Downloading %s..." % os.path.basename(str(singleurl)))
                    if not os.path.isfile(tmpfile) or not os.path.exists(tmpfile):
                        request = urllib2.Request(singleurl)
                        response = urllib2.urlopen(request)
                        chunk_read(response, savepath = tmpfile)
                except urllib2.HTTPError or urllib2.URLError, e:
                    print e.code
    except KeyError:
        print ("downHTTPSannoymous function must have the baseUrl and workspace args.")


def downPERSIANNdata(productname, **kwargs):
    baseftp = 'persiann.eng.uci.edu'
    availableTimeStep = {'PERSIANN'    : ['daily', 'mthly', 'yearly', '3hrly', '6hrly', 'hrly'],
                         'PERSIANN-CCS': ['daily', 'mthly', 'yearly', '3hrly', '6hrly', 'hrly'],
                         'PERSIANN-CDR': ['daily', 'mthly', 'yearly']}
    remotedir = 'CHRSdata/'
    if 'subproduct' in kwargs.keys():
        if kwargs['subproduct'] is not None:
            subproduct = kwargs['subproduct']
            productname += subproduct
    remotedir += productname + '/'

    timestep = 'yearly'
    if 'timestep' in kwargs.keys():
        if kwargs['timestep'] in availableTimeStep.get(productname):
            timestep = kwargs['timestep']
    remotedir += timestep

    usrname = 'anonymous'
    pwd = ''
    outpath = ''
    # try to get the required key-values, or throw exception
    try:
        outpath = kwargs["workspace"]
    except KeyError:
        print ("downPERSIANNdata function must have the workspace args.")
    # try to get optional key-values
    if 'usrname' in kwargs.keys():
        usrname = kwargs["usrname"]
    if 'pwd' in kwargs.keys():
        pwd = kwargs["pwd"]
    logfile = None
    if 'log' in kwargs.keys():
        logfile = kwargs['log']
        delfile(logfile)

    import ftplib
    from download_ftp_tree import download_ftp_tree
    ftp = ftplib.FTP(baseftp, usrname, pwd)
    download_ftp_tree(ftp, remotedir, outpath)


def downCMAPdata(productname, **kwargs):
    baseftp = 'ftp.cpc.ncep.noaa.gov'
    remotedir = 'precip/'
    availabledir = ['monthly', 'pentad', 'pentad_rt']
    subproduct = 'monthly'
    if 'subproduct' in kwargs.keys():
        if kwargs['subproduct'] is not None:
            subproduct = kwargs['subproduct']
    productname = productname.lower()
    productname += '/' + subproduct
    remotedir += productname + '/'

    usrname = 'anonymous'
    pwd = ''
    outpath = ''
    # try to get the required key-values, or throw exception
    try:
        outpath = kwargs["workspace"]
    except KeyError:
        print ("downCMAPdata function must have the workspace args.")
    # try to get optional key-values
    if 'usrname' in kwargs.keys():
        usrname = kwargs["usrname"]
    if 'pwd' in kwargs.keys():
        pwd = kwargs["pwd"]
    logfile = None
    if 'log' in kwargs.keys():
        logfile = kwargs['log']
        delfile(logfile)

    import ftplib
    from download_ftp_tree import download_ftp_tree
    ftp = ftplib.FTP(baseftp, usrname, pwd)
    download_ftp_tree(ftp, remotedir, outpath)


def downECMWFdata(productname, **kwargs):
    '''
    Only available in UNIX-platform, tested on CentOS.
    :param productname:
    :param kwargs:
    :return:
    '''
    from ecmwfapi import ECMWFDataServer
    server = ECMWFDataServer()
    # try to get the required key-values, or throw exception
    startdate = datetime.datetime.today()
    enddate = datetime.datetime.today()
    try:
        startdate = kwargs["startdate"]
        enddate = kwargs["enddate"]
        outpath = kwargs["workspace"]
    except KeyError:
        print ("downECMWFdata function must have the statdate, enddate, and workspace args.")
    savepath = outpath + os.sep + "ei-interim-sfc-oper-fc-%s.nc"
    tmpdate = startdate.replace(day = 1)
    enddate = enddate.replace(day = 1)
    while tmpdate <= enddate:
        deltadays = GetDayNumber(tmpdate.year, tmpdate.month) - 1
        tmpenddate = tmpdate + datetime.timedelta(days = deltadays)
        datestring = tmpdate.strftime("%Y%m%d") + '/to/' + tmpenddate.strftime("%Y%m%d")
        print (datestring)
        tmpsavepath = savepath % (datestring.replace('/to/', '-'))
        if os.path.exists(tmpsavepath):
            tmpdate = tmpenddate + datetime.timedelta(days = 1)
            continue
        server.retrieve({
            "class"  : "ei",
            "dataset": "interim",
            "date"   : datestring,
            "expver" : "1",
            "grid"   : "0.75/0.75",
            "levtype": "sfc",
            "param"  : "50.128/142.128/143.128/167.128/228.128/239.128",
            "step"   : "3/6/9/12",
            "stream" : "oper",
            "time"   : "00:00:00/12:00:00",
            "type"   : "fc",
            "format" : "netcdf",
            "target" : tmpsavepath,
        })
        send_mail('zlj', 'zlj', "ECMWF Download report", "%s have been done!" % datestring)
        tmpdate = tmpenddate + datetime.timedelta(days = 1)


def downCHdata(**kwargs):
    try:
        outpath = kwargs['workspace']
        baseurl = 'http://rcg.gvc.gu.se/data/ChinaPrecip/plot/%d/P%d-%d-%d.jpg'
        yperiod = [1951, 2005]
        dlt = datetime.timedelta(days = 1)

        def downsingleurl(down_url, stored_path):
            try:
                tmprequest = urllib2.Request(down_url)
                tmpresponse = urllib2.urlopen(tmprequest)
                chunk_read(tmpresponse, savepath = stored_path)
                return True
            except urllib2.HTTPError or urllib2.URLError or "Exception", err:
                print (err.code)
                time.sleep(20)
                return downsingleurl(down_url, stored_path)

        for year in range(yperiod[0], yperiod[1] + 1, 1):
            subdir = outpath + os.sep + str(year)
            mkdir(subdir)
            startday = datetime.datetime(year, 1, 1)
            days = 365
            if IsLeapYear(year):
                days = 366
            for i in range(days):
                newday = startday + dlt * i
                filename = 'P%d-%d-%d.jpg' % (newday.year, newday.month, newday.day)
                storedpath = subdir + os.sep + filename
                downurl = baseurl % (newday.year, newday.year, newday.month, newday.day)
                print ("Downloading %s..." % filename)
                if not os.path.isfile(storedpath) or not os.path.exists(storedpath):
                    downsingleurl(downurl, storedpath)
    except KeyError:
        print ("downCHdata function must have the workspace args.")


def download_precipitation(productname, **kwargs):
    print2log('******** Download %s data ********' % productname)
    if StringMatch(productname, "TRMM_3B42_Daily") or \
            StringMatch(productname, "TRMM_3B43"):
        downNASAEarthdata(productname, **kwargs)
    elif StringMatch(productname, "PERSIANN"):
        downPERSIANNdata(productname, **kwargs)
    elif StringMatch(productname, "CMAP"):
        downCMAPdata(productname, **kwargs)
    elif StringMatch(productname, "ECMWF"):
        downECMWFdata(productname, **kwargs)
    elif StringMatch(productname, "GPCP_daily"):
        downHTTPSannoymous(productname, **kwargs)
    elif StringMatch(productname, "CH0.5"):
        downCHdata(**kwargs)


if __name__ == '__main__':
    # CUR_PATH = currentPath()
    # CUR_PATH = r'C:\Users\ZhuLJ\Desktop\TRMM_download'
    # DOWN_PATH = CUR_PATH + os.sep + 'download'
    # mkdir(DOWN_PATH)
    # DOWN_PATH = currentPath()
    DOWN_PATH = r"D:\tmp\CH0.5\interpolated_prec_jpg"

    # # TRMM_3B42_Daily.7
    # product = "TRMM_3B42_Daily"
    # usrname = 'zhuliangjun'
    # pwd = 'Liangjun0130'
    # startdate = [2010, 1, 22]  # year, month, day, [mm, ss]
    # enddate = [2010, 1, 23]
    # log = DOWN_PATH + os.sep + product + '.log'
    # # TRMM_3B43.7
    # product = "TRMM_3B43"
    # download_precipitation(product, usrname = usrname, pwd = pwd,
    #                        startdate = list2datetime(startdate),
    #                        enddate = list2datetime(enddate),
    #                        workspace = DOWN_PATH, log = log)

    # # download from ftp-server, such as PERSIANN
    # product = "PERSIANN"
    # subproduct = None  # can be None, '-CSS', or '-CDR', None is the default
    # timestep = 'daily'  # can be 'daily', 'mthly', 'yearly'. '3hrly', '6hrly', and 'hrly' for PERSIANN and PERSIANN-CSS
    # log = DOWN_PATH + os.sep + product + '.log'
    # download_precipitation(product, subproduct = subproduct,
    #                        timestep = timestep,
    #                        workspace = DOWN_PATH, log = log)

    # # download CMAP data
    # product = "CMAP"
    # subproduct = 'monthly'  # can be 'monthly', 'pentad', 'pentad_rt'
    # log = DOWN_PATH + os.sep + product + '.log'
    # download_precipitation(product, subproduct = subproduct, workspace = DOWN_PATH, log = log)

    # # download ECMWF data
    # product = "ECMWF"
    # subproduct = 'interim'
    # startdate = [2002, 1, 1]  # year, month, day, [mm, ss]
    # enddate = [2016, 10, 31]
    # download_precipitation(product, subproduct = subproduct,
    #                        startdate = list2datetime(startdate),
    #                        enddate = list2datetime(enddate),
    #                        workspace = DOWN_PATH)

    # # download GPCP_daily data
    # product = "GPCP_daily"
    # url = "https://www1.ncdc.noaa.gov/pub/data/gpcp/daily-v1.2/"
    # download_precipitation(product, baseurl = url, workspace = DOWN_PATH)

    # down CH0.5 interpolated data (.jpg format)
    product = "CH0.5"
    download_precipitation(product, workspace = DOWN_PATH)
