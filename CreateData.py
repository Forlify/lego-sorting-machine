import cv2
import numpy as np
import os
import time
import StackImages

#####################################################

path_images = 'data/images'
minimal_blur = 40  # SMALLER VALUE MEANS MORE BLURRINESS
minimal_area = 100
scale = 0.25
scale_saved_images = 0.5
count = 0
count_saved_images = 0
save_data = True
font = cv2.FONT_HERSHEY_SIMPLEX

######################################################

cap = cv2.VideoCapture(0)

######################################################


def folderToSave():
    global count_folder
    count_folder = 0
    while os.path.exists(path_images + str(count_folder)):
        count_folder += 1
    os.makedirs(path_images + str(count_folder))


def scaleCoordinate(unscaled):
    return int(unscaled / scale * scale_saved_images)


def saveData(count_saved_images, img, img_small, img_contour, img_box, img_dilate):
    contours, hierarchy = cv2.findContours(img_dilate, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)  # CHAIN_APPROX_SIMPLE

    for contour in contours:
        area = cv2.contourArea(contour)
        if area > minimal_area:
            cv2.drawContours(img_contour, contour, -1, (255, 0, 255), 3)

            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
            x, y, w, h = cv2.boundingRect(approx)

            if y < int(80*scale) or y+h > int(1000*scale): continue

            cv2.rectangle(img_box, (x, y), (x + w, y + h), (0, 0, 255), 2)
            blur = cv2.Laplacian(img_small, cv2.CV_64F).var()

            cv2.putText(img_contour, "Points: " + str(len(approx)), (x + w + 20, y + 20), font, .7, (0, 255, 0), 2)
            cv2.putText(img_contour, "Area: " + str(int(area)), (x + w + 20, y + 45), font, .7, (0, 255, 0), 2)
            cv2.putText(img_contour, "Blur: " + str(int(blur)), (x + w + 20, y + 70), font, .7, (0, 255, 0), 2)

            if save_data and blur > minimal_blur:
                now_time = time.time()
                x = scaleCoordinate(x)
                y = scaleCoordinate(y)
                w = scaleCoordinate(w)
                h = scaleCoordinate(h)

                img_boxed = img[y: y + h, x: x + w]

                cv2.imwrite(path_images + str(count_folder) + '/' + str(count_saved_images) + "_" + str(int(blur)) + "_" + str(now_time) + ".png", img_boxed)
                count_saved_images += 1
    return count_saved_images


def main(count, count_saved_images):
    while True:
        success, img = cap.read()
        if not success:
            print("Can't receive web-cam image")
            break

        img = img[0:1080, 400:1520]

        img_small = cv2.resize(img, (0, 0), fx=scale, fy=scale)
        img = cv2.resize(img, (0, 0), fx=scale_saved_images, fy=scale_saved_images)
        img_contour = img_small.copy()
        img_box = img_small.copy()

        img_blur = cv2.GaussianBlur(img_small, (7, 7), 1)
        img_gray = cv2.cvtColor(img_blur, cv2.COLOR_BGR2GRAY)
        img_canny = cv2.Canny(img_gray, 45, 20)

        kernel = np.ones((5, 5))
        img_dilate = cv2.dilate(img_canny, kernel, iterations=1)

        count_saved_images = saveData(count_saved_images, img, img_small, img_contour, img_box, img_dilate)
        count += 1

        img_stacked = StackImages.stackImages(1, ([img_small, img_canny, img_dilate],
                                                  [img_contour, img_box, img_box]))

        print("count:", count, " countSave:", count_saved_images)

        cv2.imshow('result', img_stacked)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("exit")
            break


if __name__ == "__main__":
    if saveData:  folderToSave()
    main(count, count_saved_images)
    cap.release()
    cv2.destroyAllWindows()

