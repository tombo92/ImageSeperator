#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2021-04-14 14:57:35
# @Author  : Tom Brandherm (s_brandherm19@stud.hwr-berlin.de)
# @Link    : link
# @Version : 1.0.0
"""
tool for cropping a game board of rectangular shapes into single images
"""
# =========================================================================== #
#  Copyright 2021 Team Awesome
# =========================================================================== #
#  All Rights Reserved.
#  The information contained herein is confidential property of Team Awesome.
#  The use, copying, transfer or disclosure of such information is prohibited
#  except by express written agreement with Team Awesome.
# =========================================================================== #

# =========================================================================== #
#  SECTION: Imports                                                           
# =========================================================================== #
# standard:
import cv2
import numpy as np
import time
import os

# local:
import ShapeAnalysis
# =========================================================================== #
#  SECTION: Global definitions
# =========================================================================== #
# path of the taken photo of nao
FILENAME = "Testbilder/photo_test6_3.jpg"

# range of red colors
LOWER_RED = np.array([170, 50, 50])
UPPER_RED= np.array([180, 255, 255])

# =========================================================================== #
#  SECTION: Function definitions
# =========================================================================== #
def read_image(fileName:str)->np.array:
    """read in the the image file to work with it in the scipt

    Parameters
    ----------
    fileName : str
        relative path of the image

    Returns
    -------
    np.array
        3D matrix based on the colors in the image
    """
    #make the path absolute without adding the file name of the current script
    path = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(path, fileName)
    return cv2.imread(image_path)


def find_red_dots(img:np.array, debug=True)->dict:
    """finding red dots on an image

    Parameters
    ----------
    img : np.array
        3D matrix based on the colors in the image

    Returns
    -------
    dict
        dict of the coordinates for every red dot
        key: number from 1 to n, with n amount of found red dots
        value: coordinate of the red dot [numpy array]
    """
    #Read in image and resize
    img = cv2.resize(img, (1500, 1000))
    
    #convert image from BGR into HSV color space (the red color is here bright)
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    #filter all parts within the red spectrum
    mask = cv2.inRange(hsv_img, LOWER_RED, UPPER_RED)
    
    #reduce the image to the "red parts"
    res, thresh_img = cv2.threshold(
        mask, 210, 255, cv2.THRESH_BINARY_INV)
    
    #find the position of the contours
    contours, hierarchy = cv2.findContours(
        thresh_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    
    count = 0
    points = dict()
    for c in contours:
        area = cv2.contourArea(c)
        if area > 1 and area < 250:
            (x, y), radius = cv2.minEnclosingCircle(c)
            center = (int(x), int(y))
            points[count] = center
            count += 1
            radius = int(radius)
            img = cv2.circle(img, center, radius, (0, 255, 0), 10)
            cv2.circle(img, center, radius, (0, 255, 0), 10)
            x, y, w, h = cv2.boundingRect(c)
    if debug:
        debug = img.copy()
        debug = cv2.resize(debug, (750, 500))
        cv2.imshow('test', debug)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return points


def find_paper(img: np.array) -> np.array:
    """
    finding the paper/game board in the image and cropping the unecessary stuff

    Parameters
    ----------
    img : np.array
        image

    Returns
    -------
    np.array
        resized cropped image
    """
    # convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # threshold
    thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)[1]\
    # apply morphology
    kernel = np.ones((7, 7), np.uint8)
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    kernel = np.ones((9, 9), np.uint8)
    morph = cv2.morphologyEx(morph, cv2.MORPH_ERODE, kernel)
    # get largest contour
    contours = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    area_thresh = 0
    for c in contours:
        area = cv2.contourArea(c)
        if area > area_thresh:
            area_thresh = area
            big_contour = c
    # get bounding box
    x, y, w, h = cv2.boundingRect(big_contour)
    # draw filled contour on black background
    mask = np.zeros_like(gray)
    mask = cv2.merge([mask, mask, mask])
    cv2.drawContours(mask, [big_contour], -1, (255, 255, 255), cv2.FILLED)
    # apply mask to input
    result = img.copy()
    result = cv2.bitwise_and(result, mask)
    # crop result
    return result
 
 
def cut_rectangles(img:np.array, edges:list, count:int, debug=False):
    """
    cut out the single rectangles and save them into new images

    Parameters
    ----------
    img : np.array
        image
    edges : list
        list of points that representing the corners of the rectangle
    count : int
        increasing number for each found rectangle
    debug : bool, optional
        if True saves image where the found rectangle boarders are marked, by default False
    """
    original_image_copy = img.copy()
    pts = np.array(edges).astype(np.int)
    ## (1) Crop the bounding rect
    rect = cv2.boundingRect(pts)
    x, y, w, h = rect
    croped = original_image_copy[y:y+h, x:x+w]
    
    ## (2) make mask
    pts2 = pts - pts.min(axis=0)
    mask = np.zeros(croped.shape[:2], np.uint8)
    cv2.drawContours(mask, [pts2], -1, (255, 255, 255), -1, cv2.LINE_AA)
    
    ## (3) do bit-op
    dst = cv2.bitwise_and(croped, croped, mask=mask)
    
    ## (4) save images
    path = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(path, "cutouts/roi")
    
    cv2.imwrite(image_path+str(count)+".jpg", dst)
    
    if debug:
        image_path = os.path.join(path, "cutouts/debug")
        # Blue color in BGR
        color = (255, 0, 0)
        # Line thickness of 2 px
        thickness = 2
        image = cv2.polylines(img.copy(), [pts], True, color, 8)
        cv2.imwrite(image_path + str(count)+".jpg", image)
        cv2.imshow('test',image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    size = dst.shape
    area = size[0]*size[1]
    return area

def warp_perspektive(img:np.array, corners:list)->np.array:
    """
    warpes the perspective of the image with the information of the 
    red dot corners (needs corners to function!!!)

    Parameters
    ----------
    img : np.array
        image to warp
    corners : list
        list of the corner coordinates

    Returns
    -------
    np.array
        warped image
    """
    
    #TODO questionable coordinate order
    pt_A = corners['D']
    pt_B = corners['A']
    pt_C = corners['B']
    pt_D = corners['C']
    
    # L2 norm
    width_AD = np.sqrt(((pt_A[0] - pt_D[0]) ** 2) + ((pt_A[1] - pt_D[1]) ** 2))
    width_BC = np.sqrt(((pt_B[0] - pt_C[0]) ** 2) + ((pt_B[1] - pt_C[1]) ** 2))
    maxWidth = max(int(width_AD), int(width_BC))

    height_AB = np.sqrt(((pt_A[0] - pt_B[0]) ** 2) + ((pt_A[1] - pt_B[1]) ** 2))
    height_CD = np.sqrt(((pt_C[0] - pt_D[0]) ** 2) + ((pt_C[1] - pt_D[1]) ** 2))
    maxHeight = max(int(height_AB), int(height_CD))
        
    input_pts = np.float32([pt_A, pt_B, pt_C, pt_D])

    output_pts = np.float32([[10, 10],
                             [10, maxHeight - 10],  
                             [maxWidth - 10, maxHeight - 10],
                             [maxWidth - 10, 10]])
    # Compute the perspective transform M
    M = cv2.getPerspectiveTransform(input_pts, output_pts)
    img_copy = np.copy(img)
    out = cv2.warpPerspective(
        img_copy, M, (maxWidth, maxHeight), flags=cv2.INTER_LINEAR)
    return cv2.resize(out, (1500, 1000))

def check_cutouts(sizes:list()):
    #TODO define consequence, wenn std above 10%
    np_sizes = np.array(sizes)
    mean = np.mean(np_sizes)
    std = ShapeAnalysis.round_data(data=np.std(np_sizes)/mean*100,digits =2)[0]
    print(f"The cutouts have a standard deviation of {std} %")
    if int(std)>=10:
        pass
        
def seperate_the_objects(fileName:str):
    """
    seperates the rectangle shapes from the game board image

    Parameters
    ----------
    fileName : str
        path of the board game image 
    """
    begin = time.time()
    #Read in image and rezize
    img = read_image(fileName)
    #warp_perspektive(img)
    try:
        img = cv2.resize(img, (1500, 1000))
        # Find paper and resize
        paper = find_paper(img)
        # Find red dots
        points = find_red_dots(paper)
        Shape = ShapeAnalysis.Grid(points)
        #quit()
        # warp the perspektive
        warped = warp_perspektive(img, Shape.corners)
        points = find_red_dots(warped)
        # find the new coordinates out of the warped photov
        new_points = find_red_dots(warped)
        Shape.set_coordinates(new_points)
        # find rectangles
        rectangles = Shape.find_rectangles()
        sizes = list()
        for key in rectangles:
            sizes.append(cut_rectangles(warped, rectangles[key], key))
        
        check_cutouts(sizes)
            
    except Exception as e:
        print('error:')
        print(str(e))
    print(float(time.time()-begin))
    
# =========================================================================== #
#  SECTION: Main Body                                                         
# =========================================================================== #

if __name__ == '__main__':
    seperate_the_objects(FILENAME)
    
