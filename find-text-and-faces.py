import zipfile

from PIL import Image
from PIL import ImageDraw

import pytesseract
import cv2 as cv
import numpy as np
import math

# loading the face detection classifier
face_cascade = cv.CascadeClassifier('readonly/haarcascade_frontalface_default.xml')

FULL_PATH_KEY = "full_path"
STRING_FOUND_KEY = "string_found"
FACE_BOXES_KEY = "face_boxes"
FACE_IMAGES_KEY = "face_images"


def extract_image_filenames(zip_filename):
    """Extract all the image filenames from a zip archive into a dictionary"""
    images_dict = {}  # Data for all of the images, keyed by base filename.
    with zipfile.ZipFile(zip_filename, mode="r") as image_archive:
        # Get a list of the contents of the archive.
        archive_items = image_archive.infolist()
        for im in archive_items:
            item_dict = {}
            item_dict[FULL_PATH_KEY] = image_archive.extract(im)
            images_dict[im.filename] = item_dict

    return images_dict


def search_for_str(images_dict, search_str):
    """Search for a piece of text in the images, and
    store the results in the images_dict param"""

    for img_filename, img_data in images_dict.items():
        print("Searching for string '{}' in file {}".format(search_str, img_filename))

        full_path = img_data[FULL_PATH_KEY]

        with Image.open(full_path) as image:
            img_data[STRING_FOUND_KEY] = []
            page_text = pytesseract.image_to_string(image)
            if search_str in page_text:
                img_data[STRING_FOUND_KEY].append(search_str)

    return images_dict


def find_faces(img_filename):
    """Given an image file, find bounding boxes of faces in the image"""

    cv_img = cv.imread(img_filename)

    # The first param is an ndarray of the image.
    # Setting the minSize removes rectangles that are usually too small to be faces.
    # The scaleFactor value was arrived at through trial and error.
    faces = face_cascade.detectMultiScale(cv_img, minSize=(150, 150), scaleFactor=1.25)

    # detectMultiScale() returns an ndarray of objects as rectangular bounding boxes.
    return faces

    # I tried using conversions to greyscale and binarization but did not really
    # get any better results generally over the set of images in the images.zip archive.


def get_face_images(images_dict):
    """Extract face images for entries in images_dict
    for which the search string was found, and
    store the sub-images in the images_dict param"""

    for img_filename, img_data in images_dict.items():

        if not img_data[STRING_FOUND_KEY]:
            img_data[FACE_BOXES_KEY] = []
            continue

        img_data[FACE_BOXES_KEY] = find_faces(img_filename)

        img_data[FACE_IMAGES_KEY] = []
        with Image.open(img_filename) as img:
            for left, upper, width, height in img_data[FACE_BOXES_KEY]:
                face_img = img.crop(box=(left, upper, left + width, upper + height))
                img_data[FACE_IMAGES_KEY].append(face_img)

    return images_dict


def make_contact_sheet(face_images):
    """Make a contact sheet of five faces across in each row"""

    # Pixel dimensions of each face.
    PIXELS_WIDE = 100
    PIXELS_TALL = 100

    NUM_COLUMNS = 5  # Five faces across in each row
    num_rows = math.ceil(len(face_images) / NUM_COLUMNS)

    contact_dimensions = (NUM_COLUMNS * PIXELS_WIDE, num_rows * PIXELS_TALL)

    contact_sheet = Image.new(face_images[0].mode, contact_dimensions)

    for idx, face in enumerate(face_images):
        if face.height > PIXELS_TALL or face.width > PIXELS_WIDE:
            face = face.resize((PIXELS_WIDE, PIXELS_TALL))

        horz_pos = idx % NUM_COLUMNS
        vert_pos = math.floor(idx / NUM_COLUMNS)
        contact_sheet.paste(face, (horz_pos * PIXELS_WIDE, vert_pos * PIXELS_TALL))

    return contact_sheet


def show_results(images_dict):
    """Finally, show the desired results"""

    for img_filename, img_data in images_dict.items():
        search_str = img_data[STRING_FOUND_KEY]
        if search_str:
            print("\n Result '{}' found in file {}".format(search_str[0], img_filename))
            face_images = img_data[FACE_IMAGES_KEY]
            if face_images:
                contact_sheet = make_contact_sheet(face_images)
                display(contact_sheet)
            else:
                print("But there were no faces found in that file!")


## ========== Driver code here ====================

import datetime

##zip_filename = "readonly/small_img.zip"
zip_filename = "readonly/smallest.zip"
##zip_filename = "readonly/images.zip"

print("\n Started run @ {} \n".format(datetime.datetime.now()))

images_dict = extract_image_filenames(zip_filename)
search_for_str(images_dict, "Mark")  # Either "Christopher" or "Mark" or whatever
get_face_images(images_dict)
show_results(images_dict)

print("\n Completed run @ {} \n".format(datetime.datetime.now()))
