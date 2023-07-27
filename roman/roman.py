import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import os
import platform
from datetime import datetime
import shutil
from tkinter import simpledialog
from custom_commands import CustomCommandManager as ccm
import paramiko

class CommandConsole:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(False)
        self.root.title("roman.")
        self.root.geometry("800x600")
        self.root.bind("<B1-Motion>", self.move_window)  # Allow moving the window by dragging

        # Dark mode theme colors
        self.dark_bg = "#222222"
        self.dark_fg = "#0f8009"
        self.input_bg = "#333333"
        self.input_fg = "#0f8009"

        # Set the background color for the root window
        self.root.config(bg=self.dark_bg)

        # Create ccm instance
        self.command_manager = ccm()

        # Create a button to open the ccm window
        self.custom_commands_button = tk.Button(root, text="Custom Commands", command=self.open_custom_commands_window)
        self.custom_commands_button.pack(pady=5)

        # Create a scrolled text box to display the output
        self.output_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, bg=self.dark_bg, fg=self.dark_fg)
        self.output_box.pack(fill=tk.BOTH, expand=True)

        # Set MOTD
        self.display_motd()

        # Create the frame for the input bar
        self.input_frame = tk.Frame(root, bg=self.dark_bg)
        self.input_frame.pack(fill=tk.X)

        # Add the pre-text for command input
        self.input_pretext = tk.Label(self.input_frame, text="Enter command:", bg=self.dark_bg, fg=self.input_fg)
        self.input_pretext.pack(side=tk.LEFT, padx=5)

        # Create an entry widget for command input
        self.input_entry = tk.Entry(self.input_frame, bg=self.input_bg, fg=self.input_fg)
        self.input_entry.pack(fill=tk.X, padx=5, pady=2)
        self.input_entry.bind("<FocusIn>", self.clear_pretext)  # Remove pre-text when the entry is focused
        self.input_entry.bind("<FocusOut>", self.restore_pretext)  # Restore pre-text when the entry loses focus

        # Set focus to the input entry initially
        self.input_entry.focus()

        # Bind the Enter key to send the command
        self.input_entry.bind("<Return>", self.handle_command)

        # Disable the entry widget when the output box is in focus
        self.output_box.bind("<1>", self.disable_entry)
        self.output_box.bind("<Leave>", self.enable_entry)

        # Variable to hold the custom commands listbox
        self.custom_commands_listbox = None

    def open_custom_commands_window(self):
        # Create a new Toplevel window for managing custom commands
        custom_commands_window = tk.Toplevel(self.root)
        custom_commands_window.title("Custom Command Manager")

        # Create a listbox to display custom commands
        self.custom_commands_listbox = tk.Listbox(custom_commands_window, bg=self.dark_bg, fg=self.dark_fg)
        self.custom_commands_listbox.pack(fill=tk.BOTH, expand=True)

        # Populate the listbox with custom commands
        for command in self.command_manager.custom_commands.keys():
            self.custom_commands_listbox.insert(tk.END, command)

        # Create buttons for adding, editing, and removing custom commands
        add_button = tk.Button(custom_commands_window, text="Add", command=self.add_custom_command)
        add_button.pack(side=tk.LEFT, padx=5, pady=5)
        edit_button = tk.Button(custom_commands_window, text="Edit", command=self.edit_custom_command)
        edit_button.pack(side=tk.LEFT, padx=5, pady=5)
        remove_button = tk.Button(custom_commands_window, text="Remove", command=self.remove_custom_command)
        remove_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Set the minimum height of the custom command manager window
        min_height = custom_commands_window.winfo_reqheight()

        # Adjust the window height to fit the content
        new_height = min(min_height + 50, 500)  # Limit the maximum height to 500
        custom_commands_window.geometry(f"400x{new_height}")
        
    def create_command_manager_window(self):
        # Create a new window for managing custom commands
        self.command_manager_window = tk.Toplevel(self.root)
        self.command_manager_window.title("Custom Command Manager")

        # Create a listbox to display custom commands
        self.custom_commands_listbox = tk.Listbox(self.command_manager_window, bg=self.dark_bg, fg=self.dark_fg)
        self.custom_commands_listbox.pack(fill=tk.BOTH, expand=True)
        self.update_command_list()

        # Create buttons to add, edit, and remove custom commands
        self.add_button = tk.Button(self.command_manager_window, text="Add", command=self.add_custom_command)
        self.add_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.edit_button = tk.Button(self.command_manager_window, text="Edit", command=self.edit_custom_command)
        self.edit_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.remove_button = tk.Button(self.command_manager_window, text="Remove", command=self.remove_custom_command)
        self.remove_button.pack(side=tk.LEFT, padx=5, pady=5)

    def update_command_list(self):
         self.custom_commands_listbox.delete(0, tk.END)
         for command in self.command_manager.get_commands():
            self.custom_commands_listbox.insert(tk.END, command)

    def add_custom_command(self):
        name = simpledialog.askstring("Add Custom Command", "Enter the custom command name:")
        if name:
            action = simpledialog.askstring("Add Custom Command", "Enter the action:")
            if action:
                self.command_manager.add_command(name, action)
                self.update_command_list()  # Update the custom commands listbox
                self.command_manager.save_commands_to_json()  # Save the commands to the JSON file



    def edit_custom_command(self):
        selected_command = self.custom_commands_listbox.curselection()
        if selected_command:
            selected_command = self.custom_commands_listbox.get(selected_command[0])
            new_name = simpledialog.askstring("Edit Custom Command", "Enter the new name:", initialvalue=selected_command)
            if new_name:
                new_action = simpledialog.askstring("Edit Custom Command", "Enter the new action:")
                if new_action:
                    self.command_manager.remove_command(selected_command)
                    self.command_manager.add_command(new_name, new_action)

    def remove_custom_command(self):
        selected_command = self.custom_commands_listbox.curselection()
        if selected_command:
            selected_command = self.custom_commands_listbox.get(selected_command[0])
            self.command_manager.remove_command(selected_command)
            self.update_command_list()

    def handle_custom_command(self, command):
        action = self.command_manager.get_action(command)
        if action:
            try:
                # Evaluate the associated action as Python code
                eval(action)
            except Exception as e:
                print(f"Error executing custom command: {str(e)}")
        else:
            print("Invalid command.")


    def handle_command(self, event):
        command = self.input_entry.get()
        self.input_entry.delete(0, tk.END)

        # Process custom commands (if any)
        action = self.command_manager.get_action(command.lower())
        if action:
            try:
                # Evaluate the associated action as Python code
                eval(action)
            except Exception as e:
                print(f"Error executing custom command: {str(e)}")
        else:
            # Process other commands (same as before)
            output = self.process_command(command)

    def handle_custom_command(self, command):
        action = self.command_manager.get_action(command)
        if action:
            try:
                # Evaluate the associated action as Python code
                eval(action)
            except Exception as e:
                self.output_box.insert(tk.END, f"Error executing custom command: {str(e)}\n")
        else:
            self.output_box.insert(tk.END, "Invalid command.\n")

    def move_window(self, event):
        self.root.geometry(f"+{event.x_root}+{event.y_root}")

    def close_window(self):
        self.root.destroy()

    def execute_remote_command(self, host, username, password, command):
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(host, username=username, password=password)
            
            stdin, stdout, stderr = client.exec_command(command)
            output = stdout.read().decode()
            
            client.close()
            
            return output
        except paramiko.ssh_exception.AuthenticationException:
            return "Error: Authentication failed. Check your username and password."
        except paramiko.ssh_exception.SSHException:
            return "Error: Failed to establish an SSH connection to the remote host."
        except Exception as e:
            return f"Error: {str(e)}"

    def handle_command(self, event):
        command = self.input_entry.get()
        self.input_entry.delete(0, tk.END)

        # Process the command (you can extend this with your own functionality)
        output = self.process_command(command)

        # Display the output in the scrolled text box
        self.output_box.insert(tk.END, f">> {command}\n")
        self.output_box.insert(tk.END, f"{output}\n")
        self.output_box.see(tk.END)  # Scroll to the end to show the latest output

    def process_command(self, command):

        if command.lower().startswith("custom "):
            custom_command = command[7:].strip()
            action = self.command_manager.get_action(custom_command)
            if action:
                try:
                    # Evaluate the associated action as Python code
                    eval(action)
                    return f"Executed custom command: {custom_command}"
                except Exception as e:
                    return f"Error executing custom command: {str(e)}"
            else:
                return "Invalid custom command."
            
        if command.lower() == "hello":
            return "Hello, World!"
        elif command.lower() == "exit":
            self.root.destroy()  # Close the tkinter window when the user enters 'exit'
            return ""
        elif command.lower() == 'help':
            return '''

** C O M M A N D S **

hello           print hello world statment
exit            exit roman
help            print commands and their functions
custom          use a custom command [custom <custom command name>]
start           start a application [start <app name>]
kill            kill a proccess [kill <app name>]
echo            print a statment [echo <your statment>]
cd              change the current working directory [cd <directory>]
cwd             print current working directory
ls              list files in current working directory
mkdir           make a new directory
rm              remove a file or directory
py              start a python app [py <.py file>]
cp              copy a file or directory
mv              move a file or directory
rn              rename a file or directory 
cat             print contents of a file
date            print the current date and time.
time            measure the execution time of a command or script
ping            check the conectivityto a specific host or ip address
ipconfig        print network configuration details
cu              print the username of current user
cls             clear the output box
tasklist        print list of current running proccess
sysinf          print system information
remote          preform an action on a host [remote <host> <username> <password> <command>]
shutdown        shutdown or restart the computer

 #######################
## Custom Command Help ##
 #######################

What is a custom command?
    A custom command is a json varible that can be use as a command in roman.

Why custom commands?
    To give users more access to making commands than windows or powershell.

How do I make one?
    See that button that says "Custom Commands?" Press that and the control pops up!

What is..
    an action?
        An action is a line of python code that will be executed when the command is used.
    a name?
        The command name so it can be executed.

Will this be compatible with functions?
    I plan to do this in a later update
'''
        elif command.lower().startswith("start "):
            program = command[6:].strip()
            try:
                subprocess.Popen(program)
                return f"Started {program} successfully."
            except FileNotFoundError:
                 return f"Error: Program '{program}' not found or could not be executed."
            
        elif command.lower().startswith("kill "):
            app_name = command[5:].strip()
            try:
                os.system(f"taskkill /f /im {app_name}")
                return f"Terminated {app_name} successfully. (check cmd if this worked!)"
            except Exception as e:
                return f"Error: {str(e)}"
        
        elif command.lower().startswith("echo "):
            statement = command[5:].strip()
            return statement
        
        elif command.lower().startswith("cd "):
            new_directory = command[3:].strip()
            try:
                os.chdir(new_directory)
                return f"Changed working directory to: {os.getcwd()}"
            except FileNotFoundError:
                return f"Error: Directory '{new_directory}' not found."
            except Exception as e:
                return f"Error: {str(e)}"
        
        elif command.lower() == 'cwd':
            return os.getcwd()
            
        elif command.lower().startswith("py "):
            script_path = command[3:].strip()
            try:
                subprocess.Popen(["python", script_path])
                return f"Started Python script: {script_path}"
            except FileNotFoundError:
                return f"Error: Python interpreter not found or script '{script_path}' not found."
            
        elif command.lower() == 'ls':
            try:
                cwd = os.getcwd()
                items = os.listdir(cwd)
                return '\n'.join(items)
            except Exception as e:
                return f'Error: {str(e)}'
        
        elif command.lower().startswith('mkdir '):
            folder = command[6:].strip()
            try:
                os.mkdir(folder)
                return f'Created new directory: {folder}'
            except FileExistsError:
                return f'Error: Directory {folder} already exists.'
            except Exception as e:
                return f'Error: {str(e)}'

        elif command.lower().startswith('rm '):
            item = command[3:].strip()
            try:
                if os.path.isfile(item):
                    os.remove(item)
                    return f'Removed file: {item}'
                elif os.path.isdir(item):
                    os.rmdir(item)
                    return f'Removed directory: {item}'
                else:
                    return f'Error: {item} was not found.'
            except Exception as e:
                return f'Error: {str(e)}'
        elif command.lower().startswith('cp '):
            try:
                command_parts = command.split()
                if len(command_parts) != 3:
                    return "Error: Invalid usage. Usage: copy <source> <destination>"
                
                source = command_parts[1]
                destination = command_parts[2]
                shutil.copy(source, destination)
                return f"Copied '{source}' to '{destination}'"
            except Exception as e:
                return f"Error: {str(e)}"
            
        elif command.lower().startswith('mv '):
            try:
                command_parts = command.split()
                if len(command_parts) != 3:
                    return "Error: Invalid usage. Usage: move <source> <destination>"
                
                source = command_parts[1]
                destination = command_parts[2]
                shutil.move(source, destination)
                return f"Moved '{source}' to '{destination}'"
            except Exception as e:
                return f"Error: {str(e)}"
        
        elif command.lower().startswith('cat '):
            try:
                command_parts = command.split()
                if len(command_parts) != 2:
                    return "Error: Invalid usage. Usage: type <filename>"
                
                filename = command_parts[1]
                with open(filename, "r") as file:
                    content = file.read()
                return content
            except FileNotFoundError:
                return f"Error: File '{filename}' not found."
            except Exception as e:
                return f"Error: {str(e)}"
        
        elif command.lower() == 'date':
            now = datetime.now()
            return now.strftime('%Y-%m-%d %H:%M:%S')
        
        elif command.lower().startswith('ping '):
            try:
                command_parts = command.split()
                if len(command_parts) != 2:
                    return "Error: Invalid usage. Usage: ping <host_or_ip>"
                
                host = command_parts[1]
                result = subprocess.run(["ping", host], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                return result.stdout
            except Exception as e:
                return f"Error: {str(e)}"
            
        elif command.lower() == 'ipconfig':
            if platform.system().lower() == 'windows':
                command = 'ipconfig'
            else:
                command = 'ifconfig'
            result = subprocess.run([command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return result.stdout
        
        elif command.lower() == 'cu':
            result = subprocess.run(['whoami'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return result.stdout.strip()

        elif command.lower() == 'cls':
            self.output_box.delete(1.0, tk.END)
            return 'Console cleared.' #* This can change. add a '#' before the return.
        
        elif command.lower() == 'sysinf':
            result = subprocess.run(["systeminfo"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return result.stdout
        
        elif command.lower() == 'tasklist':
            result = subprocess.run(["tasklist"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return result.stdout
        
        elif command.lower() == 'shutdown':

            if platform.system().lower() == "windows":
                subprocess.run(["shutdown", "/s", "/t", "0"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                return "Shutting down the computer..."
            
            else:
                return "Shutdown command not supported on this platform."
            
        elif command.lower().startswith("remote "):
            try:
                # Parse the command for remote execution
                _, host, username, password, command_to_execute = command.split(maxsplit=4)
                
                # Call the execute_remote_command function to run the command remotely
                output = self.execute_remote_command(host, username, password, command_to_execute)
                return output
            except Exception as e:
                return f"Error: {str(e)}"

        #! all commands and custom commands end here. no further. ( if you want to manualy )
        else:
            return "Invalid command."

    def disable_entry(self, event):
        self.input_entry.config(state=tk.DISABLED)

    def enable_entry(self, event):
        self.input_entry.config(state=tk.NORMAL)

    def clear_pretext(self, event):
        # Remove pre-text when the entry is focused
        if self.input_entry.get() == "Enter command...":
            self.input_entry.delete(0, tk.END)

    def restore_pretext(self, event):
        # Restore pre-text when the entry loses focus and is empty
        if not self.input_entry.get():
            self.input_entry.insert(0, "Enter command...")
   
    def display_motd(self):
        motd = f'hello {os.getlogin()}, welcome to roman.\n\n' \
               f'this is very diffrent from your regular command prompt\n' \
               f'this is a wip.\n' \
               f'to get started, enter \'help\' into the command input bar to show a list of commands.\n\n'
        self.output_box.insert(tk.END, motd)



if __name__ == "__main__":
    root = tk.Tk()
    console = CommandConsole(root)

    # Set the dark mode theme for all tkinter widgets
    style = ttk.Style()
    style.theme_use('clam')
    style.configure(".", background=console.dark_bg, foreground=console.dark_fg)
    style.map("TEntry", fieldbackground=[("active", console.input_bg)])

    root.mainloop()
