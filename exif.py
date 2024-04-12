from PIL.ExifTags import TAGS
from PIL import Image
import exifread


def print_exif_data(path):
    image = Image.open(path)
    exif_data = image.getexif()
    for tag_id, value in exif_data.items():
        # get the tag name, instead of human unreadable tag id
        tag = TAGS.get(tag_id, tag_id)
        print(f"{tag:25} [{tag_id:5}]: {value}")

        if tag == "ExifOffset":
            info = get_exif_detail(exif_data.get_ifd(tag_id))
            print(info)

        if tag == "GPSInfo":
            info = get_exif_detail(exif_data.get_ifd(tag_id))
            print(info)
            lat, lon = get_location(info)
            print(f"coordinates: {lat}, {lon}")


def get_exif_detail(exif):
    return {
        TAGS.get(key, key): value
        for key, value in exif.items()
    }


def get_location(exif_data):
    """
    Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)
    """
    lat = None
    lon = None

    gps_latitude = _get_if_exist(exif_data, 2)
    gps_latitude_ref = _get_if_exist(exif_data, 'InteropIndex')
    gps_longitude = _get_if_exist(exif_data, 4)
    gps_longitude_ref = _get_if_exist(exif_data, 3)

    if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
        print(
            f"coordinates: {int(gps_latitude[0])}°{int(gps_latitude[1])}'{float(gps_latitude[2])}\"{gps_latitude_ref} {int(gps_longitude[0])}°{int(gps_longitude[1])}'{float(gps_longitude[2])}\"{gps_longitude_ref}")

        lat = _convert_to_degrees(gps_latitude)
        if gps_latitude_ref != 'N':
            lat = 0 - lat

        lon = _convert_to_degrees(gps_longitude)
        if gps_longitude_ref != 'E':
            lon = 0 - lon

    return lat, lon


def _get_if_exist(data, key):
    if key in data:
        return data[key]
    return None


def _convert_to_degrees(value):
    """
    Helper function to convert the GPS coordinates stored in the EXIF to degrees in float format
    :param value:
    :type value: exifread.utils.Ratio
    :rtype: float
    """
    d = float(value[0])
    m = float(value[1])
    s = float(value[2])

    return d + (m / 60.0) + (s / 3600.0)
