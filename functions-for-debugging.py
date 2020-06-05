from PIL import ImageDraw


def dump_images_dict():
    """DEBUGGING - show the contents of images_dict"""
    for im_filename, im_data in images_dict.items():
        strings_found = im_data[STRING_FOUND_KEY]
        if len(strings_found) >= 1:
            print("\n\nResults {} found in file {}".format(strings_found, im_filename))


def display_found_faces(img_filename, found_faces):
    """DEBUGGING - display the image with
    bounding boxes around all the found faces"""

    cv_img = cv.imread(img_filename)

    # The resulting rectangles are in the format of (x, y, w, h)
    # where x and y denote the upper left hand point for the image
    # and the width and height represent the bounding box.

    pil_img = Image.fromarray(cv_img, mode="RGB")
    drawing = ImageDraw.Draw(pil_img)

    # And iterate through the faces sequence.
    for x, y, w, h in found_faces:
        drawing.rectangle((x, y, x + w, y + h), outline="red", width=10)

    display(pil_img)


def outline_found_faces():
    """DEBUGGING - check what faces were found in one or more files"""
    for im_filename, im_data in images_dict.items():
        if im_filename == 'a-0.png':  ## I only want to see faces for one of the images
            faces = find_faces(im_filename)
            display_found_faces(im_filename, faces)
            break
