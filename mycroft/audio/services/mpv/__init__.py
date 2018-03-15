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
from mycroft.audio.services.mpv.mpv_lib import MPV
from mycroft.audio.services import AudioBackend
from mycroft.util.log import LOG


class MPVService(AudioBackend):
    def __init__(self, config, emitter=None, name='mpv'):
        super(MPVService, self).__init__(config, emitter)
        self.player = MPV(ytdl=True)
        self.player._set_property('video', 'no')
        self.name = name

    def track_start(self, data, other):
        if self._track_start_callback:
            self._track_start_callback(self.track_info()['name'])

    def supported_uris(self):
        return ['file', 'http', 'https']

    def clear_list(self):
        self.player.playlist_clear()

    def add_list(self, tracks):
        for track in tracks:
            self.player.playlist_append(track)

    def play(self):
        LOG.info('MpvService Play')
        filename = self.player.playlist_filenames[0]
        self.player.playlist_remove(0)
        self.player.loadfile(filename, 'append-play')

    def stop(self):
        LOG.info('MpvService Stop')
        self.clear_list()
        self.player.quit()
        self.player.terminate()

    def pause(self):
        LOG.info('MpvService Pause')
        self.player._set_property("cycle", "pause")

    def resume(self):
        LOG.info('MpvService Resume')
        self.player._set_property("cycle", "pause")

    def next(self):
        self.player.playlist_next()

    def previous(self):
        self.player.playlist_prev()

    def lower_volume(self):
        pass

    def restore_volume(self):
        pass

    def track_info(self):
        ret = {"track": self.player.playlist_filenames[0]}

        return ret


def load_service(base_config, emitter):
    backends = base_config.get('backends', [])
    services = [(b, backends[b]) for b in backends
                if backends[b]['type'] == 'mpv']
    instances = [MPVService(s[1], emitter, s[0]) for s in services]
    return instances
