import os
import cv2
from skimage.measure import compare_ssim
import imutils

images = []
for img in os.listdir("."):
	if img.endswith(".png"):
		images.append(img)

images = sorted(images)
first = images[0]
ref_img = cv2.imread(first)[450:3000, 700:1000, :]
ref_img = cv2.cvtColor(ref_img, cv2.COLOR_BGR2GRAY)
for img in images[1:]:
	cmp_img = cv2.imread(img)[450:3000, 700:1000, :]
	cmp_img = cv2.cvtColor(cmp_img, cv2.COLOR_BGR2GRAY)
	(score, diff) = compare_ssim(ref_img, cmp_img, full=True)
	diff = (diff * 255).astype("uint8")
	# threshold the difference image, followed by finding contours to
	# obtain the regions of the two input images that differ
	thresh = cv2.threshold(diff, 0, 50, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	# loop over the contours
	for c in cnts:
		# compute the bounding box of the contour and then draw the
		# bounding box on both input images to represent where the two
		# images differ
		(x, y, w, h) = cv2.boundingRect(c)

		cv2.rectangle(cmp_img, (x, y), (x + w, y + h), (0, 0, 255), 2)
	# show the output images
	cv2.imshow("Original", ref_img)
	cv2.imshow("Modified", cmp_img)
	cv2.imshow("Diff", diff)
	cv2.imshow("Thresh", thresh)
	cv2.waitKey(0)