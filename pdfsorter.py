#!/usr/bin/env python
#
# Ryan Burns <rdburns@gmail.com>
#
# Scans PDF file text for keywords and moves file to appropriate directory.
# Takes text / dir names from an ini file
#

import ConfigParser
import glob
import string
import shutil
import re
import os
import sys

try:
    from PyPDF2 import PdfFileReader
except ImportError:
    print "Requires pyPDF library"
    print "http://pybrary.net/pyPdf/"
    sys.exit(1)
    
    
def pdf2text(filename):
    """Open PDF file and extract all text as a giant string for each page in a list.
    """
    pagetext = []
    pdf = PdfFileReader(file(filename, "rb"))
    numpages = pdf.getNumPages()
    for pn in range(numpages):
        pagetext.append(pdf.getPage(pn).extractText())
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
    config = ConfigParser.ConfigParser()
    config.read(filename)
    return config.items('Main')
     
def look_for_match(text,matchstr):
     """Looks for matchstr in text, returns True if found
     """
     if string.find(text,matchstr) != -1:
         return True
     else:
         return False
     
def move_file(dryrun,oldfile,newfilename,status=""):
     """Moves oldfile to newfilename
     """
     print "move_file()",oldfile,'->',newfilename,status
     if not dryrun:
         shutil.move(oldfile,os.path.expanduser(newfilename))
      
def get_date(text):
    """Returns year and month numeral from file contents
    This doesn't work very well, as all the files are different.
    """
    yearmatch = re.search("(20[0-9][0-9])",text)
    #Take first match we find
    if yearmatch:
        year = yearmatch.group(0)
    else:
        year = "YYYY"
    
    monthmatch = re.search('(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) [0-9]',text,re.I)
    if monthmatch:
        month = monthmatch.group(0)
    else:
        month = "MM"
    
    import pdb; pdb.set_trace()
    return year,month
     
     
if __name__ == "__main__":
    
    from optparse import OptionParser
    parser = OptionParser(usage="pdfmover mappings.cfg /somedir/*.pdf")
    parser.add_option("-d","--dryrun",action="store_true",default=False,
                      help="Will not move files if set.")
    (options,args) = parser.parse_args()
    
    #args[0] is config file, remaining args are files to move.
    
    mappings = read_ini_file(args[0])
    print mappings
    

    for filename in args[1:]:
        pagetext = pdf2text(filename) 
        if pagetext[0] == u'':
            #This PDF has no OCRed text in it.
            move_file(options.dryrun,filename,mappings[0][1]+'/',"No Text")
        else:
            
            #import pdb; pdb.set_trace()
            match_found = False
            for mapping in mappings:
                searchtext = '\n'.join(pagetext).lower()
                if look_for_match(searchtext,mapping[0]):
                    newfilename = mapping[1]+'/'+os.path.basename(mapping[1])+'_'+os.path.basename(filename)
                    move_file(options.dryrun,filename,newfilename)
                    match_found = True
                    break
            if not match_found:
                move_file(options.dryrun,filename,mappings[0][1]+'/',"No Match")
                    
            
            
      
