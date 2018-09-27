import cv2

img = cv2.imread('example.jpg')
kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(10,10))
cv2.imwrite('example-dilate.jpg', cv2.dilate(img, kernel))
cv2.imwrite('example-erode.jpg', cv2.erode(img, kernel))
