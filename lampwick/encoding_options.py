# -*- coding: utf-8 -*-

import re


class EncodingOptions(object):

    def __init__(self, options=None):
        options = options or {}
        self._options = {}

        self._options.update(options)

    def supports_option(self, option):
        return hasattr(self, '_convert_%s' % option)\
            and callable(getattr(self, '_convert_%s' % option))

    def update(self, options):
        self._options.update(options)

    def __str__(self):
        params = []
        for option, value in self._options.iteritems():
            if value:
                option_list = getattr(self, '_convert_%s' % option)(value)
                params.append('%s' % ' '.join(option_list))

        # codecs should go before the presets so that the files will be matched successfully
        # all other parameters go after so that we can override whatever is in the preset
        codecs = []
        presets = []
        other = []
        for p in params:
            if re.match('codec', p):
                codecs.append(p)
            elif re.match('\-.pre', p):
                presets.append(p)
            else:
                other.append(p)

        params = codecs + presets + other

        params_string = ' '.join(params)
        if self['aspect'] and self['resolution']:
            params_string += '%s' % self._convert_aspect(self._calculate_aspect())

        return params_string

    def as_parameters(self):
        params = []
        for option, value in self._options.iteritems():
            if value:
                params.append(getattr(self, '_convert_%s' % option)(value))

        # codecs should go before the presets so that the files will be matched successfully
        # all other parameters go after so that we can override whatever is in the preset
        codecs = []
        presets = []
        other = []
        for p in params:
            if re.match('codec', p[0]):
                codecs.append(p)
            elif re.match('\-.pre', p[0]):
                presets.append(p)
            else:
                other.append(p)

        params = codecs + presets + other

        if self['aspect'] and self['resolution']:
            params += self._convert_aspect(self._calculate_aspect())

        return [i for l in params for i in l]

    @property
    def width(self):
        try:
            return int(self['resolution'].split('x')[0])
        except IndexError:
            return

    @property
    def height(self):
        try:
            return int(self['resolution'].split('x')[1])
        except IndexError:
            return

    def _convert_aspect(self, value):
        return ['-aspect', value]

    def _calculate_aspect(self):
        return float(self.width) / float(self.height)

    def _convert_video_codec(self, value):
        return ['-vcodec', value]

    def _convert_frame_rate(self, value):
        return ['-r', value]

    def _convert_resolution(self, value):
        return ['-s', value]

    def _convert_video_bitrate(self, value):
        return ['-b:v', self.k_format(value)]

    def _convert_audio_codec(self, value):
        return ['-acodec', value]

    def _convert_audio_bitrate(self, value):
        return ['-b:a', self.k_format(value)]

    def _convert_audio_sample_rate(self, value):
        return ['-ar', value]

    def _convert_audio_channels(self, value):
        return ['-ac', value]

    def _convert_video_max_bitrate(self, value):
        return ['-maxrate', self.k_format(value)]

    def _convert_video_min_bitrate(self, value):
        return ['-minrate', self.k_format(value)]

    def _convert_buffer_size(self, value):
        return ['-bufsize', self.k_format(value)]

    def _convert_video_bitrate_tolerance(self, value):
        return ['-bt', self.k_format(value)]

    def _convert_threads(self, value):
        return ['-threads', value]

    def _convert_duration(self, value):
        return ['-t', value]

    def _convert_video_preset(self, value):
        return ['-vpre', value]

    def _convert_audio_preset(self, value):
        return ['-apre', value]

    def _convert_file_preset(self, value):
        return ['-fpre', value]

    def _convert_keyframe_interval(self, value):
        return ['-g', value]

    def _convert_seek_time(self, value):
        return ['-ss', value]

    def _convert_screenshot(self, value):
        if not value:
            return []

        if isinstance(value, int):
            return ['-vf', 'fps=fps=1/%d' % value]
        else:
            return ['-vframes', '1', '-f', 'image2']

    def _convert_x264_profile(self, value):
        return ['-vprofile', value]

    def _convert_x264_preset(self, value):
        return ['-preset', value]

    def _convert_watermark(self, value):
        return ['-i', value]

    def _convert_custom(self, value):
        return value

    def k_format(self, value):
        if re.match('^.*k$', value):
            return value

        return '%sk' % value

    def get(self, item, default=None):
        return self._options.get(item, default)

    def pop(self, item, default=None):
        return self._options.pop(item, default)

    def __getitem__(self, item):
        return self._options.get(item)

    def __setitem__(self, key, value):
        self._options[key] = value
