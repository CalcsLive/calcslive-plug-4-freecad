"""
CalcsLive init tools - Following Draft workbench pattern

Provides functions and lists of commands to set up CalcsLive menus and toolbars.
"""


def get_calcslive_commands():
    """Return the CalcsLive commands list"""
    return [
        "CalcsLive_Connect",
        "CalcsLive_Dashboard",
        "CalcsLive_ExtractParams",
        "CalcsLive_SyncToCalcsLive",
        "CalcsLive_PullFromCalcsLive",
        "CalcsLive_Status"
    ]


def init_toolbar(workbench, toolbar, cmd_list):
    """Initialize a toolbar (following Draft pattern)

    Parameters
    ----------
    workbench: Gui.Workbench
        The workbench. The commands from cmd_list must be available.

    toolbar: string
        The name of the toolbar.

    cmd_list: list of strings
        List of command names to add to toolbar.
    """
    for cmd in cmd_list:
        workbench.appendToolbar(toolbar, [cmd])


def init_menu(workbench, menu_list, cmd_list):
    """Initialize a menu (following Draft pattern)

    Parameters
    ----------
    workbench: Gui.Workbench
        The workbench. The commands from cmd_list must be available.

    menu_list: list of strings
        The name of the menu.

    cmd_list: list of strings
        List of command names to add to menu.
    """
    for cmd in cmd_list:
        workbench.appendMenu(menu_list, [cmd])