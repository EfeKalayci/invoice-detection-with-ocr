import cv2
from imutils.perspective import order_points
from matplotlib import pyplot as plt
from skimage.filters import threshold_local
import numpy as np
import socket
import  pytesseract

pytesseract.pytesseract.tesseract_cmd = "C:\\Users\\efeka\\AppData\Local\\Programs\\Tesseract-OCR\\tesseract.exe"

from skimage.filters import unsharp_mask
from skimage import img_as_ubyte


def sharpening(image):
    image = unsharp_mask(image)
    return img_as_ubyte(image)

def floatFormat(text):
    word = "0123456789"
    text = "239,712,80"
    for k in text:
        if k not in word:
            text = text.replace(k, "")
    text = text[:-2] + "." + text[-2:]
    return text
def dateFormat(text):
    word = "0123456789"
    text = "11-03.2022"
    text = text.replace(".", "-")
    text = text.split("-")
    if len(text[0]) == 4:
        text = (text[0] + "-" + text[1] + "-" + text[2])
    else:
        text = (text[2] + "-" + text[1] + "-" + text[0])
    return text
def grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def threshold(image):
    T = threshold_local(image, 11, offset=10, method="gaussian")
    image = (image > T).astype("uint8") * 255
    return image


def denoising(image):
    kernel = np.ones((2, 2), np.uint8)
    # image = cv2.dilate(image, kernel,iterations=1)
    # kernel = np.ones((2, 2), np.uint8)
    # image = cv2.erode(image, kernel, iterations=1)
    image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
    return image


def nlMeansDenoising(image):
    return cv2.fastNlMeansDenoising(image, None, h=3, templateWindowSize=7, searchWindowSize=21)


def line_remover(img_gray):
    image = threshold(img_gray)
    kernel_vertical = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 50))
    temp1 = 255 - cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel_vertical)
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 1))
    temp2 = 255 - cv2.morphologyEx(image, cv2.MORPH_CLOSE, horizontal_kernel)
    temp3 = cv2.add(temp1, temp2)
    result = cv2.add(temp3, image)
    return result


def display(im_path):
    dpi = 80
    im_data = plt.imread(im_path)

    height, width = im_data.shape[:2]

    # What size does the figure need to be in inches to fit the image?
    figsize = width / float(dpi), height / float(dpi)

    # Create a figure of the right size with one axes that takes up the full figure
    fig = plt.figure(figsize=figsize)
    ax = fig.add_axes([0, 0, 1, 1])

    # Hide spines, ticks, etc.
    ax.axis('off')

    # Display the image.
    ax.imshow(im_data, cmap='gray')

    plt.show()


def four_point_transform(image, pts):
    # obtain a consistent order of the points and unpack them
    # individually
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    # compute the width of the new image, which will be the
    # maximum distance between bottom-right and bottom-left
    # x-coordiates or the top-right and top-left x-coordinates
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    # compute the height of the new image, which will be the
    # maximum distance between the top-right and bottom-right
    # y-coordinates or the top-left and bottom-left y-coordinates
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    # now that we have the dimensions of the new image, construct
    # the set of destination points to obtain a "birds eye view",
    # (i.e. top-down view) of the image, again specifying points
    # in the top-left, top-right, bottom-right, and bottom-left
    # order
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")
    # compute the perspective transform matrix and then apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    # return the warped image
    return warped

def getSkewAngle(cvImage) -> float:
    # Prep image, copy, convert to gray scale, blur, and threshold
    newImage = cvImage.copy()
    try:
        gray = cv2.cvtColor(newImage, cv2.COLOR_BGR2GRAY)
    except:
        gray = newImage
    blur = cv2.GaussianBlur(gray, (9, 9), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Apply dilate to merge text into meaningful lines/paragraphs.
    # Use larger kernel on X axis to merge characters into single line, cancelling out any spaces.
    # But use smaller kernel on Y axis to separate between different blocks of text
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 5))
    dilate = cv2.dilate(thresh, kernel, iterations=5)

    # Find all contours
    contours, hierarchy = cv2.findContours(dilate, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key = cv2.contourArea, reverse = True)
    # Find largest contour and surround in min area box
    largestContour = contours[0]
    minAreaRect = cv2.minAreaRect(largestContour)

    # Determine the angle. Convert it to the value that was originally used to obtain skewed image
    angle = minAreaRect[-1]
    if angle < -45:
        angle = 90 + angle

    return -1.0 * angle

# Rotate the image around its center
def rotateImage(cvImage, angle: float):
    newImage = cvImage.copy()
    (h, w) = newImage.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    newImage = cv2.warpAffine(newImage, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return newImage


def findInvoiceNo(d,d1):

    n_boxes = len(d['level'])
    for i in range(n_boxes):
        if "Fatura" in  d['text'][i] :
            line =  int(d['line_num'][i])
            word =  int(d['word_num'][i])
            for j in range(n_boxes):
                if int(d['line_num'][j]) == line and int(d['word_num'][j]) >= word and  int(d['word_num'][j]) < word+5 and "No" in d['text'][j] :
                    for k in range(10):
                        if len(d['text'][j+k])>13 and len(d['text'][j+k])<20 :
                            text = d['text'][j + k].strip(" ")
                            if text[0] == "İ":
                                return text[1:]
                            return text

    n_boxes = len(d1['level'])
    for i in range(n_boxes):
        if "Fatura" in d1['text'][i]:
            line = int(d1['line_num'][i])
            word = int(d1['word_num'][i])
            for j in range(n_boxes):
                if int(d1['line_num'][j]) == line and int(d1['word_num'][j]) >= word and int(
                        d1['word_num'][j]) < word + 5 and "No" in d1['text'][j]:
                    for k in range(10):
                        if len(d1['text'][j + k]) > 13 and len(d1['text'][j + k]) < 20:
                            text = d1['text'][j+k].strip(" ")
                            if text[0] == "İ":
                                return text[1:]
                            return text

# Deskew image
def deskew(cvImage):
    angle = getSkewAngle(cvImage)
    return rotateImage(cvImage, -1.0 * angle)

def findTotalAmount(d,d1):

    n_boxes = len(d['level'])
    for i in range(n_boxes):
        if "Ödenecek" in d['text'][i]:
            line = int(d['line_num'][i])
            word = int(d['word_num'][i])
            parnum= int(d['par_num'][i])
            text= ""
            returned=""
            chars="0123456789,."
            for j in range(n_boxes):
                if int(d['line_num'][j]) == line and int(d['word_num'][j]) >= word and int(d['word_num'][j]) < word + 4 and "tutar" in d['text'][j].lower():
                    for k in range(n_boxes):
                        if int(d['line_num'][k]) == line and int(d['word_num'][k]) >= word and int(d['word_num'][k]) < word+6 and parnum == int(d['par_num'][k]):
                            text+=d['text'][k]

                    for i in text:
                        if i in chars:
                            returned+=i
                        else:
                            if len(returned)>0:
                                return returned
                    if len(returned)>0:
                        return returned
    n_boxes = len(d1['level'])
    for i in range(n_boxes):
        if "Ödenecek" in d1['text'][i]:
            line = int(d1['line_num'][i])
            word = int(d1['word_num'][i])
            text = ""
            returned = ""
            chars = "0123456789,."
            for j in range(n_boxes):
                if int(d1['line_num'][j]) == line and int(d1['word_num'][j]) >= word and int(
                        d1['word_num'][j]) < word + 4 and "tutar" in d1['text'][j].lower():
                    for k in range(n_boxes):
                        if int(d1['line_num'][k]) == line and int(d1['word_num'][k]) >= word:
                            text += d1['text'][k]

                    for i in text:
                        if i in chars:
                            returned += i
                        else:
                            if len(returned) > 0:
                                return returned
                    return returned
    n_boxes = len(d['level'])
    for i in range(n_boxes):
        if "fatura" in d['text'][i].lower():
            line = int(d['line_num'][i])
            word = int(d['word_num'][i])
            text= ""
            returned=""
            chars="0123456789,."
            for j in range(n_boxes):
                if int(d['line_num'][j]) == line and int(d['word_num'][j]) >= word and int(d['word_num'][j]) < word + 4 and "tutar" in d['text'][j].lower():
                    for k in range(n_boxes):
                        if int(d['line_num'][k]) == line and int(d['word_num'][k]) >= word :
                            text+=d['text'][k]
                    for i in text:
                        if i in chars:
                            returned+=i
                        else:
                            if len(returned)>0:
                                return returned
                    return returned
    n_boxes = len(d1['level'])
    for i in range(n_boxes):
        if "fatura" in d1['text'][i].lower():
            line = int(d1['line_num'][i])
            word = int(d1['word_num'][i])
            text = ""
            returned = ""
            chars = "0123456789,."
            for j in range(n_boxes):
                if int(d1['line_num'][j]) == line and int(d1['word_num'][j]) >= word and int(
                        d1['word_num'][j]) < word + 4 and "tutar" in d1['text'][j].lower():
                    for k in range(n_boxes):
                        if int(d1['line_num'][k]) == line and int(d1['word_num'][k]) >= word:
                            text += d1['text'][k]
                    for i in text:
                        if i in chars:
                            returned += i
                        else:
                            if len(returned) > 0:
                                return returned
                    return returned

def findDate(d, d1):

    n_boxes = len(d['level'])
    for i in range(n_boxes):
        if "ödeme" in d['text'][i].lower():
            line = int(d['line_num'][i])
            word = int(d['word_num'][i])
            text= ""
            returned=""
            chars="0123456789-."
            for j in range(n_boxes):
                if int(d['line_num'][j]) == line and int(d['word_num'][j]) >= word and int(d['word_num'][j]) < word + 4 and ("tarihi" in d['text'][j].lower()or "TARİHİ" in d['text'][j].upper()):
                    for k in range(n_boxes):
                        if int(d['line_num'][k]) == line and int(d['word_num'][k]) >= word :
                            text+=d['text'][k]
                    for i in text:
                        if i in chars:
                            returned+=i
                        else:
                            if len(returned)>2:
                                return returned
                            else: returned=""

                    return returned
    n_boxes = len(d1['level'])
    for i in range(n_boxes):
        if "ödeme" in d1['text'][i].lower():
            line = int(d1['line_num'][i])
            word = int(d1['word_num'][i])
            text = ""
            returned = ""
            chars = "0123456789-."
            for j in range(n_boxes):
                if int(d1['line_num'][j]) == line and int(d1['word_num'][j]) >= word and int(
                        d1['word_num'][j]) < word + 4 and "TARİHİ" in d1['text'][j].upper():
                    for k in range(n_boxes):
                        if int(d1['line_num'][k]) == line and int(d1['word_num'][k]) >= word:
                            text += d1['text'][k]
                    for i in text:
                        if i in chars:
                            returned += i
                        else:
                            if len(returned) > 2:
                                return returned
                            else:

                                returned = ""
                    return returned
    n_boxes = len(d['level'])
    for i in range(n_boxes):
        if "fatura" in d['text'][i].lower():
            line = int(d['line_num'][i])
            word = int(d['word_num'][i])
            text= ""
            returned=""
            chars="0123456789-."
            for j in range(n_boxes):
                if int(d['line_num'][j]) == line and int(d['word_num'][j]) >= word and int(d['word_num'][j]) < word + 4 and ("tarihi" in d['text'][j].lower()or "TARİHİ" in d['text'][j].upper()):
                    for k in range(n_boxes):
                        if int(d['line_num'][k]) == line and int(d['word_num'][k]) >= word and int(d['word_num'][k]) < word+4:
                            text+=d['text'][k]

                    for i in text:
                        if i in chars:
                            returned+=i
                        else:
                            if len(returned)>2:
                                return returned
                            else:
                                returned = ""

                    return returned
    n_boxes = len(d1['level'])
    for i in range(n_boxes):
        if "fatura" in d1['text'][i].lower():
            line = int(d1['line_num'][i])
            word = int(d1['word_num'][i])
            text = ""
            returned = ""
            chars = "0123456789-."
            for j in range(n_boxes):
                if int(d1['line_num'][j]) == line and int(d1['word_num'][j]) >= word and int(
                        d1['word_num'][j]) < word + 4 and ("tarihi" in d1['text'][j].lower()or "TARİHİ" in d1['text'][j].upper()):
                    for k in range(n_boxes):
                        if int(d1['line_num'][k]) == line and int(d1['word_num'][k]) >= word:
                            text += d1['text'][k]

                    for i in text:
                        if i in chars:
                            returned += i
                        else:
                            if len(returned) > 2:
                                return returned
                            else:
                                returned = ""
                    return returned

def findInvoice(image):
    image = cv2.imread(image)
    # IMAGE PREPROCESSING
    image = grayscale(image)
    image = sharpening(image)
    image = nlMeansDenoising(image)
    image = threshold(image)
    image = cv2.GaussianBlur(image, (5, 5), 0)
    image1 = line_remover(image)
    d = pytesseract.image_to_data(image,lang="tur",config="--oem 2 --psm 6",output_type=pytesseract.Output.DICT)
    d1 = pytesseract.image_to_data(image1, lang="tur", config="--oem 2 --psm 6", output_type=pytesseract.Output.DICT)

    return findInvoiceNo(d,d1), floatFormat(findTotalAmount(d, d1)) , dateFormat(findDate(d, d1))

id, amount , date = findInvoice("Mepas-1.jpg")
print('id:{0} \n price:{1} \n date:{2}'.format(id,amount,date))