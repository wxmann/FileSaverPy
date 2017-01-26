import unittest
from datetime import datetime
from unittest.mock import patch

from saverpy.converters import BaseConverter, BatchConverter, ConversionException


class ConvertersTests(unittest.TestCase):
    def setUp(self):
        patcher = patch('saverpy.converters._get_current_time')
        self.mock_time = patcher.start()
        self.dummy_utc_timestamp = datetime(2017, 1, 1)
        self.dummy_nonutc_timestamp = datetime(2017, 1, 2)
        self.dummy_another_timestamp = datetime(2017, 1, 3)
        self.mock_time.side_effect = lambda \
                use_utc: self.dummy_utc_timestamp if use_utc else self.dummy_nonutc_timestamp
        self.url = 'http://blah.com/not_a_real_img.jpg'
        self.timeextractor = lambda url: self.dummy_another_timestamp
        self.urls_extracted = ['http://blah.com/img-1.jpg', 'http://blah.com/img-2.jpg',
                               'http://blah.com/img-3.jpg']
        self.url_fanout_func = lambda url: self.urls_extracted

    def test_should_convert_single_source_with_current_utc_timestamp(self):
        converter = BaseConverter(use_utc=True)
        srcs = converter(self.url)
        self._assertCorrectSingleSource(srcs, self.dummy_utc_timestamp)

    def test_should_convert_single_source_with_current_nonutc_timestamp(self):
        converter = BaseConverter(use_utc=False)
        srcs = converter(self.url)
        self._assertCorrectSingleSource(srcs, self.dummy_nonutc_timestamp)

    def test_should_convert_single_source_with_timeextractor(self):
        converter = BaseConverter(timeextractor=self.timeextractor)
        srcs = converter(self.url)
        self._assertCorrectSingleSource(srcs, self.dummy_another_timestamp)

    def _assertCorrectSingleSource(self, srcs, expected_timestamp):
        self.assertEqual(len(srcs), 1)
        src = srcs[0]
        self.assertEqual(src.filename, 'not_a_real_img')
        self.assertEqual(src.ext, 'jpg')
        self.assertEqual(src.url, self.url)
        self.assertEqual(src.timestamp, expected_timestamp)

    def test_should_raise_exception_if_url_not_a_file(self):
        with self.assertRaises(ConversionException):
            BaseConverter()('http://blah.com/')

    def test_should_convert_multi_source_current_utc_timestamp(self):
        converter = BatchConverter(self.url_fanout_func, use_utc=True)
        srcs = converter(self.url)
        self._assertCorrectBatchSources(srcs, self.dummy_utc_timestamp)

    def test_should_convert_multi_source_with_timeextractor(self):
        converter = BatchConverter(self.url_fanout_func, timeextractor=self.timeextractor)
        srcs = converter(self.url)
        self._assertCorrectBatchSources(srcs, self.dummy_another_timestamp)

    def test_should_skip_nonfile_urls_extracted_for_batch_sources(self):
        new_urls = list(self.urls_extracted)
        new_urls += ['http://blah.com', 'this-is-not-even-a-url']
        new_url_fanout = lambda url: new_urls

        converter = BatchConverter(new_url_fanout, timeextractor=self.timeextractor)
        srcs = converter(self.url)
        self._assertCorrectBatchSources(srcs, self.dummy_another_timestamp)

    def _assertCorrectBatchSources(self, srcs, expected_timestamp):
        self.assertEqual(len(srcs), len(self.urls_extracted))
        for src in srcs:
            self.assertEqual(src.ext, 'jpg')
            self.assertEqual(src.timestamp, expected_timestamp)

        self.assertEqual(srcs[0].filename, 'img-1')
        self.assertEqual(srcs[1].filename, 'img-2')
        self.assertEqual(srcs[2].filename, 'img-3')

        urls = [src.url for src in srcs]
        self.assertEqual(urls, self.urls_extracted)