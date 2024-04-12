import os


def declutter_dir(dir):
    if os.path.exists(dir) == 0:
        return
    files = os.listdir(dir)
    files.sort()
    if len(files) == 0:
        os.rmdir(dir)
        return
    for file in files:
        path = os.path.join(dir, file)
        if os.path.isfile(path):
            if (file.__contains__("DS_Store")
                    or file == "metadata.json"
                    or file == "print-subscriptions.json"
                    or file == "shared_album_comments.json"
                    or file == "user-generated-memory-titles.json"):
                print(f"\033[31mDeleting\033[0m file: \033[31m{path}\033[0m")
                os.remove(path)
        else:
            declutter_dir(path)


def arrange_files_in_year_folders(dir, dest):
    if os.path.exists(dir) == 0:
        return
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
            dir_dest = os.path.basename(path)[0:4]
            dir_dest = os.path.join(dest, dir_dest)
            if os.path.exists(dir_dest) == 0:
                os.mkdir(dir_dest)
            new_path = os.path.join(dir_dest, file)
            if os.path.exists(new_path) == 0:
                os.rename(path, new_path)
            else:
                print(f"Cannot move: {path}")
        else:
            arrange_files_in_year_folders(path, dest)


def arrange_files_in_day_folders(dir):
    files = os.listdir(dir)
    files.sort()
    for file in files:
        path = os.path.join(dir, file)
        if os.path.isfile(path):
            dir_dest = os.path.basename(path)[0:10]
            dir_dest = os.path.join(dir, dir_dest)
            if os.path.exists(dir_dest) == 0:
                os.mkdir(dir_dest)
            new_path = os.path.join(dir_dest, file)
            if os.path.exists(new_path) == 0:
                print(f"Moved: {new_path}")
                os.rename(path, new_path)
