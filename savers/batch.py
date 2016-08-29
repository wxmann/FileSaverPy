from core import files
from core import web, timing
from savers import common

__author__ = 'tangz'


class BatchSaver(object):
    def __init__(self, exts=None, filter=None, timeconfig=None, timeextractor=None):
        self.hist = []
        self.exts = exts if not exts else [ext.replace('.', '') for ext in exts]
        self.filter = filter
        self.timeconfig = timeconfig
        self.timeextractor = timeextractor

    def _timeaware(self):
        return self.timeextractor is not None and self.timeconfig is not None

    def _passes_outsidefilter(self, urlsrc):
        return True if not self.filter else self.filter(urlsrc.filebase)

    def _passes_extfilter(self, urlsrc):
        return urlsrc.ext and self.exts and urlsrc.ext in self.exts

    def _saveone(self, url, dirtarg, mutator):
        src = files.URLSource(url, timeextractor=self.timeextractor)
        if self._passes_outsidefilter(src) and self._passes_extfilter(src) and timing.passestime(src, self.timeconfig, self.hist):
            targloc = dirtarg.copy_filename_from(src, mutator)
            common.dosave(url, str(targloc))
            self.hist.append(targloc)
            return True
        else:
            return False

    def saveall(self, onlinedir, saveloc, mutator=None):
        allhtml = web.gethtmlforpage(onlinedir)
        parser = web.LinksHTMLParser()
        parser.feed(allhtml)
        alllinks = parser.foundlinks
        urls = [files.get_file_url(onlinedir, link) for link in alllinks if files.isfile(link)]

        dirtarg = files.DirectoryTarget(saveloc)
        for url in urls:
            self._saveone(url, dirtarg, mutator=mutator)