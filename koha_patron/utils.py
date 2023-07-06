import re

def trim_first_two_lines(file_name, string):
    with open(file_name, "r") as f:
        lines = f.readlines()
        # Check if the first line matches the string
        if re.match(string, lines[0]):
        # Remove the first two lines
            lines = lines[2:]

    with open(file_name, "w") as f:
        for line in lines:
            f.write(line)
