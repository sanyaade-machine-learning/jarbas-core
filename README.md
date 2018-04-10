jarbas - dev fork

these changes are being made into PRs for mycroft-core and will be
unlisted once merged, this readme should always be considered half outdated

## usage

to install

    git clone https://github.com/JarbasAl/jarbas-core
    cd jarbas-core
    ./dev_setup.sh

to start

    cd jarbas-core
    ./jarbas.sh start

to stop

    cd jarbas-core
    ./jarbas.sh stop

to update dev env

    cd jarbas-core
    ./update.dev.sh

to update jarbas-core

    cd jarbas-core
    git pull


## wakewords

- [multiple wake words](https://github.com/MycroftAI/mycroft-core/pull/1233)
- optionally play a sound per wake word
- optionally start listening
- optionally considered as utterance

## STT support

- [pocketsphinx](https://github.com/MycroftAI/mycroft-core/pull/1184) default stt
- pocketsphinx es-es language model included
- pocketsphinx en-us language model included

## TTS support

- [polly tts](https://github.com/MycroftAI/mycroft-core/pull/1262)
- beep speak tts (r2d2 sounds)

## privacy enhancements

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
- secure websocket by default
- send emails from your own account, instead of using mycroft's api

## dev tools
- include [mycroft_jarbas_utils](https://github.com/JarbasAl/mycroft_jarbas_utils)

## internals
- virtual env named "jarbas" instead of "mycroft"
- [abstract enclosure](https://github.com/MycroftAI/mycroft-core/pull/1306)
- [speak message metadata](https://github.com/MycroftAI/mycroft-core/pull/1069), mute, more_speech and context options
- message context and [source/destinatary tracking](https://github.com/MycroftAI/mycroft-core/pull/796/)
- [centralized api](https://github.com/MycroftAI/mycroft-core/pull/1061/files) section in config
- [fallback order override](https://github.com/MycroftAI/mycroft-core/pull/987) option in config
- [enable/disable/status TTS](https://github.com/MycroftAI/mycroft-core/pull/556) signal
- changed start scripts (uses screen)
- skills dir configurable in config file
- use virtualenv option in config file

# Links:

* [My website](jarbasai.github.io)
* [Patreon](https://www.patreon.com/jarbasAI)
* [Paypal](https://paypal.me/jarbasAI)
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


## FAQ

workon jarbas does not work, workon command not found:

    Add this to your .bashrc :

        # load virtualenvwrapper for python (after custom PATHs)
        venvwrap="virtualenvwrapper.sh"
        /usr/bin/which -a $venvwrap
        if [ $? -eq 0 ]; then
            venvwrap=`/usr/bin/which $venvwrap`
            source $venvwrap
        fi

    Then use:

        source .bashrc

    to reflect the changes.

    Additionally, if the terminal still sometimes cant find workon, use source .bash_profile to reset and find it again.

    If this fails use "/usr/bin/which -s $venvwrap" instead of "/usr/bin/which -a $venvwrap"


services fail to import mycroft, seems you are not using the provided scripts, before launching mycroft do


    export PYTHONPATH="${PYTHONPATH}:path/to/jarbas-core/mycroft"

    # optionally add this to your .bashrc
