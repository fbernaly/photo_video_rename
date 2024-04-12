from pillow_heif import register_heif_opener

# local imports
import google_takeout
import google_drive
import compare
import files

register_heif_opener()

dir = "../../Downloads/backup/"

files.declutter_dir(dir)

# google_drive.inspect_dir(dir)
# google_drive.arrange_files_in_day_folders(dir)

# google_takeout.combine_takeout_dir(dir, dest)
# google_takeout.inspect_jsons(dir, 1, 0, 0)
# google_takeout.inspect_jsons(dir, 1, 1, 0)
# google_takeout.inspect_jsons(dir, 0, 0, 1)

# files.arrange_files_in_year_folders(dir, dest)
# compare.compare_folders(dir, "temp0", "photos")

print("\n\033[32mDone!\033[0m")
