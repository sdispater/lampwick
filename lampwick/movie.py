# -*- coding: utf-8 -*-

import os
import re
import subprocess
import errno
import dateutil.parser as date_parser

from . import PROBE


class Movie(object):

    def __init__(self, path):
        if not os.path.exists(path):
            raise OSError((errno.ENOENT, 'File %s does not exist' % path))

        command = [PROBE, path]

        output = subprocess.check_output(command, stderr=subprocess.STDOUT)

        self.size = os.path.getsize(path)
        self.container = re.search('Input #\d+,\s*(\S+),\s*from', output).group(1)

        m = re.search('Duration: (\d{2}):(\d{2}):(\d{2}\.\d{2})', output)
        if m:
            self.duration = int(m.group(1)) * 60 * 60 + int(m.group(2)) * 60 + float(m.group(3))

        m = re.search('start: (\d*\.\d*)', output)
        if m:
            self.time = float(m.group(1))
        else:
            self.time = 0.0

        m = re.search('creation_time +: +(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', output)
        if m:
            self.creation_time = date_parser.parse(m.group(1))
        else:
            self.creation_time = None

        m = re.search('bitrate: (\d*)', output)
        if m:
            self.bitrate = int(m.group(1))
        else:
            self.bitrate = None

        m = re.search('rotate\ {1,}:\ {1,}(\d*)', output)
        if m:
            self.rotation = int(m.group(1))
        else:
            self.rotation = None

        m = re.search('Video: (.*)', output)
        if m:
            self.video_stream = m.group(1)
        else:
            self.video_stream = None

        m = re.search('Audio: (.*)', output)
        if m:
            self.audio_stream = m.group(1)
        else:
            self.audio_stream = None

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
            else:
                self.video_bitrate = None

            # Trying to figure out the frame rate
            for info in video_stream_info[4:]:
                m = re.search('(\d*\.?\d*)\s?(fps|tbr)', info)
                if m:
                    self.frame_rate = float(m.group(1))
                    break
                else:
                    self.frame_rate = None

            self.resolution = resolution.split(' ')[0]

        if self.audio_stream:
            audio_stream_info = re.split('\s?,\s?', self.audio_stream)
            self.audio_codec = audio_stream_info[0]
            audio_sample_rate = audio_stream_info[1]
            self._audio_channels = audio_stream_info[2]
            audio_bitrate = audio_stream_info[4]

            m = re.match('\A(\d+) kb/s\Z', audio_bitrate)
            if m:
                self.audio_bitrate = int(m.group(1))
            else:
                self.audio_bitrate = None

            self.audio_sample_rate = int(re.match('(\d*)', audio_sample_rate).group(1))

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
