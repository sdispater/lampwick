# -*- coding: utf-8 -*-

from unittest import TestCase
from lampwick.movie import Movie


class TestMovie(TestCase):

    def test_init(self):
        movie = Movie('/home/sebastien/Slender The Arrival  - Best of Horreur-ZfNIn6lGpuc.mp4')

        self.assertTrue(movie.container is not None)
        print movie.container
        print movie.duration
        print movie.time
        print movie.creation_time
        print movie.bitrate
        print movie.rotation
        print movie.video_stream
        print movie.audio_stream
        print movie.video_codec
        print movie.colorspace
        print movie.frame_rate
        print movie.resolution
        print movie.video_bitrate
        print movie.audio_codec
        print movie.audio_channels
        print movie._audio_channels
        print movie.audio_bitrate
        print movie.audio_sample_rate
        print movie.width
        print movie.height
