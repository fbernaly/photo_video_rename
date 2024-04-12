from datetime import timedelta, datetime, timezone
import pathlib
import json
import os

# local imports
import formats
import dates
import name


def _read_json_data(path):
    f = open(path)
    data = json.load(f)
    f.close()
    return data


def _copy_json_data(path, new_path):
    data = _read_json_data(path)
    _save_json_data(data, new_path)
    return data


def _save_json_data(data, path):
    json_object = json.dumps(data, indent=2)
    with open(path, "w") as outfile:
        outfile.write(json_object)


def _relocate_file(path):
    new_path = path.replace("/sandbox/", "/temp/")
    if new_path == path:
        return
    new_dir = os.path.dirname(new_path)
    if os.path.exists(new_dir) == 0:
        os.mkdir(new_dir)
    if os.path.exists(new_path) == 0:
        # print(f"Moved: {new_path}")
        os.rename(path, new_path)
    else:
        print(f"Cannot move: {new_path}")


def combine_takeout_dir(dir, dest):
    files = os.listdir(dir)
    files.sort()
    for file in files:
        path = os.path.join(dir, file)
        if os.path.isfile(path):
            filename = os.path.basename(path)
            folder = os.path.basename(os.path.dirname(path))
            new_dir = os.path.join(dest, folder)
            new_path = os.path.join(new_dir, filename)

            if os.path.exists(new_dir) == 0:
                os.mkdir(new_dir)

            if os.path.exists(new_path) == 0:
                # print(f"Moved: {new_path}")
                os.rename(path, new_path)
            else:
                print(f"Cannot move: {path}")
        else:
            combine_takeout_dir(path, dest)


def _compare_dates(file_path, file_date, json_path, json_date):
    # get delta time
    if file_date.timestamp() > json_date.timestamp():
        delta = file_date.timestamp() - json_date.timestamp()
        first = json_date
    else:
        delta = json_date.timestamp() - file_date.timestamp()
        first = file_date
    try:
        delta = timedelta(seconds=delta)
    except:
        print(f"too long: {json_date} {file_date} {delta}")
        exit(0)

    if first == json_date:
        return json_date
    else:  # first == file_date:
        if delta.days > 30:
            return json_date

    # who_is_first = 'json_date' if first == json_date else 'file_date'
    # print(
    #     f"Difference: \033[31m{file_path}\033[0m, json_date: \033[33m{json_date}\033[0m {json_date.timestamp()} file_date: \033[33m{file_date}\033[0m {file_date.timestamp()}, first: \033[31m{delta}\033[0m [{who_is_first}]")

    return json_date


def _update_json_title(json_path, filename):
    # read json data
    data = _read_json_data(json_path)

    # replace title with filename
    data['title'] = filename

    # save json file
    _save_json_data(data, json_path)


def _create_json(path, title, date):
    timestamp = int(date.timestamp())
    formatted = f"{datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()} UTC"
    geo = {
        "latitude": 0.0,
        "longitude": 0.0,
        "altitude": 0.0,
        "latitudeSpan": 0.0,
        "longitudeSpan": 0.0
    }
    data = {
        "title": title,
        "creationTime": {
            "timestamp": f"{timestamp}",
            "formatted": formatted,
        },
        "photoTakenTime": {
            "timestamp": f"{timestamp}",
            "formatted": formatted,
        },
        "geoData": geo,
        "geoDataExif": geo,
    }
    _save_json_data(data, path)


def inspect_json_file(json_path, check_date, check_name, relocate):
    dir_name = os.path.dirname(json_path)

    # check if the json name ends with () and fix name
    if json_path.endswith(").json"):
        for i in range(30):
            version = f"({i})"
            if json_path.endswith(version + ".json"):
                temp_file = os.path.basename(json_path).replace(".json", "").replace(version, "")
                extension = pathlib.Path(temp_file).suffix

                wrong_json_path = json_path
                temp_file = temp_file.replace(extension, "") + version + extension
                json_path = os.path.join(dir_name, temp_file + ".json")
                os.rename(wrong_json_path, json_path)
                _update_json_title(json_path, temp_file)

    # read json data
    data = _read_json_data(json_path)

    # check that title field in json is the same as file name
    title = data['title']
    file = os.path.basename(json_path).replace(".json", "")
    if title != file:
        # update json name to correct one
        wrong_json_path = json_path
        json_path = os.path.join(dir_name, title + ".json")
        if os.path.exists(json_path) == 0:
            os.rename(wrong_json_path, json_path)
        else:
            print(f"\033[31m>E:\033[0m Not a match: {title} != {file}, path: {json_path}")
            return

    file_path = os.path.join(dir_name, file)
    extension = pathlib.Path(file_path).suffix

    # check that file exists
    if os.path.exists(file_path) == 0:
        # check if file name is incomplete
        f = file.replace(extension, "")
        for l in range(1, len(f)):
            wrong_file_path = os.path.join(dir_name, f[0:len(f) - l] + extension)
            if os.path.exists(wrong_file_path):
                os.rename(wrong_file_path, file_path)
                break
        if os.path.exists(file_path) == 0:
            print(f"\033[31m>E:\033[0m File not found: {file_path} for {json_path}")
            return

    json_date = dates.get_taken_date_from_json(json_path)
    if json_date is None:
        print(f"No photoTakenTime in: \033[31m{json_path}\033[0m")
        exit(0)

    if formats.IMG_FORMATS.__contains__(extension):
        file_date = dates.get_image_creation_date_from_exif(file_path)
    elif formats.VIDEO_FORMATS.__contains__(extension):
        file_date = dates.get_video_creation_date_from_metadata(file_path)
    else:
        print(f"Skipped file: \033[31m{file_path}\033[0m")
        exit(0)

    # replace file_date with json_date
    if file_date is None:
        # print(
        #     f"File does not have created_date, patched with json_date: \033[33m{json_date}\033[0m, file: \033[31m{file_path}\033[0m")
        file_date = json_date

    # replace file_date with comparison
    if file_date.timestamp() != json_date.timestamp():
        file_date = _compare_dates(file_path, file_date, json_path, json_date)

    # update file names
    if check_name:
        # get new_name
        new_name = name.get_formatted_name(file_path, file_date)

        # update file name
        new_file_path = os.path.join(dir_name, new_name)
        name.check_file_name(file_path, new_file_path)

        # update file name in json metadata
        if data['title'] != new_name:
            data['title'] = new_name
            _save_json_data(data, json_path)

        # update json name
        new_json_path = new_file_path + ".json"
        name.check_file_name(json_path, new_json_path)

        file_path = new_file_path
        json_path = new_json_path

    # update file dates
    if check_date:
        dates.check_file_dates(file_path, file_date, file_date)
        dates.check_file_dates(json_path, file_date, file_date)

    if relocate:
        _relocate_file(file_path)
        _relocate_file(json_path)


def inspect_image_file(path, check_date, check_name, relocate):
    json_path = path + ".json"
    # inspect only if there is no companion json file
    if os.path.exists(json_path):
        return

    file_date = None
    filename = os.path.basename(path)
    # check if this is an edited image
    if path.__contains__("-edited"):
        proxy_json_path = path.replace("-edited", "") + ".json"
        # check if proxy json exists then copy it
        if os.path.exists(proxy_json_path):
            # copy json file
            _copy_json_data(proxy_json_path, json_path)
            # get file_date from proxy json file
            file_date = dates.get_taken_date_from_json(json_path)
            # update new json with correct filename
            _update_json_title(json_path, filename)

    extension = pathlib.Path(path).suffix
    if file_date is None:
        for i in range(30):
            version = f"({i})"
            if filename.endswith(version + extension):
                dir_name = os.path.dirname(path)
                wrong_json_path = os.path.join(dir_name, filename.replace(version, "") + version + ".json")
                if os.path.exists(wrong_json_path):
                    os.rename(wrong_json_path, json_path)
                    # get file_date from renamed json file
                    file_date = dates.get_taken_date_from_json(json_path)
                    # update new json with correct filename
                    _update_json_title(json_path, filename)
                    continue

    if file_date is None:
        wrong_json_path = json_path.replace(extension, "")
        if os.path.exists(wrong_json_path):
            os.rename(wrong_json_path, json_path)
            # get file_date from renamed json file
            file_date = dates.get_taken_date_from_json(json_path)
            # update new json with correct filename
            _update_json_title(json_path, filename)

    if file_date is None:
        wrong_json_path = json_path.replace(extension, ".j")
        if os.path.exists(wrong_json_path):
            os.rename(wrong_json_path, json_path)
            # get file_date from renamed json file
            file_date = dates.get_taken_date_from_json(json_path)
            # update new json with correct filename
            _update_json_title(json_path, filename)

    # try to get file_date from exif
    if file_date is None:
        file_date = dates.get_image_creation_date_from_exif(path)

    if file_date is None:
        print(
            f"\033[31m>E:\033[0m Image file does not have a companion json file: \033[31m{path}\033[0m and file_date is {file_date}")
        return

    _create_json(json_path, os.path.basename(path), file_date)
    inspect_json_file(json_path, check_date, check_name, relocate)


def inspect_video_file(path, check_date, check_name, relocate):
    json_path = path + ".json"

    # inspect only if there is no companion json file
    if os.path.exists(json_path) == 0:
        # try to get file_date from file metadata
        file_date = dates.get_video_creation_date_from_metadata(path)

        # hardcoded
        if path == "../../Downloads/backup/sandbox/Photos from 2022/IMG_8645.MP4":
            file_date = datetime.fromtimestamp(1648344029)

        if file_date is None:
            print(
                f"\033[31m>E:\033[0m Video file does not have a companion json file: \033[31m{path}\033[0m and file_date is {file_date}")
            return

        _create_json(json_path, os.path.basename(path), file_date)
        inspect_json_file(json_path, check_date, check_name, relocate)


def inspect_jsons(dir, check_date, check_name, relocate):
    files = os.listdir(dir)
    files.sort()
    if len(files) == 0:
        os.rmdir(dir)
        return
    for file in files:
        path = os.path.join(dir, file)
        if os.path.exists(path) == 0:
            continue
        if os.path.isfile(path):
            extension = pathlib.Path(path).suffix.lower()
            if extension == ".json":
                inspect_json_file(path, check_date, check_name, relocate)
            elif formats.IMG_FORMATS.__contains__(extension):
                inspect_image_file(path, check_date, check_name, relocate)
            elif formats.VIDEO_FORMATS.__contains__(extension):
                inspect_video_file(path, check_date, check_name, relocate)
        else:
            inspect_jsons(path, check_date, check_name, relocate)
