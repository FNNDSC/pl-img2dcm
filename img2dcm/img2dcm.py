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

        `img2dcm` is an app to convert an input image to a DICOM file

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
    TITLE                   = 'An image to DICOM converter'
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
        
        # Output the space of CLI
        d_options = vars(options)
        for k,v in d_options.items():
            print("%20s: %-40s" % (k, v))
        print("")
        
        # List of dicom tags to be ignore while copying from DICOM files
        no_include_tags = ['BitsAllocated',
                           'BitsStored',
                           'PixelData',
                           'PixelIntensityRelationship',
                           'PixelIntensityRelationshipSign',
                           'PixelRepresentation',

                           'PixelSpacingCalibrationDescription',
                           'PixelSpacingCalibrationType',
                           'SamplesPerPixel',
                           'SeriesInstanceUID',
                           'PhotometricInterpretation',
                           'Rows',
                           'Columns',
                           'CollimatorRightVerticalEdge',
                           'CollimatorLowerHorizontalEdge']
                           
        img_str_glob = '%s/%s' % (options.inputdir,options.inputImageFilter)        
        l_img_datapath = glob.glob(img_str_glob, recursive=True)
        
        dcm_str_glob = '%s/%s' % (options.inputdir,options.inputDCMFilter)        
        l_dcm_datapath = glob.glob(dcm_str_glob, recursive=True)  
        
        dcm_dirs = []
        for dcm_datapath in l_dcm_datapath:
            dcm_dirs.append(os.path.dirname(dcm_datapath))
            
        unique_dcm_dirs = set(dcm_dirs)
        
        
        for dcm_dir in unique_dcm_dirs:
            output_dirpath = dcm_dir.replace(options.inputdir,options.outputdir)
            os.makedirs(output_dirpath,exist_ok=True)
            
            unique_series_uid = dicom.uid.generate_uid()
            print(f"\n\nGenerated series instance uid is {unique_series_uid}")
            
            # traverse through all dicom files in this dir
            for file in glob.glob(dcm_dir + options.inputDCMFilter):
                dcm_image = dicom.dcmread(file)
                for img_datapath in l_img_datapath:
                    dcm_file_name = file.split('/')[-1]
                    dcm_file_stem = dcm_file_name.split('.dcm')[0]
                    if dcm_file_stem in img_datapath:
                        temp_dcm_file = os.path.join('/tmp',dcm_file_stem + '.dcm')
                        img = sitk.ReadImage(img_datapath)
                        writer = sitk.ImageFileWriter()
                        writer.SetFileName(temp_dcm_file)
                        writer.Execute(img) 
                        
                        tmp_dcm_image = dicom.dcmread(temp_dcm_file)
                        print("Setting file meta information...")
                        for item in dcm_image.dir():
                            if item not in no_include_tags:
                                tmp_dcm_image[item] = dcm_image[item]
                        print(f"Setting Series Instance UID {unique_series_uid}")
                        tmp_dcm_image.SeriesInstanceUID = unique_series_uid
                        tmp_dcm_image.CollimatorRightVerticalEdge = str(tmp_dcm_image.Columns + 1)
                        tmp_dcm_image.CollimatorLowerHorizontalEdge = str(tmp_dcm_image.Rows + 1)
                        
                        #dcm_file_stem = str(tmp_dcm_image.InstanceNumber) + '-' + unique_series_uid
                        print("Writing dicom file", dcm_file_stem+".dcm")
                        
                        tmp_dcm_image.save_as(os.path.join(output_dirpath,dcm_file_stem+".dcm"))
                        print("File saved.")    
        
             

    def show_man_page(self):
        """
        Print the app's man page.
        """
        print(Gstr_synopsis)
