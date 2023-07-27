# Roman - A Custom Command Line Interface (CLI) in Python

Roman is a custom command-line interface (CLI) written in Python using the Tkinter library for the GUI. It provides users with a familiar command-line environment while offering additional functionalities and custom commands.


## Important!

if you REALLY wish to use Roman, please run `pip3 install -r requirements.txt` in your console so the libraries for Roman to run are downloaded.
## Features

- Basic command execution: Roman supports common command-line operations such as running applications, navigating directories, listing files, creating directories, removing files/directories, etc.

- Custom Commands: Users can define their own custom commands and associate them with specific actions. These custom commands are stored in a JSON file for persistence.

- Dark Mode Theme: Roman has a dark mode theme for the GUI, providing a sleek and modern appearance.

## Code Overview

### `roman.py`

This file contains the main implementation of the Roman CLI.

- **`CommandConsole` class**: This class is responsible for creating the main GUI window and handling user input and commands. It sets up the Tkinter window, creates the input and output widgets, and processes user commands.

- **`process_command` method**: This method processes the user-entered commands and handles built-in and custom commands. For custom commands, it calls the `handle_custom_command` method.

- **`handle_custom_command` method**: This method retrieves the action associated with a custom command from the `CustomCommandManager` instance and executes the action using the `eval` function.

### `custom_commands.py`

This file contains the `CustomCommandManager` class, which handles custom commands.

- **`CustomCommandManager` class**: This class manages custom commands and their associated actions. It provides methods to add, remove, edit, and retrieve custom commands. Custom commands are stored in a JSON file using the `json` module.

## How to Use Roman

1. Run the `roman.py` script using Python to start the Roman CLI.

2. The main window will open, showing the input and output areas.

3. You can enter commands in the input area and press Enter to execute them. The output will be displayed in the output area.

4. Roman supports various built-in commands like `ls`, `mkdir`, `rm`, `cd`, `py`, `echo`, `date`, `time`, `ping`, `ipconfig`, `whoami`, `cls`, `help`, etc. Type `help` to see a list of available commands and their descriptions.

5. To create a custom command, click the "Custom Commands" button. A new window will open, showing a list of existing custom commands (if any). You can add, edit, or remove custom commands using the respective buttons.

6. For adding a new custom command, enter the name and the action (Python code) associated with the command. The action will be executed when you run the custom command.

7. To execute a custom command, type `custom <command_name>` in the input area and press Enter.

8. The custom commands and their associated actions are stored in the `custom_commands.json` file.

## Note

- Roman is a work in progress and may have some limitations or bugs. Feel free to contribute and improve the CLI.

- Be cautious when using custom commands, as they execute arbitrary Python code. Make sure to review and validate the actions before adding them as custom commands.
