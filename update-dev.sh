#!/usr/bin/env bash

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

SOURCE="${BASH_SOURCE[0]}"
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
DEFAULT_CONFIG="$DIR/mycroft/configuration/mycroft.conf"
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
        echo "$parsed" >> "$DIR/mycroft/configuration/sys.conf"
        value=$( jq -r "$key" "$DIR/mycroft/configuration/sys.conf" )
        rm -rf "$DIR/mycroft/configuration/sys.conf"
        if [[ "${value}" != "null" ]] ;  then
            echo "$value"
            return

        fi
    fi
  done
  echo "$default"
}

git pull

use_virtualenvwrapper="$(get_config_value '.enclosure.use_virtualenvwrapper' 'true')"

if [[ ${use_virtualenvwrapper} == "true" ]] ; then
    if [ -z "$WORKON_HOME" ]; then
        VIRTUALENV_ROOT=${VIRTUALENV_ROOT:-"${HOME}/.virtualenvs/jarbas"}
    else
        VIRTUALENV_ROOT="$WORKON_HOME/jarbas"
    fi

    source "${VIRTUALENV_ROOT}/bin/activate"
    easy_install pip==9.0.1
    pip install --upgrade virtualenv
    pip install -r requirements.txt
else
    sudo easy_install pip
    sudo pip install -r requirements.txt
fi

sudo ln -sf ${DIR}/mycroft /usr/local/lib/python2.7/site-packages/mycroft
export PYTHONPATH="${PYTHONPATH}:${DIR}/mycroft"

