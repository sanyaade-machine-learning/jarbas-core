# Copyright 2017 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import subprocess
from time import time, sleep

import os
import stat
import os.path
from os.path import exists

from mycroft import MYCROFT_ROOT_PATH
from mycroft.configuration import Configuration
from mycroft.tts import TTS, TTSValidator
from mycroft.util.log import LOG
from mycroft.util.download import download
from mycroft.api import DeviceApi
from threading import Thread

config = Configuration.get().get("tts").get("mimic")

BIN = config.get("path",
                 os.path.join(MYCROFT_ROOT_PATH, 'mimic', 'bin', 'mimic'))

if not os.path.isfile(BIN):
    # Search for mimic on the path
    import distutils.spawn
    BIN = distutils.spawn.find_executable("mimic")

SUBSCRIBER_VOICES = {'trinity': '/opt/mycroft/voices/mimic_tn'}


def download_subscriber_voices(selected_voice):
    """
        Function to download all premium voices, starting with
        the currently selected if applicable
    """
    def make_executable(dest):
        """ Call back function to make the downloaded file executable. """
        LOG.info('Make executable')
        # make executable
        st = os.stat(dest)
        os.chmod(dest, st.st_mode | stat.S_IEXEC)

    # First download the selected voice if needed
    voice_file = SUBSCRIBER_VOICES.get(selected_voice)
    print voice_file
    if voice_file is not None and not exists(voice_file):
        print 'voice foesn\'t exist, downloading'
        dl = download(DeviceApi().get_subscriber_voice_url(selected_voice),
                      voice_file, make_executable)
        # Wait for completion
        while not dl.done:
            sleep(1)

    # Download the rest of the subsciber voices as needed
    for voice in SUBSCRIBER_VOICES:
        voice_file = SUBSCRIBER_VOICES[voice]
        if not exists(voice_file):
            dl = download(DeviceApi().get_subscriber_voice_url(voice),
                          voice_file, make_executable)
            # Wait for completion
            while not dl.done:
                sleep(1)


class Mimic(TTS):
    def __init__(self, lang, voice):
        super(Mimic, self).__init__(lang, voice, MimicValidator(self))
        self.dl = None
        self.clear_cache()
        self.type = 'wav'
        # Download subscriber voices if needed
        self.is_subscriber = DeviceApi().is_subscriber
        if self.is_subscriber:
            t = Thread(target=download_subscriber_voices, args=[self.voice])
            t.daemon = True
            t.start()

    @property
    def args(self):
        """ Build mimic arguments. """
        if (self.voice in SUBSCRIBER_VOICES and
                exists(SUBSCRIBER_VOICES[self.voice]) and self.is_subscriber):
            # Use subscriber voice
            mimic_bin = SUBSCRIBER_VOICES[self.voice]
            voice = self.voice
        elif self.voice in SUBSCRIBER_VOICES:
            # Premium voice but bin doesn't exist, use ap while downloading
            mimic_bin = BIN
            voice = 'ap'
        else:
            # Normal case use normal binary and selected voice
            mimic_bin = BIN
            voice = self.voice

        args = [mimic_bin, '-voice', voice, '-psdur']
        stretch = config.get('duration_stretch', None)
        if stretch:
            args += ['--setf', 'duration_stretch=' + stretch]
        return args

    def get_tts(self, sentence, wav_file):
        #  Generate WAV and phonemes
        phonemes = subprocess.check_output(self.args + ['-o', wav_file,
                                                        '-t', sentence])
        return wav_file, phonemes


class MimicValidator(TTSValidator):
    def __init__(self, tts):
        super(MimicValidator, self).__init__(tts)

    def validate_lang(self):
        # TODO: Verify version of mimic can handle the requested language
        pass

    def validate_connection(self):
        try:
            subprocess.call([BIN, '--version'])
        except:
            LOG.info("Failed to find mimic at: " + str(BIN))
            raise Exception(
                'Mimic was not found. Run install-mimic.sh to install it.')

    def get_tts_class(self):
        return Mimic

