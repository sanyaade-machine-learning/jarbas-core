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

from mycroft.enclosure import Enclosure


class EnclosureEyes(Enclosure):
    """
    Listens to enclosure commands for Mycroft's Eyes.

    Performs the associated command on Arduino by writing on the Serial port.
    """

    def __init__(self, ws, writer):
        super(EnclosureEyes, self).__init__(ws, "eyes")
        self.writer = writer

    def eyes_on(self, message=None):
        self.writer.write("eyes.on")

    def eyes_off(self, message=None):
        self.writer.write("eyes.off")

    def eyes_blink(self, message=None):
        side = "b"
        if message and message.data:
            side = message.data.get("side", side)
        self.writer.write("eyes.blink=" + side)

    def eyes_narrow(self, message=None):
        self.writer.write("eyes.narrow")

    def eyes_look(self, message=None):
        if message and message.data:
            side = message.data.get("side", "")
            self.writer.write("eyes.look=" + side)

    def eyes_color(self, message=None):
        r, g, b = 255, 255, 255
        if message and message.data:
            r = int(message.data.get("r", r))
            g = int(message.data.get("g", g))
            b = int(message.data.get("b", b))
        color = (r * 65536) + (g * 256) + b
        self.writer.write("eyes.color=" + str(color))

    def eyes_brightness(self, message=None):
        level = 30
        if message and message.data:
            level = message.data.get("level", level)
        self.writer.write("eyes.level=" + str(level))

    def eyes_volume(self, message=None):
        volume = 4
        if message and message.data:
            volume = message.data.get("volume", volume)
        self.writer.write("eyes.volume=" + str(volume))

    def eyes_reset(self, message=None):
        self.writer.write("eyes.reset")

    def eyes_spin(self, message=None):
        self.writer.write("eyes.spin")

    def eyes_timed_spin(self, message=None):
        length = 5000
        if message and message.data:
            length = message.data.get("length", length)
        self.writer.write("eyes.spin=" + str(length))
