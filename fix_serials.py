# Description: Fixes the serial numbers in the README.md table to be in ascending order starting from 1.
# Usage: python fix_serials.py
# Requirement: Python 3.6+

import re


def fix_serials(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    in_table_body = False
    serial_num = 1

    for line in lines:
        # Identify the separator line to start re-numbering from the next line
        if "|---|---|---|---|---|---|---|" in line:
            new_lines.append(line)
            in_table_body = True
            continue

        if in_table_body:
            if line.strip().startswith("|"):
                # Data row: Replace the content of the first column with the current serial number
                match = re.match(r"^\|([^|]+)\|", line)
                if match:
                    new_line = "|" + str(serial_num) + "|" + line[match.end(1) + 1 :]
                    new_lines.append(new_line)
                    serial_num += 1
                else:
                    new_lines.append(line)
            elif line.strip() == "":
                # Keep empty lines within the table body
                new_lines.append(line)
            else:
                # End of table body detected (non-empty line not starting with '|')
                in_table_body = False
                new_lines.append(line)
        else:
            new_lines.append(line)

    with open(file_path, "w", encoding="utf-8", newline="") as f:
        f.writelines(new_lines)


if __name__ == "__main__":
    fix_serials("README.md")
    print("Serial numbers fixed in README.md")
