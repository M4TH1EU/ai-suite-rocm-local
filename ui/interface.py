import os

import questionary

from core.vars import loaded_services
from ui import choices
from ui.choices import update_choices


def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')


def handle_services(action, service):
    clear_terminal()

    if service == "back":
        return

    service = loaded_services[service]
    if action == "start":
        questionary.print(f"Starting {service.name} (127.0.0.1:{service.port})...")
        service.start()
    elif action == "stop":
        questionary.print(f"Stopping {service.name}...")
        service.stop()
    elif action == "install":
        confirmation = choices.are_you_sure.ask()
        if confirmation:
            questionary.print(f"Installing {service.name}...")
            service.install()
    elif action == "uninstall":
        confirmation = choices.are_you_sure.ask()
        if confirmation:
            type_confirmation = questionary.text(f"Please type {service.id} to confirm uninstallation (or type cancel):")

            value = type_confirmation.ask()

            if value == "cancel":
                questionary.print("Canceled", style="fg:ansired bold")
            elif value != service.id:
                questionary.print("Invalid input, please try again", style="fg:ansired bold")
            elif value == service.id:
                service.uninstall()

    choices.any_key.ask()


def run_interactive_cmd_ui():
    while True:
        clear_terminal()
        update_choices()
        choice = choices.start.ask()

        if choice == "Start service":
            service = choices.start_service.ask()
            handle_services("start", service)

        elif choice == "Stop service":
            service = choices.stop_service.ask()
            handle_services("stop", service)

        elif choice == "Install/update service":
            service = choices.install_service.ask()
            handle_services("install", service)

        elif choice == "Uninstall service":
            service = choices.uninstall_service.ask()
            handle_services("uninstall", service)

        elif choice == "exit":
            print("Exiting...")
            exit(0)
