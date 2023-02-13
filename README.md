# pdfsorter
Sorts PDF files to several directories by searching the text in them for keywords.

Used similar YAML file format to PyPDFOCR, but only doing my own file sorting, 
since some scanners come with OCR software that is superior to tesseract.

# Dependencies
* PyYAML
* pypdf

# Usage

    usage: pdfsorter.py [-h] [-d] yaml_fn
    
    Sorts PDF files to several directories by searching the text in them for keywords.
    
    positional arguments:
      yaml_fn       YAML file containing configuration.
    
    optional arguments:
      -h, --help    show this help message and exit
      -d, --dryrun  Will not move files if set.

# YAML File Format:

    watch_folder: "/Users/bubblegum/scaninbox"
    target_folder: "/Users/bubblegum/scans"
    default_folder: "/Users/bubblegum/scans/unfiled"
    
    folders:
        water:
            - city of gotham water utilities
            - water utilities
        gas:
            - Monthly Energy Usage
            - save energy
            - gas leak
        cable:
            - cable
            - internet
