#!/usr/bin/env bash


SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done

DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
SCRIPTS="$DIR/scripts"

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

use_virtualenvwrapper="$(get_config_value '.enclosure.use_virtualenvwrapper' 'true')"

if [[ ${use_virtualenvwrapper} == "true" ]] ; then
    echo "using venv"
    if [ -z "$WORKON_HOME" ]; then
        VIRTUALENV_ROOT=${VIRTUALENV_ROOT:-"${HOME}/.virtualenvs/jarbas"}
    else
        VIRTUALENV_ROOT="$WORKON_HOME/jarbas"
    fi

    source "${VIRTUALENV_ROOT}/bin/activate"
else
    echo "not using venv"
    export PYTHONPATH="${PYTHONPATH}:${DIR}/mycroft"

fi

function screen-config {
  echo "
    # Generated
    deflog on
    logfile scripts/logs/$1.log
    logfile flush 1
  "
}

function usage-exit {

echo "

Quickly start, stop or restart Mycroft's essential services in detached screens

usage: $0 (start|stop|restart) [options]

      start          launch all necessary services to run mycroft
      stop           end all services
      restart        stop, then start all services
      -h, --help     this help message

start options:
      [nothing]      both cli and voice client
      -v, --voice    only voice client
      -c, --cli      only cli
      -d, --debug    only cli, in current terminal

restart options:
      (same as start)

screen tips:
            run 'screen -list' to see all running screens
            run 'screen -r <screen-name>' (e.g. 'screen -r mycroft-service') to reatach a screen
            press ctrl + a, ctrl + d to detach the screen again
            See the screen man page for more details

"
exit 1

}

mkdir -p $SCRIPTS/logs

function verify-start {
    if ! screen -list | grep -q "$1";
    then
      echo "$1 failed to start. The log is below:"
      echo
      tail $SCRIPTS/logs/$1.log
      exit 1
    fi
}

function screen-script {
  SCREEN_NAME="$2"

  if [ "$1" == "log" ]; then

    SCREEN_FILE="$SCRIPTS/$SCREEN_NAME.screen"
    if [ ! -f "$SCREEN_FILE" ]; then
      echo "$(screen-config $SCREEN_NAME)" > "$SCREEN_FILE"
    fi

    args="$args -c $SCREEN_FILE"
  elif [ "$1" != "no-log" ]; then
    echo "Invalid argument $1"
    exit 1
  fi

  shift
  shift

  screen -mdS $SCREEN_NAME $args $@
  sleep 0.1
  verify-start $SCREEN_NAME
  echo "Started $SCREEN_NAME"
}

function start-mycroft-custom {
  name="mycroft-$1"
  shift
  screen-script log "$name" $@
}

function start-mycroft {

  start-mycroft-custom "$1" $DIR/start.sh $@
}

function start-mycroft-nolog {
  screen-script no-log "mycroft-$1" $DIR/start.sh $@
}

function start-mycroft-debug {
  $DIR/start.sh $@
}

function stop-screen {
  for i in $(screen -ls "$1"); do
    if echo $i | grep -q $1; then
      screen -XS $i quit && echo "Stopped $1" || echo "Could not stop $1"
    fi
  done
}

function stop-mycroft {
    stop-screen "mycroft-$1"
}

set -e

case "$1" in
"start")
  $0 stop
  start-mycroft service
  start-mycroft micro
  start-mycroft server
  start-mycroft skills

  case "$2" in
  "")
    start-mycroft hack
    start-mycroft fb
    start-mycroft webchat
    start-mycroft twitch
    ;;
  "-c"|"--cli")
    start-mycroft cli
    ;;
  "-w"|"--webchat")
    start-mycroft webchat
    ;;
  "-d"|"--debug")
    start-mycroft-debug cli
    ;;
  "-h"|"--hackchat")
    start-mycroft hack
    ;;
  "-fb"|"--facebook")
    start-mycroft fb
    ;;
  *)
    echo "Usage"
    usage-exit
    ;;
  esac
  ;;

"stop")
  if [[ -n "$2" ]]; then usage-exit; fi
  stop-mycroft service
  stop-mycroft skills
  stop-mycroft voice
  stop-mycroft cli
  stop-mycroft audio
  stop-mycroft fb
  stop-mycroft hack
  ;;

"restart")
  case "$2" in
  ""|"-v"|"--voice"|"-c"|"--cli"|"-d"|"--debug")
    $0 stop
    $0 start $2
    ;;
  *)
    usage-exit
    ;;
  esac
  ;;
*)
  usage-exit
  ;;
esac
