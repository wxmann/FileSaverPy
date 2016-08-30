from datetime import datetime as dt, timedelta
from enum import Enum
import re
from savers import periodic

__author__ = 'tangz'


class Sector(Enum):
    EASTERN_NORTH_AMERICA = "GOES-E CONUS"
    GOES_E_FULL_DISK = "GOES-E FULL"
    ATLANTIC_HURRICANE = "GOES-E HURRICANE"
    NORTHERN_HEMISPHERE = "GOES-E NHE"
    EASTERN_PACIFIC = "GOES-W PACUS"


class Zoom(Enum):
    HIGH = 1
    MEDIUM = 2
    LOW = 4


class Satellite(Enum):
    VISIBLE = 'vis'
    INFRARED = 'ir'
    WATER_VAPOR = 'wv'


class MapType(Enum):
    STANDARD = 'standard'
    COUNTY = 'county'
    LATLON = 'latlon'
    NONE = 'none'


def savesetting(sector, lat, long, sattype, zoom,
                maptype=MapType.STANDARD, past=0, palette='ir2.pal', mapcolor='black',
                quality=90, width=1000, height=800):
    colorbar = 0  # job fails if this is = 1
    queryparams = {}
    queryparams['satellite'] = sector.value
    queryparams['lat'] = lat
    queryparams['lon'] = long
    queryparams['map'] = maptype.value
    queryparams['zoom'] = zoom.value
    queryparams['info'] = sattype.value
    queryparams['past'] = past
    if sattype != Satellite.VISIBLE:
        queryparams['palette'] = palette
    queryparams['colorbar'] = colorbar
    queryparams['mapcolor'] = mapcolor
    queryparams['quality'] = quality
    queryparams['width'] = width
    queryparams['height'] = height
    # omitted query params: type=image, numframes={not used for image type}
    return queryparams


def savenasaghcc1(savesettings, saveloc, save_period, img_dt=None):
    thesaver = periodic.PeriodicSaver()
    for setting in savesettings:
        baseurl = 'http://weather.msfc.nasa.gov/cgi-bin/get-goes?'
        queryparamspart = '&'.join("{0}={1}".format(key, re.sub(r"\s+", "%20", str(setting[key]))) for key, val
                                   in setting.items())
        completeurl = baseurl + queryparamspart

        mutator = lambda x: setting['info'] + "_ghcc"
        thesaver.adddynamicjob(completeurl, saveloc, save_period, mutator, ghcc_timeextractor, img_dt)
    thesaver.executesaves()


def ghcc_timeextractor(url):
    regex = 'GOES(\d{2})(\d{2})(\d{4})(\d{1,3})'
    found = re.search(regex, url)
    if not found:
        raise url.InvalidResourceError("Cannot find date-time for file: {0}".format(url))

    found_hour = int(found.group(1))
    found_min = int(found.group(2))
    found_year = int(found.group(3))
    found_dayofyr = int(found.group(4))

    day_before_year = dt(year=found_year - 1, month=12, day=31)
    current_day = day_before_year + timedelta(days=found_dayofyr)

    return dt(year=found_year, month=current_day.month, day=current_day.day, hour=found_hour, minute=found_min)
