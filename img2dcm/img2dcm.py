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
import SimpleITK as sitk
import pydicom as dicom
import glob
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


    NAME

       img2dcm

    SYNOPSIS

        docker run --rm fnndsc/pl-img2dcm img2dcm                       \\
            [-i|--inputImageFilter <imageFilter>]                       \\
            [-d|--inputDCMFilter <dicomFilter>]                         \\
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
                fnndsc/pl-img2dcm img2dcm                           \
                /incoming /outgoing

    DESCRIPTION

        `img2dcm` ...

    ARGS
        [-i|--inputImageFilter <imageFilter>]
        A glob pattern string, default is "**/*.png", representing the input
        file pattern to analyze.
    
        [-d|--inputDCMFilter <dicomFilter>]
        A glob pattern string, default is "**/*.dcm", representing the input
        dicom files to fetch tags.
 
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
        
        self.add_argument(  '--inputImageFilter','-i',
                            dest         = 'inputImageFilter',
                            type         = str,
                            optional     = True,
                            help         = 'Input image file filter',
                            default      = '**/*.png')
                            
        self.add_argument(  '--inputDCMFilter','-d',
                            dest         = 'inputDCMFilter',
                            type         = str,
                            optional     = True,
                            help         = 'Input dicom file filter',
                            default      = '**/*.dcm')

    def run(self, options):
        """
        Define the code to be run by this plugin app.
        """
        print(Gstr_title)
        print('Version: %s' % self.get_version())
        no_include_tags = ['BitsAllocated',
                           'BitsStored',
                           'PixelData',
                           'PixelIntensityRelationship',
                           'PixelIntensityRelationshipSign',
                           'PixelRepresentation',
                           'PixelSpacing',
                           'PixelSpacingCalibrationDescription',
                           'PixelSpacingCalibrationType',
                           'SamplesPerPixel',
                           'SeriesInstanceUID',
                           'PhotometricInterpretation',
                           'Rows',
                           'Columns']
                           
        img_str_glob = '%s/%s' % (options.inputdir,options.inputImageFilter)        
        l_img_datapath = glob.glob(img_str_glob, recursive=True)
        
        dcm_str_glob = '%s/%s' % (options.inputdir,options.inputDCMFilter)        
        l_dcm_datapath = glob.glob(dcm_str_glob, recursive=True)
        
        for img_datapath in l_img_datapath:
            img_file_name = img_datapath.split('/')[-1]
            img_file_stem = img_file_name.split('.png')[0]
            temp_dcm_file = os.path.join('/tmp',img_file_stem + '.dcm')
            img = sitk.ReadImage(img_datapath)
            writer = sitk.ImageFileWriter()
            writer.SetFileName(temp_dcm_file)
            writer.Execute(img)
            
            
            
            for dcm_datapath in l_dcm_datapath:
                if img_file_stem in dcm_datapath:
                    dcm_image = dicom.dcmread(dcm_datapath)
                    tmp_dcm_image = dicom.dcmread(temp_dcm_file)
                    print("Setting file meta information...")
                    for item in dcm_image.dir():
                        if item not in no_include_tags:
                            tmp_dcm_image[item] = dcm_image[item]
                    print("Setting Series Instance UID")
                    tmp_dcm_image.SeriesInstanceUID = dicom.uid.generate_uid()
                    print("Writing dicom file", img_file_stem+".dcm")
                    tmp_dcm_image.save_as(os.path.join(options.outputdir,img_file_stem+".dcm"))
                    print("File saved.")
        
             

    def show_man_page(self):
        """
        Print the app's man page.
        """
        print(Gstr_synopsis)
