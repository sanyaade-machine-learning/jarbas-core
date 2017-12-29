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

function get_config_value() {
  key="$1"
  default="$2"
  value="null"
  for file in ~/.mycroft/mycroft.conf /etc/mycroft/mycroft.conf ; do
    if [[ -r ~/.mycroft/mycroft.conf ]] ; then
        value=$( jq -r "$key" "$file" )
        if [[ "${value}" != "null" ]] ;  then
            echo "$value"
            return
        fi
    fi
  done
  echo "$default"
}

use_virtualenvwrapper="$(get_config_value '.enclosure.use_virtualenvwrapper' 'false')"
if [[ ${use_virtualenvwrapper} == "true" ]] ; then
    if [ -z "$WORKON_HOME" ]; then
        VIRTUALENV_ROOT=${VIRTUALENV_ROOT:-"${HOME}/.virtualenvs/mycroft"}
    else
        VIRTUALENV_ROOT="$WORKON_HOME/mycroft"
    fi

    source "${VIRTUALENV_ROOT}/bin/activate"
    easy_install pip==7.1.2
    pip install --upgrade virtualenv
else
    easy_install pip
fi

pip install -r requirements.txt
