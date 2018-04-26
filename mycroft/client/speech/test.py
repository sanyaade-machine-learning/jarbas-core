import pulsectl

pulse = pulsectl.Pulse('Mycroft-audio-service')

for sink in pulse.sink_input_list():
    if sink.name != 'mycroft-voice':
        print sink