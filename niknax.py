import numpy as np
import time

import cv2
import pytesseract

import Levenshtein as lv

import string

import os

folder = "input/"
dir_list = os.listdir(folder)
dir_list.sort()

topLeft = (300, 400)
bottomRight = (1550, 1100)

def run(fname, resultsMap):
    img = cv2.imread(folder + fname)

    cropped = img[topLeft[1]:bottomRight[1], topLeft[0]:bottomRight[0]]

    # Convert the image to gray scale
    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)

    #cv2.imshow("n", gray)
    #cv2.waitKey(0)
    
    # Performing OTSU threshold
    ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY)

    #cv2.imshow("n", thresh1)
    #cv2.waitKey(0)
    
    # Specify structure shape and kernel size.
    # Kernel size increases or decreases the area
    # of the rectangle to be detected.
    # A smaller value like (10, 10) will detect
    # each word instead of a sentence.
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 10))
    
    # Applying dilation on the threshold image
    dilation = cv2.dilate(thresh1, rect_kernel, iterations = 1)

    #cv2.imshow("n", dilation)
    #cv2.waitKey(0)
    
    # Finding contours
    _, contours, _ = cv2.findContours(dilation, cv2.RETR_EXTERNAL,
                                                    cv2.CHAIN_APPROX_NONE)

    im2 = cv2.bitwise_not(thresh1.copy())

    #rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    #im2 = cv2.erode(im2, rect_kernel, iterations = 1)

    im3 = cropped.copy()#im2.copy()

    #print(len(contours), "contours")

    # Looping through the identified contours
    # Then rectangular part is cropped and passed on
    # to pytesseract for extracting text from it
    # Extracted text is then written into the text file
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        
        # Cropping the text block for giving input to OCR
        cropped = im2[y:y + h, x:x + w]
        
        # Drawing a rectangle on copied image
        #rect = cv2.rectangle(im3, (x, y), (x + w, y + h), (255, 255, 255), 2)#(0, 0, 0), 2)
        
        # Apply OCR on the cropped image
        text = pytesseract.image_to_string(cropped, config='--psm 6')
        text = text.strip(string.whitespace)
        text = text.replace("”", "\"")
        text = text.replace("“", "\"")

        if len(text) == 0:
            continue
        
        #print(text)
        if text in resultsMap:
            resultsMap[text] += 1
        else:
            resultsMap[text] = 1

        #cv2.imshow("n", rect)
        #cv2.waitKey(0)

resultsMap = {}    

for i in range(0, len(dir_list)):
    fname = dir_list[i]
    print("Running " + str(i+1) + "/" + str(len(dir_list)) + "...")
    run(fname, resultsMap)
    #if i >= 5:
    #    break

print("\nChecking string similarity...")

keys = list(resultsMap.keys());
for i in range(0, len(keys)-1):
    for j in range(i + 1, len(keys)):
        keyA = keys[i]
        keyB = keys[j]

        if keyA not in resultsMap or keyB not in resultsMap or keyA == keyB:
            continue

        if resultsMap[keyB] > resultsMap[keyA]:
            keyB = keys[i]
            keyA = keys[j]

        auto = resultsMap[keyA] >= 3 * resultsMap[keyB]
        
        lvDist = lv.distance(keyB, keyA)
        if lvDist <= 3:
            if not auto:
                inp = input("\nIs \n  |" + keyB + "| (" + str(resultsMap[keyB]) + ") supposed to be \n  |" + keyA + "| (" + str(resultsMap[keyA]) + ")? Y/N/S:")
            if auto or inp == "Y" or inp == "y":
                print("    Changing |" + keyB + "| to |" + keyA + "|")
                resultsMap[keyA] += resultsMap[keyB]
                keys[j] = keyA
                del resultsMap[keyB]
            elif inp == "S" or inp == "s":
                print("    Changing |" + keyA + "| to |" + keyB + "|")
                resultsMap[keyB] += resultsMap[keyA]
                keys[i] = keyB
                del resultsMap[keyA]
            else:
                print("    Skipping")


print("Done.\n\nInventory:")

for key in sorted(resultsMap.keys()):
    print(key + ": " + str(resultsMap[key]))