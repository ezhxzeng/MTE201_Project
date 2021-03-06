# adapted from pyimagesearch.com 
# import the necessary packages

from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2


def midpoint(ptA, ptB):
    return (ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5


def objsize(img, qr_info):
    '''
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True,
        help="path to the input image")
    ap.add_argument("-w", "--width", type=float, required=True,
        help="width of the left-most object in the image (in inches)")
    args = vars(ap.parse_args())
    '''

    # load the image, convert it to grayscale, and blur it slightly
    # image = cv2.imread(args["image"])

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


    gray = cv2.GaussianBlur(gray, (7, 7), 0)
    # perform edge detection, then perform a dilation + erosion to
    # close gaps in between object edges
    edged = cv2.Canny(gray, 50, 100)
    edged = cv2.dilate(edged, None, iterations=1)
    edged = cv2.erode(edged, None, iterations=1)

    # find contours in the edge map
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]

    if type(qr_info['data']) != int:
        print("error type in qr_info['data']")
        return

    # obtain heightwidth/qrcode data
    pixelsPerMetric = qr_info["width"] / qr_info['data']
    # pixelsPerMetric = qr_info["data"] / qr_info["width"]

    # cv2.imshow("Image", edged)
    # cv2.waitKey(0)

    # loop over the contours individually
    for c in cnts:
        # if the contour is not sufficiently large, ignore it
        if cv2.contourArea(c) < 1000:
            continue

        # compute the rotated bounding box of the contour
        orig = img.copy()
        box = cv2.minAreaRect(c)
        box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
        box = np.array(box, dtype="int")

        print(box)

        # order the points in the contour such that they appear
        # in top-left, top-right, bottom-right, and bottom-left
        # order, then draw the outline of the rotated bounding
        # box
        box = perspective.order_points(box)
        cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)

        # loop over the original points and draw them
        for (x, y) in box:
            cv2.circle(orig, (int(x), int(y)), 4, (0, 0, 255), -1)

        # unpack the ordered bounding box, then compute the midpoint
        # between the top-left and top-right coordinates, followed by
        # the midpoint between bottom-left and bottom-right coordinates
        (tl, tr, br, bl) = box
        (tltrX, tltrY) = midpoint(tl, tr)
        (blbrX, blbrY) = midpoint(bl, br)

        # compute the midpoint between the top-left and top-right points,
        # followed by the midpoint between the top-righ and bottom-right
        (tlblX, tlblY) = midpoint(tl, bl)
        (trbrX, trbrY) = midpoint(tr, br)

        # draw the midpoints on the image
        cv2.circle(orig, (int(tltrX), int(tltrY)), 4, (255, 0, 0), -1)
        cv2.circle(orig, (int(blbrX), int(blbrY)), 4, (255, 0, 0), -1)
        cv2.circle(orig, (int(tlblX), int(tlblY)), 4, (255, 0, 0), -1)
        cv2.circle(orig, (int(trbrX), int(trbrY)), 4, (255, 0, 0), -1)

        # draw lines between the midpoints
        cv2.line(orig, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)),
                 (255, 0, 255), 2)
        cv2.line(orig, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)),
                 (255, 0, 255), 2)

        # compute the Euclidean distance between the midpoints
        dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
        dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))

        # compute the size of the object
        dimA = dA / pixelsPerMetric
        dimB = dB / pixelsPerMetric

        # draw the object sizes on the image
        # cyan
        cv2.putText(orig, "{:.2f}in".format(dimA),
                    (int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (255, 255, 0), 2)
        # magenta
        cv2.putText(orig, "{:.2f}in".format(dimB),
                    (int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (255, 0, 255), 2)

        # show the output image
        cv2.namedWindow("Display Window", cv2.WINDOW_NORMAL)
        cv2.imshow("Display Window", orig)
        cv2.waitKey(0)

    return


# Main
if __name__ == '__main__':
    img = cv2.imread("test_qr_code.png")

    objsize(img, {"data": 100, "width": 200, "height": 200})
