import asyncio
import iterm2
import time
tab_titles = []

async def get_all_sessions(app):
    """
    Prints the titles of all windows, tabs, and sessions in the iTerm2 application.

    This function iterates over all windows, tabs, and sessions in the iTerm2 application
    and prints their titles.

    Parameters:
    app (iterm2.App): The iTerm2 application instance.
    """
    global tab_titles
    for window in app.windows:
        window_title = await window.async_get_variable("title")
        print("Window title: %s" % (window_title))
        for tab in window.tabs:
            tab_title = await tab.async_get_variable("title")
            print("\tTab title: %s" % (tab_title))
            tab_titles.append(tab_title)
            for session in tab.sessions:
                session_title = await session.async_get_variable("name")
                print("\t\tSession title: %s" % (session_title))

async def main_get_all_sessions(connection):
    app = await iterm2.async_get_app(connection)
    await get_all_sessions(app)


def get_iterm2_titles():
    global tab_titles
    iterm2.run_until_complete(main_get_all_sessions)
    tabtitles_copy = [i for i in tab_titles]
    tab_titles = []
    return tabtitles_copy
