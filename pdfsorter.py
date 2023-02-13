#!/usr/bin/env python
#
# Ryan Burns <rdburns@gmail.com>
#
# Scans PDF file text for keywords and moves file to appropriate directory.
# Takes text / dir names from an ini file
#

import configparser
import glob
import string
import shutil
import re
import os
import sys
import logging
from pprint import pprint, pformat
from argparse import ArgumentParser

try:
    from yaml import load, Loader
except ImportError:
    print("PyYAML required to use this script.")
    print("https://pypi.org/project/PyYAML/")
    print("Try pip install PyYAML")
    sys.exit(1)

try:
    from pypdf import PdfReader
except ImportError:
    print("pydf required to use this script.")
    print("https://pypi.org/project/pypdf/")
    print("Try pip install pypdf")
    sys.exit(1)
    
    
def pdf2text(filename):
    """Open PDF file and extract all text as a giant string for each page in a list.
    """
    pagetext = []
    pdf = PdfReader(filename)
    numpages = len(pdf.pages)
    for pn in range(numpages):
        pagetext.append(pdf.pages[pn].extract_text())
    return pagetext


def read_ini_file(filename):
    """Reads INI file to get match/dest pairs
    The file format expected is one [Main] section followed by a series of 
    value assignments which map keywords to directories:
    John Doe = ./john_doe_dir
    
    one special entry is used:
    nomatch = ~/MyDocuments/test_nomatch
    It must be the first item in the file.
    
    This is used to move files which don't match anything or have no text.
    It is assumed "nomatch" won't occur in any target file.
    
    """
    config = configparser.ConfigParser()
    config.read(filename)
    return config.items('Main')


def look_for_match(text, matchstr):
     """Looks for matchstr in text, returns True if found
     """
     if text.find(matchstr.lower()) != -1:
         return True
     else:
         return False

     
def move_file(dryrun, oldfile, newfilename, status=""):
     """Moves oldfile to newfilename
     """
     logging.info("move_file() " + oldfile + ' -> ' + \
                  str(newfilename) + ' ' +  str(status))
     logging.info("Dry_run: " + str(dryrun))
     if not dryrun:
         shutil.move(oldfile, os.path.expanduser(newfilename))

         
def get_date(text):
    """Returns year and month numeral from file contents
    This doesn't work very well, as all the files are different.
    """
    yearmatch = re.search("(20[0-9][0-9])", text)
    #Take first match we find
    if yearmatch:
        year = yearmatch.group(0)
    else:
        year = "YYYY"
    
    monthmatch = re.search('(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) [0-9]', text, re.I)
    if monthmatch:
        month = monthmatch.group(0)
    else:
        month = "MM"
    
    import pdb; pdb.set_trace()
    return year, month


def main(args):

    with open(args.yaml_fn, 'r') as f:
        conf = load(f, Loader=Loader)
    logging.debug(pformat(conf))

    defaultdir = conf['default_folder'] + '/'
    if not os.path.exists(defaultdir):
        logging.debug('Making directory ' + defaultdir)
        os.makedirs(defaultdir)  

    logging.info("Looking for PDFs in " + conf['watch_folder'])
    pdf_fns = glob.glob(conf['watch_folder'] + '/*.pdf')

    logging.info("Processing files: " + str(pdf_fns))
    
    for filename in pdf_fns:
        pagetext = pdf2text(filename)
        searchtext = '\n'.join(pagetext).lower()
        if pagetext[0] == '':
            logging.info(filename + " has no OCRed text in it.")
            move_file(args.dryrun, filename, conf['default_folder'], "No Text")
        else:
            match_found = False
            for vector in conf['folders']:
                for matchstr in conf['folders'][vector]:
                    if look_for_match(searchtext, str(matchstr)):
                        # Prepend the vector name onto the filename and put it in the vector folder.
                        newdir = conf['target_folder'] + '/' + \
                          vector + '/'
                        newfilename = newdir + vector + '_' + \
                          os.path.basename(filename)
                        if not os.path.exists(newdir):
                            logging.debug('Making directory ' + newdir)
                            os.makedirs(newdir)  
                        move_file(args.dryrun, filename, newfilename)
                        match_found = True
                        break
                if match_found: break
            if not match_found:
                move_file(args.dryrun, filename, conf['default_folder']+'/', "No Match")
                    
    
     
if __name__ == "__main__":
    
    parser = ArgumentParser(description="Sorts PDF files to several directories by searching the text in them for keywords.")
    parser.add_argument("yaml_fn", help="YAML file containing configuration.")
    parser.add_argument("-d","--dryrun",action="store_true",default=False,
                      help="Will not move files if set.")
    args = parser.parse_args()
    
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    fh = logging.FileHandler('pdfsorter.log')
    fh.setLevel(logging.DEBUG)
    root.addHandler(fh)

    main(args)
            
            
      
