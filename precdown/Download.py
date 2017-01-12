#! /usr/bin/env python
# coding=utf-8
# Author: Liangjun Zhu
# Date  : 2017-1-8
# Email : zlj@lreis.ac.cn
# Blog  : zhulj.net

from Utils import *
import urllib2


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


def download_precipitation(productname, **kwargs):
    print2log('******** Download %s data ********' % productname)
    if StringMatch(productname, "TRMM_3B42_Daily") or \
            StringMatch(productname, "TRMM_3B43"):
        downNASAEarthdata(productname, **kwargs)


if __name__ == '__main__':
    CUR_PATH = currentPath()
    CUR_PATH = r'C:\Users\ZhuLJ\Desktop\TRMM_download'
    DOWN_PATH = CUR_PATH + os.sep + 'download'
    mkdir(DOWN_PATH)
    # DOWN_PATH = currentPath()

    # TRMM_3B42_Daily.7
    product = "TRMM_3B42_Daily"
    usrname = 'zhuliangjun'
    pwd = 'Liangjun0130'
    startdate = [2010, 1, 22]  # year, month, day, [mm, ss]
    enddate = [2010, 1, 23]
    log = DOWN_PATH + os.sep + product + '.log'
    # TRMM_3B43.7
    product = "TRMM_3B43"

    download_precipitation(product, usrname = usrname, pwd = pwd,
                           startdate = list2datetime(startdate),
                           enddate = list2datetime(enddate),
                           workspace = DOWN_PATH, log = log)
