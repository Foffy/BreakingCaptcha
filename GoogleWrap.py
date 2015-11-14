#!/usr/bin/env python2.7

"""Library for performing speech recognition (transcribtion) with support for Google Speech Recognition"""

__author__ = "Ionel Moreau-Serez"
__version__ = "1.0"
__license__ = "BSD"

import io, os, subprocess, wave
import audioop
import platform, stat
import json
import apiKey

try: # try to use python2 module
    from urllib2 import Request, urlopen, URLError, HTTPError
except ImportError: # otherwise, use python3 module
    from urllib.request import Request, urlopen
    from urllib.error import URLError, HTTPError

# constants
API_KEY = 'api.key'

# define exceptions
class WaitTimeoutError(Exception): pass
class RequestError(Exception): pass
class UnknownValueError(Exception): pass

class AudioSource(object):
    def __init__(self):
        raise NotImplementedError("this is an abstract class")

    def __enter__(self):
        raise NotImplementedError("this is an abstract class")

    def __exit__(self, exc_type, exc_value, traceback):
        raise NotImplementedError("this is an abstract class")

class WavFile(AudioSource):
    """
    Creates a new ``WavFile`` instance given a WAV audio file `filename_or_fileobject`. Subclass of ``AudioSource``.
    If ``filename_or_fileobject`` is a string, then it is interpreted as a path to a WAV audio file (mono or stereo) on the filesystem. Otherwise, ``filename_or_fileobject`` should be a file-like object such as ``io.BytesIO`` or similar.
    Note that the WAV file must be in PCM/LPCM format; WAVE_FORMAT_EXTENSIBLE and compressed WAV are not supported and may result in undefined behaviour.
    """

    def __init__(self, filename_or_fileobject):
        if isinstance(filename_or_fileobject, str):
            self.filename = filename_or_fileobject
        else:
            assert filename_or_fileobject.read, "Given WAV file must be a filename string or a file-like object"
            self.filename = None
            self.wav_file = filename_or_fileobject
        self.stream = None
        self.DURATION = None

    def __enter__(self):
        assert self.stream is None, "This audio source is already inside a context manager"
        if self.filename is not None: self.wav_file = open(self.filename, "rb")
        self.wav_reader = wave.open(self.wav_file, "rb")
        assert 1 <= self.wav_reader.getnchannels() <= 2, "Audio must be mono or stereo"
        self.SAMPLE_WIDTH = self.wav_reader.getsampwidth()
        self.SAMPLE_RATE = self.wav_reader.getframerate()
        self.CHUNK = 4096
        self.FRAME_COUNT = self.wav_reader.getnframes()
        self.DURATION = self.FRAME_COUNT / float(self.SAMPLE_RATE)
        self.stream = WavFile.WavStream(self.wav_reader)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.filename: self.wav_file.close()
        self.stream = None
        self.DURATION = None

    class WavStream(object):
        def __init__(self, wav_reader):
            self.wav_reader = wav_reader

        def read(self, size = -1):
            buffer = self.wav_reader.readframes(self.wav_reader.getnframes() if size == -1 else size)
            if isinstance(buffer, str) and str is not bytes: buffer = b"" # workaround for https://bugs.python.org/issue24608, unfortunately only fixes the issue for little-endian systems
            if self.wav_reader.getnchannels() != 1: # stereo audio
                buffer = audioop.tomono(buffer, self.wav_reader.getsampwidth(), 1, 1) # convert stereo audio data to mono
            return buffer

class AudioData(object):
    def __init__(self, frame_data, sample_rate, sample_width):
        assert sample_rate > 0, "Sample rate must be a positive integer"
        assert sample_width % 1 == 0 and sample_width > 0, "Sample width must be a positive integer"
        self.frame_data = frame_data
        self.sample_rate = sample_rate
        self.sample_width = int(sample_width)

    def get_wav_data(self):
        """
        Returns a byte string representing the contents of a WAV file containing the audio represented by the ``AudioData`` instance.
        Writing these bytes directly to a file results in a valid WAV file.
        """
        with io.BytesIO() as wav_file:
            wav_writer = wave.open(wav_file, "wb")
            try: # note that we can't use context manager due to Python 2 not supporting it
                wav_writer.setframerate(self.sample_rate)
                wav_writer.setsampwidth(self.sample_width)
                wav_writer.setnchannels(1)
                wav_writer.writeframes(self.frame_data)
            finally:  # make sure resources are cleaned up
                wav_writer.close()
            wav_data = wav_file.getvalue()
        return wav_data

    def get_flac_data(self):
        """
        Returns a byte string representing the contents of a FLAC file containing the audio represented by the ``AudioData`` instance.
        Writing these bytes directly to a file results in a valid FLAC file.
        """
        wav_data = self.get_wav_data()

        # determine which converter executable to use
        system = platform.system()
        path = os.path.dirname(os.path.abspath(__file__)) # directory of the current module file, where all the FLAC bundled binaries are stored
        flac_converter = shutil_which("flac") # check for installed version first
        if flac_converter is None: # flac utility is not installed
            if system == "Windows" and platform.machine() in ["i386", "x86", "x86_64", "AMD64"]: # Windows NT, use the bundled FLAC conversion utility
                flac_converter = os.path.join(path, "flac-win32.exe")
            elif system == "Linux" and platform.machine() in ["i386", "x86", "x86_64", "AMD64"]:
                flac_converter = os.path.join(path, "flac-linux-i386")
            elif system == "Darwin" and platform.machine() in ["i386", "x86", "x86_64", "AMD64"]:
                flac_converter = os.path.join(path, "flac-mac")
            else:
                raise OSError("FLAC conversion utility not available - consider installing the FLAC command line application using `brew install flac` or your operating system's equivalent")

        # mark FLAC converter as executable
        try:
            stat_info = os.stat(flac_converter)
            os.chmod(flac_converter, stat_info.st_mode | stat.S_IEXEC)
        except OSError: pass

        # run the FLAC converter with the WAV data to get the FLAC data
        process = subprocess.Popen("\"{0}\" --stdout --totally-silent --best -".format(flac_converter), stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        flac_data, stderr = process.communicate(wav_data)
        return flac_data

class Recognizer(AudioSource):
    def __init__(self):
        """
        Creates a new ``Recognizer`` instance, which represents a collection of speech recognition functionality.
        """
        self.energy_threshold = 300 # minimum audio energy to consider for recording
        self.dynamic_energy_threshold = True
        self.dynamic_energy_adjustment_damping = 0.15
        self.dynamic_energy_ratio = 1.5
        self.pause_threshold = 0.8 # seconds of non-speaking audio before a phrase is considered complete
        self.phrase_threshold = 0.3 # minimum seconds of speaking audio before we consider the speaking audio a phrase - values below this are ignored (for filtering out clicks and pops)
        self.non_speaking_duration = 0.5 # seconds of non-speaking audio to keep on both sides of the recording

    def record(self, source, duration = None, offset = None):
        """
        Records up to ``duration`` seconds of audio from ``source`` (an ``AudioSource`` instance) starting at ``offset`` (or at the beginning if not specified) into an ``AudioData`` instance, which it returns.
        If ``duration`` is not specified, then it will record until there is no more audio input.
        """
        assert isinstance(source, AudioSource), "Source must be an audio source"

        frames = io.BytesIO()
        seconds_per_buffer = (source.CHUNK + 0.0) / source.SAMPLE_RATE
        elapsed_time = 0
        offset_time = 0
        offset_reached = False
        while True: # loop for the total number of chunks needed
            if offset and not offset_reached:
                offset_time += seconds_per_buffer
                if offset_time > offset:
                    offset_reached = True

            buffer = source.stream.read(source.CHUNK)
            if len(buffer) == 0: break

            if offset_reached or not offset:
                elapsed_time += seconds_per_buffer
                if duration and elapsed_time > duration: break

                frames.write(buffer)

        frame_data = frames.getvalue()
        frames.close()
        return AudioData(frame_data, source.SAMPLE_RATE, source.SAMPLE_WIDTH)

    def recognize_google(self, audio_data, key = None, language = "en-US", show_all = False):
        
        assert isinstance(audio_data, AudioData), "`audio_data` must be audio data"
        assert key is None or isinstance(key, str), "`key` must be `None` or a string"
        assert isinstance(language, str), "`language` must be a string"

        flac_data, sample_rate = audio_data.get_flac_data(), audio_data.sample_rate
        if key is None: key = apiKey.getKey(API_KEY)
        url = "http://www.google.com/speech-api/v2/recognize?client=chromium&lang={0}&key={1}".format(language, key)
        request = Request(url, data = flac_data, headers = {"Content-Type": "audio/x-flac; rate={0}".format(sample_rate)})

        # obtain audio transcription results
        try:
            response = urlopen(request)
        except HTTPError as e:
            raise RequestError("recognition request failed: {0}".format(getattr(e, "reason", "status {0}".format(e.code)))) # use getattr to be compatible with Python 2.6
        except URLError as e:
            raise RequestError("recognition connection failed: {0}".format(getattr(e, "reason", "status {0}".format(e.code)))) # use getattr to be compatible with Python 2.6
        response_text = response.read().decode("utf-8")

        # ignore any blank blocks
        actual_result = []
        for line in response_text.split("\n"):
            if not line: continue
            result = json.loads(line)["result"]
            if len(result) != 0:
                actual_result = result[0]
                break

        if show_all: return actual_result

        # return the best guess
        if "alternative" not in actual_result: raise UnknownValueError()
        for entry in actual_result["alternative"]:
            if "transcript" in entry:
                return entry["transcript"]

        # no transcriptions available
        raise UnknownValueError()

def shutil_which(pgm):
    """
    python2 backport of python3's shutil.which()
    """
    path = os.getenv('PATH')
    for p in path.split(os.path.pathsep):
        p = os.path.join(p, pgm)
        if os.path.exists(p) and os.access(p, os.X_OK):
            return p