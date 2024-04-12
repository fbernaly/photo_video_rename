from PIL import Image
import numpy as np
import subprocess
import filecmp
import pathlib
import cv2
import os

# local imports
import formats


def _compare_image(path, ori, dest):
    compare_path = path.replace(ori, dest)
    if os.path.exists(compare_path) == 0:
        print(f"Image \033[31mdoes not exist\033[0m in: {compare_path}")
        path_edited = path.replace(' ', '\\ ')
        subprocess.Popen(f"open -R  {path_edited}", shell=True)
        input("Hit enter to continue")
        return

    filename = os.path.basename(path)
    print(f"Image: {filename}")

    img1 = np.array(Image.open(path).convert('RGB'))
    img2 = np.array(Image.open(compare_path).convert('RGB'))

    img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    h1, w1 = img1.shape
    h2, w2 = img2.shape

    if h1 == w2 and h2 == w1:
        img2 = cv2.rotate(img2, cv2.ROTATE_90_CLOCKWISE)

    if h1 * w1 != h2 * w2:
        print(">>>> ")
        result = False
    else:
        difference = cv2.subtract(img1, img2)
        result = not np.any(difference)

        if result is False:
            error = np.sum(difference ** 2)
            error = error / (float(h1 * w1))
            print("Error between the two images:", error)
            if error < 10:
                result = True

    if result is True:
        print("Images are the same")
    else:
        print(f"Images are \033[31mdifferent\033[0m, compare result: {filecmp.cmp(path, compare_path)}")

        path_edited = path.replace(' ', '\\ ')
        compare_path_edited = compare_path.replace(' ', '\\ ')
        subprocess.Popen(f"open -R  {path_edited}", shell=True)
        subprocess.Popen(f"open -R  {compare_path_edited}", shell=True)

        input("Hit enter to continue")

        # f = plt.figure(figsize=(14, 8))
        # f.suptitle(f'Path: {filename}', fontsize=16)
        # f.add_subplot(1, 2, 1)
        # plt.imshow(mpimg.imread(path))
        # plt.title(ori)
        #
        # f.add_subplot(1, 2, 2)
        # plt.imshow(mpimg.imread(compare_path))
        # plt.title(dest)
        # plt.show(block=True)


def _compare_video(path, ori, dest):
    compare_path = path.replace(ori, dest)
    if os.path.exists(compare_path) == 0:
        print(f"Video \033[31mdoes not exist\033[0m in: {compare_path}")
        path_edited = path.replace(' ', '\\ ')
        subprocess.Popen(f"open -R  {path_edited}", shell=True)
        input("Hit enter to continue")
        return

    filename = os.path.basename(path)
    print(f"Video: {filename}")

    result = filecmp.cmp(path, compare_path)

    if result is True:
        print("Videos are the same")
    else:
        print("Videos are \033[31mdifferent\033[0m")
        path_edited = path.replace(' ', '\\ ')
        compare_path_edited = compare_path.replace(' ', '\\ ')
        subprocess.Popen(f"open -R  {path_edited}", shell=True)
        subprocess.Popen(f"open -R  {compare_path_edited}", shell=True)
        input("Hit enter to continue")


def compare_folders(dir, ori, dest):
    if os.path.exists(dir) == 0:
        return
    _files = os.listdir(dir)
    _files.sort()
    if len(_files) == 0:
        os.rmdir(dir)
        return
    for file in _files:
        path = os.path.join(dir, file)
        if os.path.exists(path) == 0:
            continue
        if os.path.isfile(path):
            extension = pathlib.Path(file).suffix.lower()
            if extension == ".json":
                continue
            elif formats.VIDEO_FORMATS.__contains__(extension):
                _compare_video(path, ori, dest)
            elif formats.IMG_FORMATS.__contains__(extension):
                _compare_image(path, ori, dest)
        else:
            compare_folders(path, ori, dest)
