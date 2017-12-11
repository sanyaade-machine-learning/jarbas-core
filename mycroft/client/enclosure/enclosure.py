from mycroft.messagebus.client.ws import WebsocketClient
from threading import Thread
from mycroft.util.log import LOG
import time


class Enclosure(object):
    """
    This base class is intended to be used to interface with the hardware
    that is running Mycroft.  It exposes all possible commands which
    can be sent to a Mycroft enclosure implementation.

    Different enclosure implementations may implement this differently
    and/or may ignore certain API calls completely.  For example,
    the eyes_color() API might be ignore on a Mycroft that uses simple
    LEDs which only turn on/off, or not at all on an implementation
    where there is no face at all.
    """

    def __init__(self, ws=None, name=""):
        if ws is None:
            self.ws = WebsocketClient()
            self.event_thread = Thread(target=self.connect)
            self.event_thread.setDaemon(True)
            self.event_thread.start()
        else:
            self.ws = ws
        self.log = LOG
        self.name = name
        self.ws.on("enclosure.reset", self.reset)
        self.ws.on("enclosure.system.reset", self.system_reset)
        self.ws.on("enclosure.system.mute", self.system_mute)
        self.ws.on("enclosure.system.unmute", self.system_unmute)
        self.ws.on("enclosure.system.blink", self.system_blink)
        self.ws.on("enclosure.system.eyes.on", self.eyes_on)
        self.ws.on("enclosure.system.eyes.off", self.eyes_off)
        self.ws.on("enclosure.system.eyes.blink", self.eyes_blink)
        self.ws.on("enclosure.system.eyes.narrow", self.eyes_narrow)
        self.ws.on("enclosure.system.eyes.look", self.eyes_look)
        self.ws.on("enclosure.system.eyes.color", self.eyes_color)
        self.ws.on("enclosure.system.eyes.brightness", self.eyes_brightness)
        self.ws.on("enclosure.system.eyes.reset", self.eyes_reset)
        self.ws.on("enclosure.system.eyes.timedspin", self.eyes_timed_spin)
        self.ws.on("enclosure.system.eyes.volume", self.eyes_volume)
        self.ws.on("enclosure.system.mouth.reset", self.mouth_reset)
        self.ws.on("enclosure.system.mouth.talk", self.mouth_talk)
        self.ws.on("enclosure.system.mouth.think", self.mouth_think)
        self.ws.on("enclosure.system.mouth.listen", self.mouth_listen)
        self.ws.on("enclosure.system.mouth.smile", self.mouth_smile)
        self.ws.on("enclosure.system.mouth.viseme", self.mouth_viseme)
        self.ws.on("enclosure.system.mouth.text", self.mouth_text)
        self.ws.on("enclosure.system.mouth.display", self.mouth_display)
        self.ws.on("enclosure.system.weather.display", self.weather_display)
        self.ws.on("enclosure.mouth.events.activate",
                   self.activate_mouth_events)
        self.ws.on("enclosure.mouth.events.deactivate",
                   self.deactivate_mouth_events)
        self.ws.on("mycroft.awoken", self.handle_awake)
        self.ws.on("recognizer_loop:sleep", self.handle_sleep)
        self.ws.on("speak", self.handle_speak)
        self.ws.on('recognizer_loop:record_begin', self.record_begin)
        self.ws.on('recognizer_loop:record_end', self.record_end)
        self.ws.on('recognizer_loop:audio_output_start', self.talk_start)
        self.ws.on('recognizer_loop:audio_output_end', self.talk_stop)

    def run(self):
        ''' start enclosure '''
        while True:
            time.sleep(1)

    def record_begin(self, message):
        ''' listening started '''
        pass

    def record_end(self, message):
        ''' listening ended '''
        pass

    def talk_start(self, message):
        ''' speaking started '''
        pass

    def talk_stop(self, message):
        ''' speaking ended '''
        pass

    def handle_awake(self, message):
        ''' handle wakeup animation '''
        pass

    def handle_sleep(self, message):
        ''' handle naptime animation '''
        pass

    def handle_speak(self, message):
        ''' handle speak messages, intended for enclosures that disregard
        visemes '''
        pass

    def connect(self):
        # Once the websocket has connected, just watch it for speak events
        self.ws.run_forever()

    def reset(self, message):
        """The enclosure should restore itself to a started state.
        Typically this would be represented by the eyes being 'open'
        and the mouth reset to its default (smile or blank).
        """
        pass

    def system_reset(self, message):
        """The enclosure hardware should reset any CPUs, etc."""
        pass

    def system_mute(self, message):
        """Mute (turn off) the system speaker."""
        pass

    def system_unmute(self, message):
        """Unmute (turn on) the system speaker."""
        pass

    def system_blink(self, message):
        """The 'eyes' should blink the given number of times.
        Args:
            times (int): number of times to blink
        """
        times = message.data.get("times")

    def eyes_on(self, message):
        """Illuminate or show the eyes."""
        pass

    def eyes_off(self, message):
        """Turn off or hide the eyes."""
        pass

    def eyes_blink(self, message):
        """Make the eyes blink
        Args:
            side (str): 'r', 'l', or 'b' for 'right', 'left' or 'both'
        """
        side = message.data.get("side")

    def eyes_narrow(self, message):
        """Make the eyes look narrow, like a squint"""
        pass

    def eyes_look(self, message):
        """Make the eyes look to the given side
        Args:
            side (str): 'r' for right
                        'l' for left
                        'u' for up
                        'd' for down
                        'c' for crossed
        """
        side = message.data.get("side")

    def eyes_color(self, message):
        """Change the eye color to the given RGB color
        Args:
            r (int): 0-255, red value
            g (int): 0-255, green value
            b (int): 0-255, blue value
        """
        r = message.data.get("r")
        g = message.data.get("g")
        b = message.data.get("b")

    def eyes_brightness(self, message):
        """Set the brightness of the eyes in the display.
        Args:
            level (int): 1-30, bigger numbers being brighter
        """
        level = message.data.get("brightness", 30)

    def eyes_reset(self, message):
        """Restore the eyes to their default (ready) state."""
        pass

    def eyes_timed_spin(self, message):
        """Make the eyes 'roll' for the given time.
        Args:
            length (int): duration in milliseconds of roll, None = forever
        """
        length = message.data.get("length")

    def eyes_volume(self, message):
        """Indicate the volume using the eyes
        Args:
            volume (int): 0 to 11
        """
        volume = message.data.get("volume")

    def mouth_reset(self, message):
        """Restore the mouth display to normal (blank)"""
        pass

    def mouth_talk(self, message):
        """Show a generic 'talking' animation for non-synched speech"""
        pass

    def mouth_think(self, message):
        """Show a 'thinking' image or animation"""
        pass

    def mouth_listen(self, message):
        """Show a 'thinking' image or animation"""
        pass

    def mouth_smile(self, message):
        """Show a 'smile' image or animation"""
        pass

    def mouth_viseme(self, message):
        """Display a viseme mouth shape for synched speech
        Args:
            code (int):  0 = shape for sounds like 'y' or 'aa'
                         1 = shape for sounds like 'aw'
                         2 = shape for sounds like 'uh' or 'r'
                         3 = shape for sounds like 'th' or 'sh'
                         4 = neutral shape for no sound
                         5 = shape for sounds like 'f' or 'v'
                         6 = shape for sounds like 'oy' or 'ao'
        """
        code = message.data.get("code")

    def mouth_text(self, message):
        """Display text (scrolling as needed)
        Args:
            text (str): text string to display
        """
        text = message.data.get("text")

    def mouth_display(self, message):
        """Display images on faceplate. Currently supports images up to 16x8,
           or half the face. You can use the 'x' parameter to cover the other
           half of the faceplate.
        Args:
            img_code (str): text string that encodes a black and white image
            x (int): x offset for image
            y (int): y offset for image
            refresh (bool): specify whether to clear the faceplate before
                            displaying the new image or not.
                            Useful if you'd like to display muliple images
                            on the faceplate at once.
        """
        img_code = message.data.get("img_code", "")
        x = message.data.get("x", 0)
        y = message.data.get("y", 0)
        refresh = message.data.get("refresh", True)

    def weather_display(self, message):
        """Show a the temperature and a weather icon

        Args:
            img_code (char): one of the following icon codes
                         0 = sunny
                         1 = partly cloudy
                         2 = cloudy
                         3 = light rain
                         4 = raining
                         5 = stormy
                         6 = snowing
                         7 = wind/mist
            temp (int): the temperature (either C or F, not indicated)
        """
        img_code = message.data.get("img_code")
        temp = message.data.get("temp")

    def activate_mouth_events(self, message):
        """Enable movement of the mouth with speech"""
        pass

    def deactivate_mouth_events(self, message):
        """Disable movement of the mouth with speech"""
        pass
