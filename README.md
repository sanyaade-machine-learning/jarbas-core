jarbas - dev fork

these changes are being made into PRs for mycroft-core and will be
unlisted once merged


# wakewords

- [multiple wake words](https://github.com/MycroftAI/mycroft-core/pull/1233)
- optionally play a sound per wake word
- optionally start listening
- optionally considered as utterance

# STT support

- [pocketsphinx](https://github.com/MycroftAI/mycroft-core/pull/1184) default stt
- pocketsphinx es-es language model included
- pocketsphinx en-us language model included
- [houndify stt](https://github.com/MycroftAI/mycroft-core/pull/1229)
- [bing stt](https://github.com/MycroftAI/mycroft-core/pull/1229)

# TTS support

- [bing tts](https://github.com/MycroftAI/mycroft-core/pull/1260)
- [polly tts](https://github.com/MycroftAI/mycroft-core/pull/1262)
- [watson tts](https://github.com/MycroftAI/mycroft-core/pull/1261)
- beep speak tts (r2d2 sounds)

# privacy enhancements

- blacklist pairing skill
- blacklist configuration skill
- disable remote configuration
- disable pairing check
- disable mycroft API
- disable mycroft STT
- disable ww upload
- disable identity manager
- disable mycroft ai remote skill settings
- privacy compromising options removed from config (server, opt in, ww upload, mycroft stt)
- [secure websocket](https://github.com/MycroftAI/mycroft-core/pull/1148) by default

# dev tools

- [messagebus api](https://github.com/MycroftAI/mycroft-core/pull/1013)
- include [auto_translatable skill class](https://github.com/JarbasAl/auto_translatable_skills)
- util to [get phonemes](https://github.com/MycroftAI/mycroft-core/pull/1174)

# internals

- [speak message metadata](https://github.com/MycroftAI/mycroft-core/pull/1069), mute, more_speech and context options
- message context and [source/destinatary tracking](https://github.com/MycroftAI/mycroft-core/pull/796/)
- [centralized api](https://github.com/MycroftAI/mycroft-core/pull/1061/files) section in config
- [fallback order override](https://github.com/MycroftAI/mycroft-core/pull/987) option in config
- [enable/disable/status TTS](https://github.com/MycroftAI/mycroft-core/pull/556) signal
- [enable/disable intent signal](https://github.com/MycroftAI/mycroft-core/pull/860)



# Links:

* [My website](jarbasai.github.io)
* [Patreon](https://www.patreon.com/jarbasAI)
* [My old github](https://github.com/JarbasAI)
* [Twitter](twitter.com/JarbasAi)


# Mycroft Links

* [mycroft-core](https://github.com/MycroftAI/mycroft-core)
* [Creating a Skill](https://docs.mycroft.ai/skill.creation)
* [Documentation](https://docs.mycroft.ai)
* [Release Notes](https://github.com/MycroftAI/mycroft-core/releases)
* [Mycroft Chat](https://chat.mycroft.ai)
* [Mycroft Forum](https://community.mycroft.ai)
* [Mycroft Blog](https://mycroft.ai/blog)