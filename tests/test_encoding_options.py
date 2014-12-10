# -*- coding: utf-8 -*-

from unittest import TestCase
from lampwick.encoding_options import EncodingOptions


class TestMovie(TestCase):

    def test_init(self):
        base_options = {
            'video_codec': 'h264'
        }
        options = EncodingOptions(base_options)

        print(options)
        print(options.as_parameters())
