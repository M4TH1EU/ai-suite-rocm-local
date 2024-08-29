import questionary
from questionary import Choice

from core.vars import loaded_services

start = None
start_service = None
stop_service = None
install_service = None
uninstall_service = None
are_you_sure = None
any_key = None
already_running = None


def update_choices():
    global start, start_service, stop_service, install_service, uninstall_service, are_you_sure, any_key, already_running

    start = questionary.select(
        "Choose an option:",
        choices=[
            Choice("Start service"),
            Choice("Stop service"),
            Choice("Install/update service"),
            Choice("Uninstall service"),
            Choice("exit")
        ])

    _services_choices = [Choice(service.name, value=service.id) for service in loaded_services.values()]
    _services_choices.append(Choice("go back", value="back"))

    start_service = questionary.select(
        "Select service to start:",
        choices=_services_choices
    )

    stop_service = questionary.select(
        "Select service to stop:",
        choices=_services_choices
    )

    install_service = questionary.select(
        "Select service to install/update:",
        choices=_services_choices
    )

    uninstall_service = questionary.select(
        "Select service to uninstall:",
        choices=_services_choices
    )

    are_you_sure = questionary.confirm("Are you sure?")

    already_running = questionary.confirm("Service is already running, do you want to restart it?")

    any_key = questionary.text("Press any key to continue")
