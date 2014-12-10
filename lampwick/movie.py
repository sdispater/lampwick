# -*- coding: utf-8 -*-

import os
import re
import subprocess
import errno
import dateutil.parser as date_parser

from . import BINARY
from .encoding_options import EncodingOptions
from .transcoder import Transcoder


class Movie(object):

    def __init__(self, path):
        if not os.path.exists(path):
            raise OSError((errno.ENOENT, 'File %s does not exist' % path))

        output = self._execute_command(path)

        self.path = os.path.realpath(path)
        self.name = os.path.basename(path)
        self.size = os.path.getsize(path)
        self.container = re.search('Input #\d+,\s*(\S+),\s*from', output).group(1)
        self.time = 0.0
        self.creation_time = None
        self.bitrate = None
        self.rotation = None
        self.frame_rate = None
        self.video_stream = None
        self.audio_stream = None
        self.colorspace = None
        self.video_bitrate = None
        self.video_codec = None
        self.sar = None
        self.dar = None
        self.audio_bitrate = None
        self._audio_channels = None
        self.audio_codec = None
        self.audio_sample_rate = None
        self.invalid = False

        m = re.search('Duration: (\d{2}):(\d{2}):(\d{2}\.\d{2})', output)
        if m:
            self.duration = int(m.group(1)) * 60 * 60 + int(m.group(2)) * 60 + float(m.group(3))

        m = re.search('start: (\d*\.\d*)', output)
        if m:
            self.time = float(m.group(1))

        m = re.search('creation_time +: +(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', output)
        if m:
            self.creation_time = date_parser.parse(m.group(1))

        m = re.search('bitrate: (\d*)', output)
        if m:
            self.bitrate = int(m.group(1))

        m = re.search('rotate {1,}: {1,}(\d*)', output)
        if m:
            self.rotation = int(m.group(1))

        matches = re.findall('Video: (.*)', output)
        if matches:
            if len(matches) == 1:
                self.video_stream = matches[0]
            else:
                # Multiple video streams found, figuring out the right one
                for m in matches:
                    video_codec = re.match('((?:\([^()]*\)|[^,])+)', m).group(1)
                    # The first video stream in some mp4 files
                    # (like iTunes one) have a png file as
                    # first video stream, so we ignore it
                    if video_codec == 'png':
                        continue

                    self.video_stream = m
                    break

        m = re.search('Audio: (.*)', output)
        if m:
            self.audio_stream = m.group(1)

        if self.video_stream:
            # regexp to handle "yuv420p(tv, bt709)" colorspace etc from http://goo.gl/6oi645
            commas_except_in_parenthesis = '(?:\([^()]*\)|[^,])+'
            video_stream_info = re.findall(commas_except_in_parenthesis, self.video_stream)
            self.video_codec = video_stream_info[0].strip()
            self.colorspace = video_stream_info[1].strip()
            resolution = video_stream_info[2].strip()
            video_bitrate = video_stream_info[3].strip()

            m = re.match('\A(\d+) kb/s\Z', video_bitrate)
            if m:
                self.video_bitrate = int(m.group(1))

            # Trying to figure out the frame rate
            for info in video_stream_info[4:]:
                m = re.search('(\d*\.?\d*)\s?(fps|tbr)', info)
                if m:
                    self.frame_rate = float(m.group(1))
                    break

            self.resolution = resolution.split(' ')[0]

            m = re.match('SAR (\d+:\d+)', self.video_stream)
            if m:
                self.sar = m.group(1)

            m = re.match('DAR (\d+:\d+)', self.video_stream)
            if m:
                self.sar = m.group(1)

        if self.audio_stream:
            audio_stream_info = re.split('\s?,\s?', self.audio_stream)
            self.audio_codec = audio_stream_info[0]
            audio_sample_rate = audio_stream_info[1]
            self._audio_channels = audio_stream_info[2]
            audio_bitrate = audio_stream_info[4]

            m = re.match('\A(\d+) kb/s\Z', audio_bitrate)
            if m:
                self.audio_bitrate = int(m.group(1))

            self.audio_sample_rate = int(re.match('(\d*)', audio_sample_rate).group(1))

        if self.video_stream is None and self.audio_stream is None\
                or 'is not supported' in output\
                or 'could not find codec parameters' in output:
            self.invalid = True

    def transcode(self, output_file, options=EncodingOptions(), transcoder_options=None):
        transcoder = Transcoder(self, output_file, options, transcoder_options)

        for progress in transcoder.run():
            yield progress

    @property
    def audio_channels(self):
        if not self._audio_channels:
            return None
        elif 'channels' in self._audio_channels:
            return int(re.match('(\d*)', self._audio_channels).group(1))
        elif 'mono' in self._audio_channels:
            return 1
        elif 'stereo' in self._audio_channels:
            return 2
        elif '5.1' in self._audio_channels:
            return 6

    @property
    def width(self):
        try:
            return int(self.resolution.split('x')[0])
        except (NameError, IndexError):
            return

    @property
    def height(self):
        try:
            return int(self.resolution.split('x')[1])
        except (NameError, IndexError):
            return

    @property
    def aspect_ratio(self):
        return self._aspect_from_dar() or self._aspect_from_dimensions()

    @property
    def pixel_aspect_ratio(self):
        return self._aspect_from_sar() or 1

    def is_valid(self):
        return not self.invalid

    def _aspect_from_dar(self):
        if not self.dar:
            return

        w, h = self.dar.split(':')
        aspect = float(w) / float(h)

        if not aspect:
            return

        return aspect

    def _aspect_from_sar(self):
        if not self.sar:
            return

        w, h = self.sar.split(':')
        aspect = float(w) / float(h)

        if not aspect:
            return

        return aspect

    def _aspect_from_dimensions(self):
        aspect = float(self.width) / float(self.height)

        if not aspect:
            return

        return aspect

    def _execute_command(self, path):
        command = [BINARY, '-i', path]

        try:
            subprocess.check_output(command, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            return e.output
