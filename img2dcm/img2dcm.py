#
# img2dcm ds ChRIS plugin app
#
# (c) 2022 Fetal-Neonatal Neuroimaging & Developmental Science Center
#                   Boston Children's Hospital
#
#              http://childrenshospital.org/FNNDSC/
#                        dev@babyMRI.org
#

from chrisapp.base import ChrisApp
import os
import sys
import time
import SimpleITK as sitk
import pydicom as dicom
import glob
import numpy as np
from PIL import Image
from pydicom import dcmread

Gstr_title = r"""
 _                  _____     _                
(_)                / __  \   | |               
 _ _ __ ___   __ _ `' / /' __| | ___ _ __ ___  
| | '_ ` _ \ / _` |  / /  / _` |/ __| '_ ` _ \ 
| | | | | | | (_| |./ /__| (_| | (__| | | | | |
|_|_| |_| |_|\__, |\_____/\__,_|\___|_| |_| |_|
              __/ |                            
             |___/                             
"""

Gstr_synopsis = """

(Edit this in-line help for app specifics. At a minimum, the 
flags below are supported -- in the case of DS apps, both
positional arguments <inputDir> and <outputDir>; for FS and TS apps
only <outputDir> -- and similarly for <in> <out> directories
where necessary.)

    NAME

       img2dcm

    SYNOPSIS

        docker run --rm fnndsc/pl-img2dcm img2dcm                     \\
            [-h] [--help]                                               \\
            [--json]                                                    \\
            [--man]                                                     \\
            [--meta]                                                    \\
            [--savejson <DIR>]                                          \\
            [-v <level>] [--verbosity <level>]                          \\
            [--version]                                                 \\
            <inputDir>                                                  \\
            <outputDir> 

    BRIEF EXAMPLE

        * Bare bones execution

            docker run --rm -u $(id -u)                             \
                -v $(pwd)/in:/incoming -v $(pwd)/out:/outgoing      \
                fnndsc/pl-img2dcm img2dcm                        \
                /incoming /outgoing

    DESCRIPTION

        `img2dcm` ...

    ARGS

        [-h] [--help]
        If specified, show help message and exit.
        
        [--json]
        If specified, show json representation of app and exit.
        
        [--man]
        If specified, print (this) man page and exit.

        [--meta]
        If specified, print plugin meta data and exit.
        
        [--savejson <DIR>] 
        If specified, save json representation file to DIR and exit. 
        
        [-v <level>] [--verbosity <level>]
        Verbosity level for app. Not used currently.
        
        [--version]
        If specified, print version number and exit. 
"""


class Img2dcm(ChrisApp):
    """
    An app to convert an input image to a DICOM file
    """
    PACKAGE                 = __package__
    TITLE                   = 'A image to DICOM converter'
    CATEGORY                = ''
    TYPE                    = 'ds'
    ICON                    = ''   # url of an icon image
    MIN_NUMBER_OF_WORKERS   = 1    # Override with the minimum number of workers as int
    MAX_NUMBER_OF_WORKERS   = 1    # Override with the maximum number of workers as int
    MIN_CPU_LIMIT           = 2000 # Override with millicore value as int (1000 millicores == 1 CPU core)
    MIN_MEMORY_LIMIT        = 8000  # Override with memory MegaByte (MB) limit as int
    MIN_GPU_LIMIT           = 0    # Override with the minimum number of GPUs as int
    MAX_GPU_LIMIT           = 0    # Override with the maximum number of GPUs as int

    # Use this dictionary structure to provide key-value output descriptive information
    # that may be useful for the next downstream plugin. For example:
    #
    # {
    #   "finalOutputFile":  "final/file.out",
    #   "viewer":           "genericTextViewer",
    # }
    #
    # The above dictionary is saved when plugin is called with a ``--saveoutputmeta``
    # flag. Note also that all file paths are relative to the system specified
    # output directory.
    OUTPUT_META_DICT = {}

    def define_parameters(self):
        """
        Define the CLI arguments accepted by this plugin app.
        Use self.add_argument to specify a new app argument.
        """

    def run(self, options):
        """
        Define the code to be run by this plugin app.
        """
        print(Gstr_title)
        print('Version: %s' % self.get_version())
        img = sitk.ReadImage(image_path)

        writer = sitk.ImageFileWriter()
        writer.KeepOriginalImageUIDOn()
        writer.SetFileName('png2dcm.dcm')
        writer.Execute(img)
        # dummy image

        image = pydicom.dcmread('/home/sandip/image2.dcm')
        img1 = pydicom.dcmread('/home/sandip/Downloads/chris_feed_211_pl-dircopy_1687_data_chris_feed_210_pl-        dircopy_1683_data_SERVICES_PACS_PACSDCM_4346815-AKIKI_MOUNIR-20090218_PACSDCM_4346815-AKIKI_MOUNIR-20090218_XR-        Hips_to_Ankles_No_Ruler_-26348628-20220105-012Y-004704d_16.dcm')

        print("Setting file meta information...")
        for item in img1.dir():
            image[item] = img1[item]





        print("Writing test file", "image.dcm")
        image.save_as("image.dcm")
        print("File saved.")

    def show_man_page(self):
        """
        Print the app's man page.
        """
        print(Gstr_synopsis)