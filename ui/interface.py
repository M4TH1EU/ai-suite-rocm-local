import os

import questionary

from core.vars import logger, loaded_services
from ui import choices


def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')


def handle_services(action, service):
    clear_terminal()

    if service == "back":
        return

    service = loaded_services[service]
    if action == "start":
        logger.info(f"Starting service: {service.name}")
        service.start()
    elif action == "stop":
        logger.info(f"Stopping service: {service.name}")
        service.stop()
    elif action == "update":
        confirmation = choices.are_you_sure.ask()
        if confirmation:
            logger.info(f"Installing/updating service: {service.name}")
            service.update()
    elif action == "uninstall":
        confirmation = choices.are_you_sure.ask()
        if confirmation:
            type_confirmation = questionary.text(f"Please type {service.id} to confirm uninstallation:")
            if type_confirmation.ask() == service.id:
                logger.info(f"Uninstalling service: {service.name}")
                service.uninstall()

    choices.any_key.ask()


def run_interactive_cmd_ui():
    while True:
        clear_terminal()
        choice = choices.start.ask()

        if choice == "Start service":
            service = choices.start_service.ask()
            handle_services("start", service)

        elif choice == "Stop service":
            service = choices.stop_service.ask()
            handle_services("stop", service)

        elif choice == "Install/update service":
            service = choices.install_service.ask()
            handle_services("update", service)

        elif choice == "Uninstall service":
            service = choices.uninstall_service.ask()
            handle_services("uninstall", service)

        elif choice == "Exit":
            print("Exiting...")
            exit(0)
