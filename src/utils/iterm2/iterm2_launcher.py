import iterm2

async def launch_iterm2_with_custom_title(connection):
    try:
        app = await iterm2.async_get_app(connection)
        new_window = await iterm2.Window.async_create(connection)
        if new_window:
            # Get the current session in the new window
            session = new_window.current_tab.current_session

            # Ensure the session is valid
            if session:
                await session.async_set_name("My Custom Title")
                print("Custom title set successfully")
                await new_window.async_activate()
                await app.async_activate()
            else:
                print("Session not found")
        else:
            print("New window could not be created")
    except Exception as e:
        print(f"An error occurred: {e}")

# iterm2.launch_iterm2_with_custom_title(main, retry=True)