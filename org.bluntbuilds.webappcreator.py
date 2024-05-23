#!/usr/bin/env python3

from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import os
from gi.repository import Gtk3
from pyxdg import DesktopEntry
from gi.repository import Gio
from plyvel import DesktopEntry


def create_web_app(url):
  # Parse URL and extract website name (optional for pre-filling entry)
  parsed_url = urlparse(url)
  website_name = parsed_url.netloc.split('.')[0]

  # Create a GTK window for user input
  window = Gtk.Window(title="Create Web App")

  # Grid layout for user input elements
  grid = Gtk.Grid()

  # Labels for user input
  url_label = Gtk.Label("URL:")
  browser_label = Gtk.Label("Browser:")
  launch_mode_label = Gtk.Label("Launch Mode:")
  shortcut_label = Gtk.Label("Install Shortcut:")
  gaming_mode_label = Gtk.Label("Create Gaming Mode Entry:")

  # URL entry (pre-filled with provided URL if available)
  url_entry = Gtk.Entry()
  url_entry.set_text(url)  # Pre-fill with the provided URL (optional)

  # Use application picker to select browser
  def choose_browser():
    app = Gio.AppInfo.get_default_for_type("text/html", False, Gio.AppLaunchContext())
    if not app:
      print("Failed to launch application picker!")
      return

     # Get chosen browser's desktop entry information
    info = app.get_all_launchers()[0].get_start_uri()

    # Parse chosen browser's Exec parameter
    exec_parts = Gio.DesktopAppInfo.new_from_uri(info).get_metadata("Exec")["value"].split()
    browser_exec = exec_parts[0]  # Assuming browser executable is the first part

    launch_mode = "fullscreen" if fullscreen_radio.get_active() else ("kiosk" if kiosk_radio.get_active() else "windowed")
    is_gaming_mode = gaming_mode_check.get_active()

    # Create DesktopEntry instances (one for regular, one for gaming mode if applicable)
    desktop_entry = DesktopEntry(version="1.0")
    gaming_desktop_entry = None  # Initialize for potential gaming mode

    # Set desktop entry attributes based on user choices and chosen browser
    desktop_entry.Name = f"{website_name} Web App"
    desktop_entry.Exec = [browser_exec, url]  # Adjust for launch mode arguments if needed
    if launch_mode != "windowed":
      desktop_entry.Exec.append(launch_mode)  # Add launch mode flag (fullscreen/kiosk)
    if is_gaming_mode and (browser_exec.lower().endswith("chrome") or browser_exec.lower().endswith("chromium")):
      desktop_entry.Exec.append("--app")  # Add "--app" flag for Chrome/Chromium gaming mode (optional)
    desktop_entry.Icon = os.path.abspath(f"{website_name}.ico")  # Use absolute path for icon
    desktop_entry.Type = "Application"
    desktop_entry.Categories = ["Web"]

    # Create gaming mode desktop entry if selected and Chrome/Chromium based browser
    if is_gaming_mode:
      gaming_desktop_entry = DesktopEntry(version="1.0")
      gaming_desktop_entry.Name = f"{website_name} Web App (Gaming Mode)"
      gaming_desktop_entry.Exec = [browser_exec, url]  # Use "--start-fullscreen" for Chrome/Chromium later
      if browser_exec.lower().endswith("chrome") or browser_exec.lower().endswith("chromium"):
        gaming_desktop_entry.Exec.append("--start-fullscreen")  # Use --start-fullscreen for Chrome/Chromium in gaming mode
      else:
        gaming_desktop_entry.Exec.append("--kiosk")  # Use --kiosk for other browsers in gaming mode
      gaming_desktop_entry.Icon = desktop_entry.Icon  # Use same icon
      gaming_desktop_entry.Type = "Application"
      gaming_desktop_entry.Categories = desktop_entry.Categories

    # Save the desktop entries using pyxdg (KDE specific locations)
    desktop_entry.save(os.path.join(os.getenv("HOME"), ".local", "share", "applications", f"{website_name}.desktop"), sync=True)
    if gaming_desktop_entry:
      gaming_desktop_entry.save(os.path.join(os.getenv("HOME"), ".local", "share", "applications", f"{website_name}_gaming_mode.desktop"), sync=True)

    # Save a copy to Desktop directory (optional for KDE)
    desktop_entry.save

  # Browser selection using application picker
  browser_combo = Gtk.Button()  # Use button to trigger application picker
  browser_combo.set_label("Select Browser")
  browser_combo.connect("clicked", lambda btn: set_browser_exec(btn))
  browser_exec = None  # Variable to store chosen browser's Exec

  def set_browser_exec(button):
    chosen_exec = choose_browser()
    if chosen_exec:
      global browser_exec  # Update global variable
      browser_combo.set_label(f"Selected: {chosen_exec}")  # Display selected browser
      browser_exec = chosen_exec

  # Radio buttons for launch mode selection
  launch_mode_box = Gtk.VBox()
  fullscreen_radio = Gtk.RadioButton(label="Fullscreen")
  kiosk_radio = Gtk.RadioButton(label="Kiosk")
  windowed_radio = Gtk.RadioButton(label="Windowed")
  launch_mode_box.pack_start(fullscreen_radio, True, True, 0)
  launch_mode_box.pack_start(kiosk_radio, True, True, 0)
  launch_mode_box.pack_start(windowed_radio, True, True, 0)

  # Check buttons for desktop and gaming mode shortcut creation
  shortcut_check = Gtk.CheckButton(label="Desktop")
  gaming_mode_check = Gtk.CheckButton(label="Gaming Mode")

  # Connect signals for custom browser path
  def on_browser_combo_changed(combo):
    if combo.get_active_text() == "Custom Path":
      custom_browser_entry.set_sensitive(True)
    else:
      custom_browser_entry.set_sensitive(False)

  browser_combo.connect("changed", on_browser_combo_changed)

  # Add UI elements to the grid with appropriate attachments
  grid.attach(url_label, 0, 0, 1, 1)
  grid.attach(url_entry, 1, 0, 2, 1)
  grid.attach(browser_label, 0, 1, 1, 1)
  grid.attach(browser_combo, 1, 1, 1, 1)
  grid.attach(custom_browser_entry, 2, 1, 1, 1)
  grid.attach(launch_mode_label, 0, 2, 1, 1)
  grid.attach(launch_mode_box, 1, 2, 2, 1)
  grid.attach(shortcut_label, 0, 3, 1, 1)
  grid.attach(desktop_shortcut_check, 1, 3, 1, 1)
  grid.attach(gaming_mode_label, 0, 4, 1, 1)
  grid.attach(gaming_mode_check, 1, 4, 1, 1)

  # Define a function to build the desktop entry based on user choices
  def build_desktop_entry():
    # Use application picker to get chosen browser
    app = Gio.AppInfo.get_default_for_type("text/html", False, Gio.AppLaunchContext())
    if not app:
      print("Failed to launch application picker!")
      return

    # Get chosen browser's desktop entry information
    info = app.get_all_launchers()[0].get_start_uri()

    # Parse chosen browser's Exec parameter
    exec_parts = Gio.DesktopAppInfo.new_from_uri(info).get_metadata("Exec")["value"].split()
    browser_exec = exec_parts[0]  # Assuming browser executable is the first part

    launch_mode = "fullscreen" if fullscreen_radio.get_active() else ("kiosk" if kiosk_radio.get_active() else "windowed")
    is_gaming_mode = gaming_mode_check.get_active()

    # Create a DesktopEntry instance
    desktop_entry = DesktopEntry(version="1.0")

    # Set desktop entry attributes based on user choices and chosen browser
    desktop_entry.Name = f"{website_name} Web App"
    desktop_entry.Exec = [browser_exec, url]  # Adjust for launch mode arguments if needed
    if is_gaming_mode and browser_exec.lower().endswith("chrome") or browser_exec.lower().endswith("chromium"):
      desktop_entry.Exec.append("--app")  # Add "--app" flag for Chrome/Chromium gaming mode (optional)
    desktop_entry.Icon = os.path.abspath(f"{website_name}.ico")  # Use absolute path for icon
    desktop_entry.Type = "Application"
    desktop_entry.Categories = ["Web"]

    # Save desktop entries using pyxdg (standard locations)
    desktop_entry.save(os.path.join(os.getenv("HOME"), ".local", "share", "applications", f"{website_name}.desktop"), sync=True)
    if gaming_desktop_entry:
      gaming_desktop_entry.save(os.path.join(os.getenv("HOME"), ".local", "share", "applications", f"{website_name}_gaming_mode.desktop"), sync=True)

    # Save a copy to Desktop directory (optional for KDE)
    if desktop_shortcut_check.get_active():
      # Check for write permissions to Desktop directory
      if not os.access("/desktop", os.W_OK):
        dialog = Gtk.MessageDialog(parent=window, type=Gtk.MessageType.WARNING,
                                   buttons=Gtk.ButtonsType.OK,
                                   message_format="This script requires write permissions to your Desktop directory.\n"
                                                   "Would you like to run it with elevated privileges (using sudo)?")
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.OK:
          # Relaunch script with sudo (replace 'your_script.py' with the actual script name)
          os.system('gksu "python3 your_script.py"')
          return  # Exit the function to avoid redundant saving attempts

      try:
        from gi.repository import KIO  # Import KIO for file operations
        # Construct desktop entry paths with user selection
        desktop_path = f"local:///desktop/{website_name}.desktop"
        gaming_desktop_path = (
            f"local:///desktop/{website_name}_gaming_mode.desktop"
            if gaming_desktop_entry
            else None
        )

        # Save desktop entry using KIO.put (consider error handling)
        KIO.put(desktop_path, desktop_entry.save_as_string(), False, -1, None)
        if gaming_desktop_path:
          KIO.put(gaming_desktop_path, gaming_desktop_entry.save_as_string(), False, -1, None)
        print("Desktop entries created successfully!")
      except ImportError:
        print("KIO module not found. Desktop shortcuts creation failed.")
      except Exception as e:
        print(f"Error saving desktop entries: {e}")

    # Close the window after successful creation
    window.destroy()

  # Create a button to trigger desktop entry building
  create_button = Gtk.Button(label="Create Web App")
  create_button.connect("clicked", build_desktop_entry)

  # Add the grid to the window
  window.add(grid)

  # Add the button to the grid (spanning two columns in the last row)
  grid.attach(create_button, 0, 5, 3, 1)

  # Show the window
  window.show_all()

  # Main loop to handle user interaction
  Gtk.main()
