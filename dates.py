from datetime import datetime
from pathlib import Path
from PIL import Image
import subprocess
import filedate
import struct
import json
import os


# Source: https://mybyways.com/blog/file-date-created-to-photo-video-metadata
def _get_video_date_moov(fp, length):
    epoch_adjuster = 2082844800  # January 1, 1904
    creation = None
    pos = fp.tell()
    length = fp.read(4)
    if fp.read(4) == b'mvhd':
        fp.seek(4, 1)
        creation = struct.unpack('>I', fp.read(4))[0] - epoch_adjuster
        creation = datetime.fromtimestamp(creation)
    fp.seek(pos, 0)
    return creation


def _get_video_date_meta(fp, length):
    pos = fp.tell()
    fp.seek(16, 1)
    if fp.read(4) == b'mdta':
        found = i = 0
        fp.seek(26, 1)
        count = struct.unpack('>I', fp.read(4))[0]
        while i < count:
            i += 1
            length = struct.unpack('>I', fp.read(4))[0]
            if fp.read(length - 4) == b'mdtacom.apple.quicktime.creationdate':
                found = i
        fp.seek(4, 1)
        if fp.read(4) == b'ilst' and found > 0:
            i = 0
            while i < count:
                length = struct.unpack('>I', fp.read(4))[0]
                if struct.unpack('>I', fp.read(4))[0] == found:
                    fp.seek(16, 1)
                    creation = fp.read(length - 16)
                    if (n := creation.find(0)) > -1:
                        creation = creation[0:n]
                    return datetime.strptime(creation.decode(), '%Y-%m-%dT%H:%M:%S%z')
                fp.seek(length - 8, 1)
    fp.seek(pos, 0)
    return None


def get_video_creation_date_from_metadata(path):
    creation = None
    with open(path, 'rb') as fp:
        while (length := fp.read(4)) != b'':
            length = struct.unpack('>I', length)[0]
            section = fp.read(4)
            if section == b'moov':
                creation = _get_video_date_moov(fp, length)
            elif section == b'meta':
                metadata = _get_video_date_meta(fp, length)
                if metadata:
                    return metadata
            else:
                fp.seek(length - 8, 1)
    return creation


# Source: https://stackoverflow.com/questions/21355316/getting-metadata-for-mov-video
def get_mov_timestamps(path):
    """ Get the creation and modification date-time from .mov metadata.

        Returns None if a value is not available.
    """
    from datetime import datetime as DateTime
    import struct

    ATOM_HEADER_SIZE = 8
    # difference between Unix epoch and QuickTime epoch, in seconds
    EPOCH_ADJUSTER = 2082844800

    creation_time = modification_time = None

    # search for moov item
    with open(path, "rb") as f:
        while True:
            atom_header = f.read(ATOM_HEADER_SIZE)
            # ~ print('atom header:', atom_header)  # debug purposes
            if atom_header[4:8] == b'moov':
                break  # found
            else:
                atom_size = struct.unpack('>I', atom_header[0:4])[0]
                f.seek(atom_size - 8, 1)

        # found 'moov', look for 'mvhd' and timestamps
        atom_header = f.read(ATOM_HEADER_SIZE)
        if atom_header[4:8] == b'cmov':
            raise RuntimeError('moov atom is compressed')
        elif atom_header[4:8] != b'mvhd':
            raise RuntimeError('expected to find "mvhd" header.')
        else:
            f.seek(4, 1)
            creation_time = struct.unpack('>I', f.read(4))[0] - EPOCH_ADJUSTER
            creation_time = DateTime.fromtimestamp(creation_time)
            if creation_time.year < 1990:  # invalid or censored data
                creation_time = None

            modification_time = struct.unpack('>I', f.read(4))[0] - EPOCH_ADJUSTER
            modification_time = DateTime.fromtimestamp(modification_time)
            if modification_time.year < 1990:  # invalid or censored data
                modification_time = None

    return creation_time, modification_time


def get_image_creation_date_from_exif(path):
    image = Image.open(path)
    exif_data = image.getexif()
    date = exif_data.get(306)
    if isinstance(date, bytes):
        date = date.decode()
    if date is None:
        return None
    date = datetime.strptime(date, '%Y:%m:%d %H:%M:%S')
    return date


def get_taken_date_from_json(path):
    try:
        f = open(path)
        data = json.load(f)
        f.close()
        date = int(data['photoTakenTime']['timestamp'])
        return datetime.fromtimestamp(date)
    except:
        return None


def check_file_dates(path, created_date, modified_date):
    # check if modified time is different then update
    target = Path(path)

    c_time = target.stat().st_birthtime
    m_time = target.stat().st_mtime  # os.path.getmtime(path)

    cOk = c_time == created_date.timestamp()
    mOk = m_time == modified_date.timestamp()

    if cOk == 0 or mOk == 0:
        print(f"\033[34mUpdating dates\033[0m for: {path}")
        print(
            f"c_time {c_time} {created_date.timestamp()} {'' if c_time == created_date.timestamp() else f'---offset {c_time - created_date.timestamp()}'} {'' if cOk else '<<<'}")
        print(
            f"m_time {m_time} {modified_date.timestamp()} {'' if m_time == modified_date.timestamp() else f'---offset {m_time - modified_date.timestamp()}'} {'' if mOk else '<<<'}")
        print(f"created_date {created_date}, modified_date {modified_date}")

        set_file_dates(path, created_date, modified_date)


def set_file_dates(path, created_date, modified_date):
    dateformat = '%m/%d/%Y %H:%M:%S'

    # set creation, accessed and modified date
    filedate.File(path).set(
        created=created_date.strftime(dateformat),
        modified=modified_date.strftime(dateformat),
        accessed=modified_date.strftime(dateformat)
    )

    # set creation date
    subprocess.run(['SetFile', '-d', created_date.strftime(dateformat), path], check=True, stdout=subprocess.PIPE)

    # set accessed and modified time
    os.utime(path, (modified_date.timestamp(), modified_date.timestamp()))
