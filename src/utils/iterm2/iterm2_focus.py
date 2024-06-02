import asyncio
import iterm2
import time
from AppKit import NSWorkspace, NSRunningApplication
from functools import partial

def focus_iterm2():
    """
    Brings iTerm2 application to the foreground using AppKit.

    This function iterates over the running applications and activates iTerm2 if it is found.
    """
    ws = NSWorkspace.sharedWorkspace()
    apps = ws.runningApplications()
    for app in apps:
        if app.localizedName() == "iTerm2":
            app.activateWithOptions_(1 << 1)
            break

async def focus_on_specific_session(connection, target_window_title, target_tab_title, target_session_title):
    """
    Focuses on a specific session in iTerm2.

    This function navigates through the iTerm2 application structure to focus on the specified
    window, tab, and session based on their titles.

    Parameters:
    connection (iterm2.Connection): The connection to the iTerm2 application.
    target_window_title (str or None): The title of the target window. Use None if the window title is None.
    target_tab_title (str): The title of the target tab.
    target_session_title (str): The title of the target session.
    """
    app = await iterm2.async_get_app(connection)
    for window in app.windows:
        window_title = await window.async_get_variable("title")
        if window_title == target_window_title or (target_window_title is None and window_title is None):
            # Focus on the window
            await window.async_activate()  
            for tab in window.tabs:
                tab_title = await tab.async_get_variable("title")
                if tab_title == target_tab_title:
                    # Focus on the tab
                    await tab.async_select()  
                    for session in tab.sessions:
                        session_title = await session.async_get_variable("name")
                        if session_title == target_session_title:
                            # Focus on the session
                            await session.async_activate()
                            print(f"Focused on window: {window_title}, tab: {tab_title}, session: {session_title}")
                            return

async def focus_context(connection, target_window_title, target_tab_title, target_session_title):
    """
    Main function to initiate focusing on the specified iTerm2 session and ensure iTerm2 stays in front.

    This function specifies the titles of the target window, tab, and session and calls the function to focus
    on the specific session. It also ensures iTerm2 is brought to the foreground again after focusing.

    Parameters:
    connection (iterm2.Connection): The connection to the iTerm2 application.
    target_window_title (str or None): The title of the target window. Use None if the window title is None.
    target_tab_title (str): The title of the target tab.
    target_session_title (str): The title of the target session.
    """
    await focus_on_specific_session(connection, target_window_title, target_tab_title, target_session_title)
    
    # Ensure iTerm2 is brought to the foreground
    focus_iterm2()

def focus_iterm2_run(target_window_title = None, target_tab_title = "My Custom Title (zsh)", target_session_title = "My Custom Title (zsh)"):
    time.sleep(2)
    iterm2.run_until_complete(partial(focus_context, target_window_title=target_window_title, \
        target_tab_title=target_tab_title, target_session_title=target_session_title))

