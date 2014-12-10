# -*- coding: utf-8 -*-

import math
import re
import subprocess
import select
import fcntl
import os
import pexpect
from .encoding_options import EncodingOptions
from . import BINARY


class Transcoder(object):

    timeout = 30

    def __init__(self, movie, output_file,
                 options=EncodingOptions(), transcoder_options=None):
        """
        :param movie: a Movie instance
        :type movie: Movie
        :param options: an EncodinOptions instance
        :type options: EncodingOptions
        """
        transcoder_options = transcoder_options or {}

        self.movie = movie
        self.output_file = output_file

        if isinstance(options, (basestring, EncodingOptions)):
            self.raw_options = options
        elif isinstance(options, dict):
            self.raw_options = EncodingOptions(options)
        else:
            raise Exception('Unknown options format %s, '
                            'should be either EncodingOptions, str or dict'
                            % type(options))

        self.transcoder_options = transcoder_options
        self.errors = []

        self.apply_transcoder_options()

    def run(self):
        for progress in self._transcode_movie():
            yield progress

    def apply_transcoder_options(self):
        self.transcoder_options['validate'] = self.transcoder_options.get('validate', True)

        if self.movie.aspect_ratio is None:
            return

        preserve_aspect_ratio = self.transcoder_options.get('preserver_aspect_ratio')
        if preserve_aspect_ratio == 'width':
            new_height = self.raw_options['width'] / self.movie.aspect_ratio
            if new_height % 2 == 0:
                new_height = math.ceil(new_height)
            else:
                new_height = math.floor(new_height)

            if new_height % 2 == 1:
                new_height += 1

            self.raw_options['resolution'] = '%sx%s' % (self.raw_options['width'], new_height)
        elif preserve_aspect_ratio == 'height':
            new_width = self.raw_options['height'] * self.movie.aspect_ratio
            if new_width % 2 == 0:
                new_width = math.ceil(new_width)
            else:
                new_width = math.floor(new_width)

            if new_width % 2 == 1:
                new_width += 1

            self.raw_options['resolution'] = '%sx%s' % (new_width, self.raw_options['height'])

    def _transcode_movie(self):
        command = [BINARY, '-y', '-i', self.movie.path] + self.raw_options.as_parameters() + [self.output_file]

        thread = pexpect.spawn(subprocess.list2cmdline(command))
        cpl = thread.compile_pattern_list([
            pexpect.EOF,
            "time=(\d+):(\d+):(\d+.\d+)"
        ])

        while True:
            i = thread.expect_list(cpl, timeout=5)
            if i == 0:
                yield 0.0
                break
            elif i == 1:
                m = thread.match

                time = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))

                progress = time / self.movie.duration

                yield progress

        thread.close()

