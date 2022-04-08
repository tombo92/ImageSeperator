#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2021-04-14 14:57:35
# @Author  : Tom Brandherm (s_brandherm19@stud.hwr-berlin.de)
# @Link    : link
# @Version : 1.0.0
"""
Class for analysing the shape of a random number and position of found points.
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
import numpy as np
import math

# local:
import StraightLineEquation as sle
# =========================================================================== #
#  SECTION: Global definitions
# =========================================================================== #
# find nearest neighbour, but exclude same point
MINIMAL_DISTANCE = 100
# amount of red dots in one horizantal line
DOTS_IN_LINE = 6

# =========================================================================== #
#  SECTION: Class definitions
# =========================================================================== #


class Grid(object):
    """
    Grid of coordinates
    """

    # ----------------------------------------------------------------------- #
    #  SUBSECTION: Constructor
    # ----------------------------------------------------------------------- #

    def __init__(self, coordinates:dict):
        # dict of tuples with (x,y)
        self.__coordiantes = self.__clustering(coordinates)
        # total number of found points
        self.__knots = len(coordinates)
        # corners
        self.corners = self.__sort_corners()

    # ----------------------------------------------------------------------- #
    #  SUBSECTION: Getter/Setter
    # ----------------------------------------------------------------------- #

    def get_coordinates(self):
        return self.__coordiantes

    def get_knots(self):
        return self.__knots

    def set_coordinates(self, coordinates):
        self.__coordiantes = self.__clustering(coordinates)
        self.corners = self.__sort_corners()

    # ----------------------------------------------------------------------- #
    #  SUBSECTION: Public Methods
    # ----------------------------------------------------------------------- #
    def find_rectangles(self)->dict:
        """
        Find the corners of every rectangle on the game board.
        Returns
        -------
        dict
            dictionay of lists of corner points for each found rectangle
        """
        # FIRST STEP:
        # Fill the matrix with all the found points in the correct order
        # each element represents one row on the game board
        matrix = self.__calculate_missing_knots()
        # SECOND STEP:
        # Iterate through the (3x6) matrix to sort the points to
        # corners of rectangles

        rectangles = dict()
        for j in range(2):
            for i in range(DOTS_IN_LINE-1):
                rectangle = list()
                rectangle.append(matrix[j+1][i+1])
                rectangle.append(matrix[j][i+1])
                rectangle.append(matrix[j][i])
                rectangle.append(matrix[j+1][i])

                rectangles[i+5*j] = rectangle
        return rectangles


    # ----------------------------------------------------------------------- #
    #  SUBSECTION: Private Methods
    # ----------------------------------------------------------------------- #
    def __convert_dict(self):
        """convert the dict values into a matrix (numpy array)
        Returns
        -------
        [numpy array]
            numpy array of the dict values
        """
        result = self.__coordiantes.values()
        data = list(result)
        return np.array(data)


    def __calculate_angle(self, vec1, vec2):
        """calculate the angle between two sensors in degree

        Parameters
        ----------
        vec1 : [1D numpy array]
            vector
        vec2 : [1D numpy array]
            vector

        Returns
        -------
        [float]
            angle between the two vectors
        """
        unit_vector_vec1 = vec1/np.linalg.norm(vec1)
        unit_vector_vec2 = vec2/np.linalg.norm(vec2)
        dot_product = np.dot(unit_vector_vec1, unit_vector_vec2)
        return math.degrees(np.arccos(dot_product))


    def __calculate_distances(self):
        """calculate the distance between every point and save it into a distance matrix D

        Returns
        -------
        [2D numpy array]
            distance matrix:
                        vec1                vec2            ...     vecn
                vec1    0               d(vec1, vec2)       ...     d(vec1,vecn)
                vec2    d(vec1, vec2)       0               ...     d(vec2,vecn)
                ...     ...                 ...             ...       ...
                vecn    d(vecn, vec1)   d(vecn,vec2)        ...     0
        """
        n = self.__knots
        #reshape matrix to iterable array, every row represents the x and y coordinate of a red dot
        matrix = self.__convert_dict().reshape(n, 2)
        #distance matrix
        D = np.zeros((n,n))
        for i, vector1 in enumerate(matrix):
            for j, vector2 in enumerate(matrix):
                #euclidean distance between two vectors
                if i != j:
                    dist = np.linalg.norm(vector1-vector2)
                    D[i,j] = dist
        return D


    def __calculate_angles(self):
        """calculate the angle between every point and save it into a angle matrix A

        Returns
        -------
        [2D numpy array]
            distance matrix:
                        vec1                vec2            ...     vecn
                vec1    0               a(vec1, vec2)       ...     a(vec1,vecn)
                vec2    a(vec1, vec2)       0               ...     a(vec2,vecn)
                ...     ...                 ...             ...      ...
                vecn    a(vecn, vec1)   a(vecn,vec2)        ...     0
        """
        n = self.__knots
        #reshape matrix to iterable array, every row represents the x and y coordinate of a red dot
        matrix = self.__convert_dict().reshape(n, 2)
        #angle matrix
        A = np.zeros((n, n))
        for i, vector1 in enumerate(matrix):
            for j, vector2 in enumerate(matrix):
                #angle between two vectors, unnecessary for same vectors
                if i != j:
                    angle = self.__calculate_angle(vector1, vector2)
                    A[i, j] = angle
        return A


    def __clustering(self, coords: dict) -> dict:
        """
        Cluster the coordinates by the distance. Are two ore more coordinates
        in a radial distance range of the given minimal distance there a forming
        one cluster.

        Parameters
        ----------
        coords : list
            list of points

        Returns
        -------
        dict
            dict of four corner coordintates
        """
        coords = list(coords.values())
        cluster = {1:[], 2: [], 3:[],4:[]}
        new_coords = list()
        for key in range(1,5):
            for i, coord in enumerate(coords):
                if i == 0:
                    cluster[key].append(coord)
                else:
                    vector1 = np.asarray(cluster[key][0])
                    vector2 = np.asarray(coord)
                    dist = np.linalg.norm(vector1-vector2)
                    if dist < MINIMAL_DISTANCE:
                        cluster[key].append(coord)
                    else:
                        new_coords.append(coord)
            coords=new_coords
            new_coords = []
            # calculating the mean of the x and the y value of all coordinates
            # in one cluster. the result is one statistical center point
            cluster[key] = self.__find_center(cluster[key])
        return cluster


    def __find_center(self, coords:list)->tuple:
        """
        calculating the mean of the x and y value for a list of tuple coordinates

        Parameters
        ----------
        coords : list
            list of tuple like coordinates

        Returns
        -------
        tuple
            (mean x, mean y)
        """
        X = 0
        Y = 0
        n = len(coords)
        for coord in coords:
            X += coord[0]
            Y += coord[1]

        mean_X = round(X/n)
        mean_Y = round(Y/n)
        return (mean_X, mean_Y)


    def __sort_corners(self)->dict:
        """
        find the corners from the "rectangular" shaped grid:

        A-------D\n
        |       |\n
        B-------C\n

        Returns
        -------
        dict
            4 corner coordinates
        """
        ###### 1.Step
        # find corner C and A by summing up the y and y values and using the one with the
        # biggest sum value for C and the lowest for A
        max_sum_val = 0
        min_sum_val = 0
        coords = list(self.__coordiantes.values())
        for coord in coords:
            sum_value = coord[0] + coord[1]
            if sum_value>max_sum_val:
                max_sum_val=sum_value
                min_sum_val=sum_value
                C = coord
            elif sum_value<min_sum_val:
                min_sum_val=sum_value
                A = coord
        coords.remove(A)
        coords.remove(C)
        ###### 2.Step
        # determine B and D
        if check_inBetween(coords[0][0], A[0]+MINIMAL_DISTANCE, A[0]-MINIMAL_DISTANCE):
            B = coords[0]
            D = coords[1]
        else:
            D = coords[0]
            B = coords[1]
        return {'A':A,'B':B,'C':C,'D':D}


    def __calculate_missing_knots(self)->np.array:
        """
        Calculating the missing knots out of the symmetrie
        and the 4 corner coordinates.

        Returns
        -------
        np.array
            3x6 matrix with all coordinates
        """
        # convert the tuple coordinates into numpy arrays
        vectorA = np.asarray(self.corners['A'])
        vectorB = np.asarray(self.corners['B'])
        vectorC = np.asarray(self.corners['C'])
        vectorD = np.asarray(self.corners['D'])
        # creating straight line equations out of the given symmetrie
        upper_h = sle.StraightLineEquation(vectorD, vectorA)
        lower_h = sle.StraightLineEquation(vectorC, vectorB)
        left_v = sle.StraightLineEquation(vectorB, vectorA)
        right_v = sle.StraightLineEquation(vectorC, vectorD)
        middle_h = sle.StraightLineEquation(
            right_v.calculate(1/2), left_v.calculate(1/2))
        # calculating the missing coordinates and putting it into a matrix shape
        # the rows in the matrix are correspond to the horizontal lines in the grid
        coord_Matrix = [[],[],[]]
        for i in range(5, -1, -1):
            x1 = tuple(np.rint(upper_h.calculate(i/5)))
            coord_Matrix[0].append(x1)
            x2 = tuple(np.rint(middle_h.calculate(i/5)))
            coord_Matrix[1].append(x2)
            x3 = tuple(np.rint(lower_h.calculate(i/5)))
            coord_Matrix[2].append(x3)

        return coord_Matrix
# =========================================================================== #
#  SECTION: Function definitions
# =========================================================================== #
def check_inBetween(value: float, upper: float = 0, lower:float=0)->bool:
    """
    check if the value is in a specified range
    Parameters
    ----------
    value : float
        value to ckeck
    upper : float, optional
        upper limit, by default 0
    lower : float, optional
        lower limit, by default 0
    Returns
    -------
    bool
        is the value in the range
    """
    return lower <= value and value <= upper


def round_data(data, err=0, digits=-1) -> tuple:
    """
    round_data
    Round the data by using DIN 1333. The position of the first segnificant␣
    ,→digit of the error
    is used as the the last segnificant digit of the data. If the first␣
    ,→segnificant digit of the error
    is a 1 or 2, one more digit is added.
    Parameters
    ----------
    data : [float]
    floating number with inaccuracy
    err : [float, optional]
    floating number of the data inaccuracy
    Returns
    digits : [int, optional]
    if digits are set, the rounding is not made by DIN 1333
    the numbers will be returned with the wanted number of digits
    -------
    [tuple of str]
    [0] rounded data by DIN 1333
    [1] rounded error by DIN 1333
    """
    if digits >= -1:
        counter = 0
        for number in str(err).replace('.', ''):
            if number == '0':
                counter += 1
            elif number == '1' or number == '2':
                counter += 1
                break
            else:
                break
    else:
        counter = digits
    rounded_err = format(err, f'.{counter}f')
    rounded_data = format(data, f'.{counter}f')
    return rounded_data, rounded_err
# =========================================================================== #
#  SECTION: Main Body
# =========================================================================== #

if __name__ == '__main__':
    pass


