#!/usr/bin/python3
"""Module for the entry point of the command interpreter."""

import cmd  # Import cmd module to create command-line interfaces
from models.base_model import BaseModel  # Import BaseModel from the models package
from models import storage  # Import storage object for managing data
import re  # Import regular expression module
import json  # Import JSON module for parsing and encoding


class HBNBCommand(cmd.Cmd):
    """Class for the command interpreter."""

    prompt = "(hbnb) "  # Define the command prompt

    def default(self, line):
        """Handle commands that do not match any command method."""
        self._precmd(line)  # Process the command line for custom syntax

    def _precmd(self, line):
        """Intercept commands to test for class.method() syntax."""
        match = re.search(r"^(\w*)\.(\w+)(?:\(([^)]*)\))$", line)  # Match class.method(args) pattern
        if not match:
            return line  # Return if no match
        classname = match.group(1)  # Extract class name
        method = match.group(2)  # Extract method name
        args = match.group(3)  # Extract arguments
        match_uid_and_args = re.search('^"([^"]*)"(?:, (.*))?$', args)  # Match UID and additional args
        if match_uid_and_args:
            uid = match_uid_and_args.group(1)  # Extract UID
            attr_or_dict = match_uid_and_args.group(2)  # Extract attributes or dictionary
        else:
            uid = args  # Set UID if no additional args
            attr_or_dict = False  # No attributes or dictionary

        attr_and_value = ""
        if method == "update" and attr_or_dict:
            match_dict = re.search('^({.*})$', attr_or_dict)  # Match dictionary pattern
            if match_dict:
                self.update_dict(classname, uid, match_dict.group(1))  # Update using dictionary
                return ""
            match_attr_and_value = re.search(
                '^(?:"([^"]*)")?(?:, (.*))?$', attr_or_dict)  # Match attribute and value
            if match_attr_and_value:
                attr_and_value = (match_attr_and_value.group(1) or "") + " " + (match_attr_and_value.group(2) or "")
        command = method + " " + classname + " " + uid + " " + attr_and_value  # Construct command
        self.onecmd(command)  # Execute command
        return command

    def update_dict(self, classname, uid, s_dict):
        """Helper method for update() with a dictionary."""
        s = s_dict.replace("'", '"')  # Replace single quotes with double quotes for JSON compatibility
        d = json.loads(s)  # Parse JSON string to dictionary
        if not classname:
            print("** class name missing **")
        elif classname not in storage.classes():
            print("** class doesn't exist **")
        elif uid is None:
            print("** instance id missing **")
        else:
            key = "{}.{}".format(classname, uid)  # Construct key
            if key not in storage.all():
                print("** no instance found **")
            else:
                attributes = storage.attributes()[classname]  # Get class attributes
                for attribute, value in d.items():  # Update attributes
                    if attribute in attributes:
                        value = attributes[attribute](value)  # Cast value to correct type
                    setattr(storage.all()[key], attribute, value)  # Set attribute
                storage.all()[key].save()  # Save changes

    def do_EOF(self, line):
        """Handle End Of File character to exit."""
        print()
        return True  # Exit the command loop

    def do_quit(self, line):
        """Exit the program."""
        return True  # Exit the command loop

    def emptyline(self):
        """Do nothing on empty input line."""
        pass

    def do_create(self, line):
        """Create an instance of a specified class."""
        if line == "" or line is None:
            print("** class name missing **")
        elif line not in storage.classes():
            print("** class doesn't exist **")
        else:
            b = storage.classes()[line]()  # Create a new instance
            b.save()  # Save the instance
            print(b.id)  # Print the instance ID

    def do_show(self, line):
        """Print the string representation of an instance."""
        if line == "" or line is None:
            print("** class name missing **")
        else:
            words = line.split(' ')  # Split the input line
            if words[0] not in storage.classes():
                print("** class doesn't exist **")
            elif len(words) < 2:
                print("** instance id missing **")
            else:
                key = "{}.{}".format(words[0], words[1])  # Construct key
                if key not in storage.all():
                    print("** no instance found **")
                else:
                    print(storage.all()[key])  # Print the instance

    def do_destroy(self, line):
        """Delete an instance based on class name and ID."""
        if line == "" or line is None:
            print("** class name missing **")
        else:
            words = line.split(' ')  # Split the input line
            if words[0] not in storage.classes():
                print("** class doesn't exist **")
            elif len(words) < 2:
                print("** instance id missing **")
            else:
                key = "{}.{}".format(words[0], words[1])  # Construct key
                if key not in storage.all():
                    print("** no instance found **")
                else:
                    del storage.all()[key]  # Delete the instance
                    storage.save()  # Save changes

    def do_all(self, line):
        """Print all string representations of all instances."""
        if line != "":
            words = line.split(' ')  # Split the input line
            if words[0] not in storage.classes():
                print("** class doesn't exist **")
            else:
                nl = [str(obj) for key, obj in storage.all().items()
                      if type(obj).__name__ == words[0]]  # Filter instances by class name
                print(nl)  # Print the instances
        else:
            new_list = [str(obj) for key, obj in storage.all().items()]  # Print all instances
            print(new_list)

    def do_count(self, line):
        """Count the instances of a specified class."""
        words = line.split(' ')
        if not words[0]:
            print("** class name missing **")
        elif words[0] not in storage.classes():
            print("** class doesn't exist **")
        else:
            matches = [
                k for k in storage.all() if k.startswith(
                    words[0] + '.')]  # Count instances of the class
            print(len(matches))  # Print the count

    def do_update(self, line):
        """Update an instance by adding or updating attributes."""
        if line == "" or line is None:
            print("** class name missing **")
            return

        rex = r'^(\S+)(?:\s(\S+)(?:\s(\S+)(?:\s((?:"[^"]*")|(?:(\S)+)))?)?)?'  # Regex to parse input
        match = re.search(rex, line)
        classname = match.group(1)
        uid = match.group(2)
        attribute = match.group(3)
        value = match.group(4)
        if not match:
            print("** class name missing **")
        elif classname not in storage.classes():
            print("** class doesn't exist **")
        elif uid is None:
            print("** instance id missing **")
        else:
            key = "{}.{}".format(classname, uid)  # Construct key
            if key not in storage.all():
                print("** no instance found **")
            elif not attribute:
                print("** attribute name missing **")
            elif not value:
                print("** value missing **")
            else:
                cast = None
                if not re.search('^".*"$', value):  # Check if value is not a string
                    if '.' in value:
                        cast = float  # Cast to float if contains a dot
                    else:
                        cast = int  # Cast to int otherwise
                else:
                    value = value.replace('"', '')  # Remove double quotes for string
                attributes = storage.attributes()[classname]  # Get class attributes
                if attribute in attributes:
                    value = attributes[attribute](value)  # Cast value to correct type
                elif cast:
                    try:
                        value = cast(value)  # Attempt to cast value
                    except ValueError:
                        pass  # Keep as string if casting fails
                setattr(storage.all()[key], attribute, value)  # Set attribute
                storage.all()[key].save()  # Save changes


if __name__ == '__main__':
    HBNBCommand().cmdloop()  # Start the command loop if the script is executed directly