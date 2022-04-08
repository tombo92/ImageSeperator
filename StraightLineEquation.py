#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2021-04-14 14:57:35
# @Author  : Tom Brandherm (tom.brandherm@msasafety.com)
# @Link    : link
# @Version : 1.0.0
"""
Straight line equation in two dimensional context: vec(f)(t)=vec(a)*t+vec(b) 
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

import math
import numpy as np

# =========================================================================== #
#  SECTION: Global definitions
# =========================================================================== #

# =========================================================================== #
#  SECTION: Function definitions
# =========================================================================== #

# =========================================================================== #
#  SECTION: Class definitions
# =========================================================================== #


class StraightLineEquation(object):
    counter : int = 1
    # ----------------------------------------------------------------------- #
    #  SUBSECTION: Constructor
    # ----------------------------------------------------------------------- #

    def __init__(self, a: np.array, b: np.array):
        """
        create new straight line equation out of two points (2D-vectors) 
        Parameters
        ----------
        a : numpy array
            start point (x,y)
        b : numpy array
            end point (x,y)
        """
        # start point is the new support vector
        self.__supportVector = a
        # calculate direction vector via b - a 
        self.__directionVector = b-a
        # increment the instance counter
        self.counter = StraightLineEquation.counter
        StraightLineEquation.counter +=1
        
        
    # ----------------------------------------------------------------------- #
    #  SUBSECTION: Getter/Setter
    # ----------------------------------------------------------------------- #
    def get_supportVektor(self):
        return self.__supportVector

    def get_directionVector(self):
        return self.__directionVector
    

    def get_equation(self):
        print("New equation: g{0}: x(t)={1}t+{2}".format(self.counter,
                                                         self.__directionVector, 
                                                         self.__supportVector))
    # ----------------------------------------------------------------------- #
    #  SUBSECTION: Public Methods
    # ----------------------------------------------------------------------- #
    def check_points(self, otherPoints:dict, yErr:float)->list:
        """
        Check which of the found points are in line with the two points that are 
        defining the straight line equation

        Parameters
        ----------
        otherPoints : dict
            dict of all found points with a tuple of x and y coordiantes
        yErr : float
            maximal difference between the y-value of the calculated straight line
            equation and the point
        Returns
        -------
        list
            list of bools: the position is linked to the dictionary keys and true if
            the point is in line 
        """
        listOfTruth = list()
        #check which of the points is in that range
        for key in otherPoints:
            x = otherPoints[key][0]
            y = otherPoints[key][1]
            #error range by shifting the y value of the support vector +/- value
            yMin, yMax = self.__get_error_range(x, yErr)
            #check if y value is in that range
            in_between = yMin <= y and y <= yMax
            if in_between:
                listOfTruth.append(True)
            else:
                listOfTruth.append(False)
        return listOfTruth
                
    def calculate(self, t: float) -> np.array:
        """
        calculate a new point by using the straight line equation
        Parameters
        ----------
        t : float
            variable to shift into the direction of the directional vector

        Returns
        -------
        np.array
            calculated point on the line
        """
        a = self.__directionVector
        b = self.__supportVector
        return a*t+b

    def calculate_t(self, x_value:float, a:np.array, b:np.array)->float:
        """
        calculate the variable t of the equation g: x(t)=a+b*t by giving points
        a, b and x. Only the x and not the y value is used in the calculation.

        Parameters
        ----------
        x_value : float
            x value 
        a : np.array
            support vector
        b : np.array
            directional vector

        Returns
        -------
        float
            variable t the shifts the directional vector from the support vector
            to the giving x value
        """
        return (x_value - b[0])/a[0]
    
    def calculate_coord_in_distance(self, refCoord:np.array, d:float)->np.array:
        """
        Calculate the coordiantes in a given distance from a reference point.
        the new coordinates are still on the straight line equation. 

        Parameters
        ----------
        refCoord : np.array
            reference point
        d : float
            distance from the reference point

        Returns
        -------
        np.array
            new coordinates
        """
        a1, a2 = self.__seperate_2Dvector(self.__directionVector)
        b1, b2 = self.__seperate_2Dvector(self.__supportVector)
        x, y = self.__seperate_2Dvector(refCoord)
        # calculate the single constants c
        c1 = a1**2 + a2**2
        c2 = (a1*(x-b1)+a2*(y-b2)) / c1
        c3 =  ((b1-x)**2 + (b2-y)**2 - d**2) / c1
        c4 = c2**2 - c3
        # calculate t from the pq-formula
        t = c2 + np.sqrt(c4)
        # calculate the new coordinates out of the calculated t
        return self.calculation(t, self.__directionVector, self.__supportVector)
        

    # ----------------------------------------------------------------------- #
    #  SUBSECTION: Private Methods
    # ----------------------------------------------------------------------- #
    def __calculate_angle(self, a:np.array,b:np.array)->float:
        """
        calculate angle between the straight line equation and the x axis
        Parameters
        ----------
        a : np.array
            support vector
        b : np.array
            directional vector

        Returns
        -------
        float
            angle between straight line equation and the x axis in degree
        """
        dX = b[0]-a[0]
        dY = b[1]-a[1]
        angle_in_radians = math.atan(dY/dX)      
        angle_in_degrees = math.degrees(angle_in_radians)
        return angle_in_degrees

    
    def __get_error_range(self, x:float, yErr:float)->tuple:
        """
        calculate the upper and lower y value to know if the analaysed 
        point is into the acceptable range or not.

        Parameters
        ----------
        x : float
            x value of the analysed point
        yErr : float
            defined acceptable y error range 

        Returns
        -------
        tuple
            lower bound, upper bound
        """
        shift = np.asarray((0, yErr))
        # shifting the support vector in both directions
        upper_supportVector = self.__supportVector + shift
        lower_supportVector = self.__supportVector - shift
        # calculate the upper t value 
        tMax = self.calculate_t(
            x, self.__directionVector, upper_supportVector)
        # use the upper t value to calculate the upper y value for the range
        yMax = self.calculation(
            tMax, self.__directionVector, upper_supportVector)[1]
        # same for lower t and y
        tMin = self.calculate_t(
            x, self.__directionVector, lower_supportVector)
        yMin = self.calculation(
            tMin, self.__directionVector, lower_supportVector)[1]
        return yMin, yMax

    def __seperate_2Dvector(self, vector:np.array)->tuple:
        return vector.item(0), vector.item(1)
        
# =========================================================================== #
#  SECTION: Main Body                                                         
# =========================================================================== #

if __name__ == '__main__':
    pass


