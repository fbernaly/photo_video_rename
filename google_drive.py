from datetime import datetime
import pathlib
import dates
import exif
import name
import os

# local imports
import formats


def inspect_video(path):
    date = dates.get_video_creation_date_from_metadata(path)

    if date is None:
        date = os.path.getmtime(path)
        date = datetime.fromtimestamp(date)
        print(
            f'Patched \033[31mcreated_date\033[0m for \033[35mvideo\033[0m file: {path} with date: \033[32m{date}\033[0m')

    # to hardcode the time pass a timestamp in the next line
    # date = datetime.fromtimestamp(1454812080)

    extension = pathlib.Path(path).suffix
    if [".mov", ".MOV"].__contains__(extension):
        dates.check_file_dates(path, date, date)
        name.check_file_name(path, os.path.join(os.path.dirname(path), name.get_formatted_name(path, date)))
    elif [".3gp", ".mp4", ".MP4", ".m4v"].__contains__(extension):
        dates.check_file_dates(path, date, date)
        # delta = 3  # set time difference because SetFile uses local timezone
        # date = date + timedelta(hours=delta)
        name.check_file_name(path, os.path.join(os.path.dirname(path), name.get_formatted_name(path, date)))
    else:
        print(f'\033[31mVideo file not inspected: {path}, date: {date}\033[0m')
        exit(0)


def inspect_image(path):
    date = dates.get_image_creation_date_from_exif(path)
    if date is None:
        try:
            filename = os.path.basename(path)[0:19]
            date = datetime.strptime(filename, name.NAME_FORMAT)
            print(
                f'Patched \033[31mcreated_date\033[0m for \033[36mimage\033[0m file: {path} with date: \033[32m{date}\033[0m')
        except:
            print(f'Not able to parse \033[31mcreated_date\033[0m from image name for: {path}')
            date = os.path.getmtime(path)
            date = datetime.fromtimestamp(date)

    filename = os.path.basename(path)
    suggested_name = date.strftime(name.NAME_FORMAT)
    if filename.startswith(suggested_name) == 0:
        print(f"\033[34mNeed to check name for:\033[0m {path}")
        exif.print_exif_data(path)

    # delta = 3  # set time difference because SetFile uses local timezone
    # date = date - timedelta(hours=delta)
    dates.check_file_dates(path, date, date)
    name.check_file_name(path, os.path.join(os.path.dirname(path), name.get_formatted_name(path, date)))


def inspect_file(path):
    extension = pathlib.Path(path).suffix
    if formats.IMG_FORMATS.__contains__(extension):
        inspect_image(path)
    elif formats.VIDEO_FORMATS.__contains__(extension):
        inspect_video(path)
    else:
        print(f"Skipped file: \033[31m{path}\033[0m")
        exit(0)


def inspect_dir(dir):
    files = os.listdir(dir)
    files.sort()
    for file in files:
        path = os.path.join(dir, file)
        if os.path.isfile(path):
            inspect_file(path)
        else:
            inspect_dir(path)
