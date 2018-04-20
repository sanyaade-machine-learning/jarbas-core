from mycroft.msm.py_msm import JarbasSkillsManager


if __name__ == "__main__":
    from mycroft.messagebus.client.ws import WebsocketClient
    from threading import Thread
    import argparse
    from time import sleep
    from sys import exit

    ws = WebsocketClient()

    def connect():
        ws.run_forever()

    ws_thread = Thread(target=connect)
    ws_thread.setDaemon(True)
    ws_thread.start()

    parser = argparse.ArgumentParser()
    parser.add_argument("option", help="action to take, defaults to install default skills, list to list available skills, install {url_or_name} to install a skill")
    parser.add_argument("skill", help="skill to install", action="store_true")
    args = parser.parse_args()
    option = args.option

    while not ws.started_running:
        print "waiting for websocket connection..."
        sleep(2)

    msm = JarbasSkillsManager(emitter=ws)

    if option in ["defaults"]:
        msm.install_defaults()
        exit(0)
    elif option in ["list"]:
        msm.list_skills()
        exit(0)
    elif option in ["install"]:
        if args.skill:
            if args.skill.startswith("http"):
                msm.install_by_url(args.skill)
            else:
                msm.install_by_name(args.skill)
            exit(0)
        print "bad skill name"
        exit(666)
    ws_thread.join(0)
    exit(5373)
