import pathlib
import os

NAME_FORMAT = "%Y-%m-%d %H.%M.%S"


def check_file_name(old_path, new_path):
    if old_path != new_path:
        print(f'\033[34mUpdating file name\033[0m for file: {old_path}')
        print("Old name: " + os.path.basename(old_path))
        print("New name: " + os.path.basename(new_path))
        os.rename(old_path, new_path)


def get_formatted_name(path, date):
    formatted_name = date.strftime(NAME_FORMAT)

    if path.__contains__("-EFFECTS"):
        formatted_name = formatted_name + "-EFFECTS"
    if path.__contains__("-COLLAGE"):
        formatted_name = formatted_name + "-COLLAGE"
    if path.__contains__("-ANIMATION"):
        formatted_name = formatted_name + "-ANIMATION"
    if path.__contains__("-edited"):
        formatted_name = formatted_name + "-edited"

    new_name = check_name_available(path, formatted_name, 0)
    return new_name


def check_name_available(path, formatted_name, count):
    dir_name = os.path.dirname(path)
    extension = pathlib.Path(path).suffix
    new_name = formatted_name + ("" if count == 0 else f' {count:02d}') + extension
    new_path = os.path.join(dir_name, new_name)
    if new_path == path:
        return new_name
    if os.path.exists(new_path):
        # print(f"Path exist: {new_path}")
        return check_name_available(path, formatted_name, count + 1)
    else:
        return new_name
