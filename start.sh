#!/usr/bin/env bash
TOP=$(cd $(dirname $0) && pwd -L)

DEFAULT_CONFIG="$TOP/mycroft/configuration/mycroft.conf"
SYSTEM_CONFIG="/etc/mycroft/mycroft.conf"
USER_CONFIG="$HOME/.mycroft/mycroft.conf"
function get_config_value() {
  key="$1"
  default="$2"
  value="null"
  for file in $USER_CONFIG $SYSTEM_CONFIG $DEFAULT_CONFIG;   do
    if [[ -r $file ]] ; then
        # remove comments in config for jq to work
        # assume they may be preceded by whitespace, but nothing else
        parsed="$( sed 's:^\s*//.*$::g' $file )"
        echo "$parsed" >> "$TOP/mycroft/configuration/sys.conf"
        value=$( jq -r "$key" "$TOP/mycroft/configuration/sys.conf" )
        rm -rf "$TOP/mycroft/configuration/sys.conf"
        if [[ "${value}" != "null" ]] ;  then
            echo "$value"
            return

        fi
    fi
  done
  echo "$default"
}



# ${TOP}/scripts/prepare-msm.sh

case $1 in
	"service") SCRIPT=${TOP}/mycroft/messagebus/service/main.py ;;
	"webchat") SCRIPT=${TOP}/mycroft/client/webchat/main.py ;;
	"hack") SCRIPT=${TOP}/mycroft/server/bridges/hack_chat_bridge.py ;;
	"fb") SCRIPT=${TOP}/mycroft/server/bridges/facebook_chat_bridge.py ;;
	"server") SCRIPT=${TOP}/mycroft/client/server/main.py ;;
	"client") SCRIPT=${TOP}/mycroft/client/client/main.py ;;
	"skills") SCRIPT=${TOP}/mycroft/skills/main.py ;;
	"audio") SCRIPT=${TOP}/mycroft/audio/main.py ;;
	"display") SCRIPT=${TOP}/mycroft/screen_display/main.py ;;
	"wav") SCRIPT=${TOP}/mycroft/client/wave_file/main.py ;;
	"skill_container") SCRIPT=${TOP}/mycroft/skills/container.py ;;
	"voice") SCRIPT=${TOP}/mycroft/client/speech/main.py ;;
	"cli") SCRIPT=${TOP}/mycroft/client/text/main.py ;;
	"audiotest") SCRIPT=${TOP}/mycroft/util/audio_test.py ;;
	"collector") SCRIPT=${TOP}/mycroft_data_collection/cli.py ;;
	"unittest") SCRIPT=${TOP}/test/main.py ;;
	"audioaccuracytest") SCRIPT=${TOP}/mycroft/audio-accuracy-test/audio_accuracy_test.py ;;
	"sdkdoc") SCRIPT=${TOP}/doc/generate_sdk_docs.py ;;
    "enclosure") SCRIPT=${TOP}/mycroft/client/enclosure/main.py ;;
    "wifi") SCRIPT=${TOP}/mycroft/client/wifisetup/main.py ;;
	*) echo "Usage: start.sh [service | skills | skill_container | voice | cli | server | client | audio | display | wav | audiotest| audioaccuracytest | collector | unittest | enclosure | sdkdoc | wifi]"; exit ;;
esac

echo "Starting $@"

shift

use_virtualenvwrapper="$(get_config_value '.enclosure.use_virtualenvwrapper' 'true')"
if [[ ${use_virtualenvwrapper} == "true" ]] ; then
    if [ -z "$WORKON_HOME" ]; then
        VIRTUALENV_ROOT=${VIRTUALENV_ROOT:-"${HOME}/.virtualenvs/jarbas"}
    else
        VIRTUALENV_ROOT="$WORKON_HOME/jarbas"
    fi
    source ${VIRTUALENV_ROOT}/bin/activate
fi

export PYTHONPATH="${PYTHONPATH}:${TOP}/mycroft"

PYTHONPATH=${TOP} python ${SCRIPT} $@
