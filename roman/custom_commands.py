import json
import os

class CustomCommandManager:
    def __init__(self):
        self.json_file_path = "custom_commands.json"
        self.custom_commands = {}
        self.load_commands_from_json()

    def load_commands_from_json(self):
        try:
            with open(self.json_file_path, "r") as json_file:
                self.custom_commands = json.load(json_file)
        except FileNotFoundError:
            self.custom_commands = {}

    def save_commands_to_json(self):
        with open(self.json_file_path, "w") as json_file:
            json.dump(self.custom_commands, json_file, indent=4)

    def add_command(self, command, action):
        self.custom_commands[command] = action
        self.save_commands_to_json()  # Save the commands to the JSON file

    def remove_command(self, command):
        if command in self.custom_commands:
            del self.custom_commands[command]
            self.save_commands_to_json()  # Save the commands to the JSON file

    def get_action(self, command):
        return self.custom_commands.get(command, None)

    def get_commands(self):
        return list(self.custom_commands.keys())
