import re

__author__ = 'tangz'

from datetime import datetime as dt

DATEFORMAT = '%Y%m%d_%H%M'

def gettimestamp(datetime=None, frmt=DATEFORMAT):
    if datetime is None:
        datetime = dt.utcnow()
    return datetime.strftime(frmt)

def buildfilename(base=None, prependval=None, appendval=None, joiner='_'):
    parts = []
    if prependval is not None:
        parts.append(prependval)
    if base is not None:
        parts.append(base)
    if appendval is not None:
        parts.append(appendval)
    return None if not parts else joiner.join(parts)

def withdotsep(extstr):
    return extstr if extstr.startswith('.') else '.' + extstr

def withslash(folder):
    return folder if folder.endswith('/') or folder.endswith('\\') else folder + '/'


class URLSource(object):
    def __init__(self, url, timeextractor=None):
        self.url = url
        self.filebase = None
        self.timestamp = None
        self.ext = None
        self.extractall(timeextractor)

    def extractall(self, timeextractor):
        def checkparts(parts):
            if not parts:
                raise ValueError("Cannot parse file name from: " + self.url)
        urlparts = re.split('/', self.url)
        checkparts(urlparts)
        filename = urlparts[len(urlparts) - 1]
        filenameparts = re.split('\.', filename)
        checkparts(filenameparts)
        filepartslen = len(filenameparts)

        self.filebase = '.'.join(filenameparts[:filepartslen-1])
        self.ext = filenameparts[filepartslen-1]
        if timeextractor is not None:
            self.timestamp = timeextractor(self.url)
        else:
            self.timestamp = dt.utcnow()

    def __str__(self):
        return self.url


class FileTarget(object):
    def __init__(self, folder, file, ext, timestamp=None):
        self.folder = folder
        self.file = file
        self.ext = ext
        self.timestamp = timestamp

    def __str__(self):
        return withslash(self.folder) + self.file + withdotsep(self.ext)


class DirectoryTarget(object):
    def __init__(self, folder):
        self.folder = folder
        self._filebuilder = None

    def usetimestamp(self, base, ext):
        def timestampbuild():
            thetime = dt.utcnow()
            file = buildfilename(base=base, appendval=gettimestamp(datetime=thetime))
            return FileTarget(self.folder, file, ext, timestamp=thetime)
        self._filebuilder = timestampbuild

    def usecopy(self, src, prependval=None, appendval=None):
        def otherurlbuild():
            thetime = dt.utcnow() if src.timestamp is None else src.timestamp
            file = buildfilename(base=src.filebase, prependval=prependval, appendval=appendval)
            return FileTarget(self.folder, file=file, ext=src.ext, timestamp=thetime)
        self._filebuilder = otherurlbuild

    def getfiletarget(self):
        if self._filebuilder is not None:
            return self._filebuilder()
        else:
            return None










