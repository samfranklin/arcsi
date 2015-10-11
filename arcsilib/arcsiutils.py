"""
Module that contains the ARCSIUtils class.
"""
############################################################################
#  arcsiutils.py
#
#  Copyright 2013 ARCSI.
#
#  ARCSI: 'Atmospheric and Radiometric Correction of Satellite Imagery'
#
#  ARCSI is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  ARCSI is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with ARCSI.  If not, see <http://www.gnu.org/licenses/>.
#
#
# Purpose:  A class with some useful utilites.
#
# Author: Pete Bunting
# Email: pfb@aber.ac.uk
# Date: 05/07/2013
# Version: 1.0
#
# History:
# Version 1.0 - Created.
#
############################################################################

# Import the ARCSI exception class
from .arcsiexception import ARCSIException
# Import the OS python module
import os
# Import the OSGEO GDAL module
import osgeo.gdal as gdal
# Import the numpy library
import numpy

class ARCSIUtils (object):
    """
    A class with useful utilties for the ARCSI System.
    """
    
    def getFileExtension(self, format):
        ext = ".NA"
        if format.lower() == "kea":
            ext = ".kea"
        elif format.lower() == "gtiff":
            ext = ".tif"
        elif format.lower() == "hfa":
            ext = ".img"
        elif format.lower() == "envi":
            ext = ".env"
        else:
            raise ARCSIException("The extension for the format specified is unknown.")
        return ext
        
    def readTextFile(self, file):
        """
        Read a text file into a single string
        removing new lines.
        """
        txtStr = ""
        try:
            dataFile = open(file, 'r')
            for line in dataFile:
                txtStr += line.strip()
            dataFile.close()
        except Exception as e:
            raise e
        return txtStr
    
    def stringTokenizer(self, line, delimiter):
        tokens = list()
        token = str()
        for i in range(len(line)):
            if line[i] == delimiter:
                tokens.append(token)
                token = str()
            else:
                token = token + line[i]
        tokens.append(token)
        return tokens
        
    def readSpectralResponseFunc(self, inFile, seperator, ignoreLines, waveCol, respCol):
        specResp = list()
        try:
            specFile = open(inFile, 'r')
            lineCount = 0
            for line in specFile:
                if lineCount >= ignoreLines:
                    line = line.strip()
                    if line:
                        lineVals = line.split(seperator)
                        if (len(lineVals) <= waveCol) or (len(lineVals) <= respCol):
                            raise ARCSIException("")
                        waveVal = float(lineVals[waveCol].strip())
                        respVal = float(lineVals[respCol].strip())
                        specResp.append([waveVal,respVal])
                lineCount += 1
            specFile.close()
        except ARCSIException as e:
            raise e
        except Exception as e:
            raise e
        return numpy.array(specResp)
    
    def isSummerOrWinter(self, lat, long, date):
        summerWinter = 0
        if lat < 0:
            # Southern Hemisphere
            print("Southern Hemisphere")
            if (date.month > 4) & (date.month < 11):
                summerWinter = 2 # Winter
            else:
                summerWinter = 1 # Summer
        else: 
            # Northern Hemisphere
            print("Northern Hemisphere")
            if (date.month > 3) & (date.month < 10):
                summerWinter = 1 # summer
            else:
                summerWinter = 2 # Winter
        return summerWinter
        
    def getEnvironmentVariable(self, var):
        outVar = None
        try:
            outVar = os.environ[var]
            #print(outVar)
        except Exception:
            outVar = None
        return outVar

    def setImgThematic(self, imageFile):
        ds = gdal.Open(imageFile, gdal.GA_Update)
        for bandnum in range(ds.RasterCount):
            band = ds.GetRasterBand(bandnum + 1)
            band.SetMetadataItem('LAYER_TYPE', 'thematic')
        ds = None
        
    def copyGCPs(self, srcImg, destImg):
        srcDS = gdal.Open(srcImg, gdal.GA_ReadOnly)     
        if srcDS == None:
            raise ARCSIException("Could not open the srcImg.")
        destDS = gdal.Open(destImg, gdal.GA_Update)
        if destDS == None:
            raise ARCSIException("Could not open the destImg.")
            srcDS = None
        
        numGCPs = srcDS.GetGCPCount()
        if numGCPs > 0:
            gcpProj = srcDS.GetGCPProjection()
            gcpList = srcDS.GetGCPs()
            destDS.SetGCPs(gcpList, gcpProj)
                
        srcDS = None
        destDS = None

class ARCSILandsatMetaUtils(object):
    """
    A class with common functions for parsing Landsat
    metadata
    """

    @staticmethod
    def getGeographicCorners(headerParams):
        """
        Function to get geographic coordinates of image from metatdata

        Returns array containing:

        * UL_LON
        * UL_LAT
        * UR_LON
        * UR_LAT
        * LL_LAT
        * LL_LON
        * LR_LAT
        * LR_LON

        """
        outCornerCoords = []
        geoVarList = [["UL","LAT"],
                      ["UL","LON"],
                      ["UR","LAT"],
                      ["UR","LON"],
                      ["LL","LAT"],
                      ["LL","LON"],
                      ["LR","LAT"],
                      ["LR","LON"]]

        for geoItem in geoVarList:
            try:
                outCornerCoords.append(float(headerParams["CORNER_{0}_{1}_PRODUCT".format(geoItem[0],geoItem[1])]))
            except KeyError:
                outCornerCoords.append(float(headerParams["PRODUCT_{0}_CORNER_{1}".format(geoItem[0],geoItem[1])]))

        return outCornerCoords

    @staticmethod
    def getProjectedCorners(headerParams):
        """
        Function to get projected coordinates of image from metatdata

        Returns array containing:

        * UL_X
        * UL_Y
        * UR_X
        * UR_Y
        * LL_X
        * LL_Y
        * LR_X
        * LR_Y

        """
        outCornerCoords = []
        projectedVarList =  [["UL","X"],
                             ["UL","Y"],
                             ["UR","X"],
                             ["UR","Y"],
                             ["LL","X"],
                             ["LL","Y"],
                             ["LR","X"],
                             ["LR","Y"]]

        for projectedItem in projectedVarList:
            try:
                outCornerCoords.append(float(headerParams["CORNER_{0}_PROJECTION_{1}_PRODUCT".format(projectedItem[0],projectedItem[1])]))
            except KeyError:
                outCornerCoords.append(float(headerParams["PRODUCT_{0}_CORNER_MAP{1}".format(projectedItem[0],projectedItem[1])]))

        return outCornerCoords

    @staticmethod
    def getBandFilenames(headerParams, nBands):
        """
        Get filenames for individual bands

        Returns a list with a name for each band.
        """
        metaFilenames = []
        
        for i in range(1,nBands+1):
            try:
                metaFilenames.append(headerParams["FILE_NAME_BAND_{}".format(i)])
            except KeyError:
                try:
                    metaFilenames.append(headerParams["BAND{}_FILE_NAME".format(i)])
                # For Landsat 7 ETM+ There are two band 6 files.
                # Just set to 'None' here and fetch separately.
                except Exception:
                    if i == 6:
                        metaFilenames.append(None)
                    else:
                        raise

        return metaFilenames

