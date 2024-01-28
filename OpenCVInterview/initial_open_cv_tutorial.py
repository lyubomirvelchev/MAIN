import cv2

image = cv2.imread("road.jpg")
# h, w = image.shape[:2]
# print("Height = {},  Width = {}".format(h, w))
# print("Image shape = {}".format(image.shape))
#
# roi = image[100: 500, 200: 700]
#
# # cv2.imshow("ROI", roi)
# # cv2.waitKey(0)
#
# print("R, G, B values:", image[100, 200])
# print("R, G, B values:", image[100, 300])
# print("R, G, B values:", image[100, 200])
# print("R, G, B values:", image[100, 250])
#
# resize = cv2.resize(image, (300, 300))
# # cv2.imshow("Resize", resize)
# # cv2.waitKey(0)
#
# ratio = 800 / w
#
# dim = (800, int(h * ratio))
#
# resize_aspect = cv2.resize(image, dim)
# cv2.imshow("Resize aspect", resize_aspect)
# cv2.waitKey(0)


# Load two images
img1 = cv.imread('messi5.jpg')
img2 = cv.imread('opencv-logo-white.png')
assert img1 is not None, "file could not be read, check with os.path.exists()"
assert img2 is not None, "file could not be read, check with os.path.exists()"
# I want to put logo on top-left corner, So I create a ROI
rows,cols,channels = img2.shape
roi = img1[0:rows, 0:cols]
# Now create a mask of logo and create its inverse mask also
img2gray = cv.cvtColor(img2,cv.COLOR_BGR2GRAY)
ret, mask = cv.threshold(img2gray, 10, 255, cv.THRESH_BINARY)
mask_inv = cv.bitwise_not(mask)
# Now black-out the area of logo in ROI
img1_bg = cv.bitwise_and(roi,roi,mask = mask_inv)
# Take only region of logo from logo image.
img2_fg = cv.bitwise_and(img2,img2,mask = mask)
# Put logo in ROI and modify the main image
dst = cv.add(img1_bg,img2_fg)
img1[0:rows, 0:cols ] = dst
cv.imshow('res',img1)
cv.waitKey(0)
cv.destroyAllWindows()