import asyncio
import iterm2

# Color presets to use
LIGHT_PRESET_NAME = "Light Background"
DARK_PRESET_NAME = "Dark Background"
PROFILES = ["Default"]

async def set_colors(connection, preset_name):
    print("Change to preset {}".format(preset_name))
    preset = await iterm2.ColorPreset.async_get(connection, preset_name)
    for partial in (await iterm2.PartialProfile.async_query(connection)):
        if partial.name in PROFILES:
            await partial.async_set_color_preset(preset)

async def launch_iterm2_with_custom_title(connection):
    try:
        app = await iterm2.async_get_app(connection)
        new_window = await iterm2.Window.async_create(connection)
        if new_window:
            # Get the current session in the new window
            session1 = new_window.current_tab.current_session

            # Ensure the session is valid
            if session1:
                await session1.async_set_name("My Custom Title")
                print("Custom title for session1 set successfully")
                
                # Split the tab vertically
                session2 = await session1.async_split_pane(vertical=True)
                
                if session2:
                    await session2.async_set_name("My Custom Title2")
                    print("Custom title for session2 set successfully")

                    await set_colors(connection, LIGHT_PRESET_NAME)
                    await asyncio.sleep(1)

                # Bring the new window to the front
                await new_window.async_activate()
                # Activate the iTerm2 application
                await app.async_activate()
            else:
                print("Session1 not found")
        else:
            print("New window could not be created")
    except Exception as e:
        print(f"An error occurred: {e}")

def launch_iterm2():
    iterm2.run_until_complete(launch_iterm2_with_custom_title, retry=True)