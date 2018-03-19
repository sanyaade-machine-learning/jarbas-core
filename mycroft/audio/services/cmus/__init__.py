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
from mycroft.audio.services import AudioBackend
from mycroft.util.log import LOG
try:
    from pycmus.remote import PyCmus
except ImportError:
    LOG.error("install cmus with \n"
              "sudo apt-get install cmus \n"
              "pip install pycmus")
    raise


class CmusService(AudioBackend):
    """
        Audio backend for cmus.
    """

    def __init__(self, config, emitter, name='cmus'):
        super(CmusService, self).__init__(config, emitter)
        self.config = config
        self.emitter = emitter
        self.name = name
        self.tracks = []
        self.player = PyCmus()
        self.normal_volume = 70

    def supported_uris(self):
        return ['file', 'http', 'https']

    def clear_list(self):
        self.tracks = []

    def add_list(self, tracks):
        self.tracks += tracks
        for track in tracks:
            self.player.send_cmd("-p track")
        LOG.info("Track list is " + str(self.tracks))

    def play(self):
        LOG.info('Call CmusServicePlay')
        self.player.player_play()

    def stop(self):
        LOG.info('CmusServiceStop')
        self.player.player_stop()
        self.clear_list()

    def pause(self):
        self.player.player_pause()

    def resume(self):
        self.player.player_play()

    def next(self):
        self.player.player_next()

    def previous(self):
        self.player.player_prev()

    def lower_volume(self):
        self.player.set_volume(self.normal_volume/3)

    def restore_volume(self):
        self.player.set_volume(self.normal_volume)

    def track_info(self):
        return self.player.get_status_dict()


def load_service(base_config, emitter):
    backends = base_config.get('backends', [])
    services = [(b, backends[b]) for b in backends
                if backends[b]['type'] == 'cmus']
    instances = [CmusService(s[1], emitter, s[0]) for s in services]
    return instances
