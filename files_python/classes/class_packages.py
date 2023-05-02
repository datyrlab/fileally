#!/usr/bin/python3

import argparse, datetime, json, os, platform, random, re, shutil, subprocess, sys, time
from typing import Any, Callable, Dict, Optional, Union 

package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir = os.path.dirname(package_dir)
sys.path.insert(0, project_dir)
from files_python.classes import class_converttime, class_files 
from files_python.jobs import docdirectory

class Packages:      

    def __init__(self, config:dict):
        self.config = config
        self.proj = config.get('proj')
        self.projectdir = config.get('projectdir')
        self.packagedir = f"{config.get('projectdir')}/{config.get('packagename')}"
        self.packagename = config.get('packagename')
        self.docpath = self.config.get('docpath')
    
    def documentPackage(self, packagedir:str) -> None:
        def createPdf(projectdir:str, pdflist:list):
            p = projectdir.split("/")
            name = p[-1]
            if isinstance(pdflist, list):
                if len(pdflist) == 0:
                    return None
                n = list(filter(None, [x for x in pdflist if x == name]))
                return n[0] if len(n) > 0 else None
            return name 

        directories = {"pathlist":[packagedir]}
        scrape = {"include":".cpp$|.js$|.json$|.py$|.sh$|.sql$|.txt$", "exclude":"__init__.py$|.fspy$|.npy$|.swp$|__pycache__|/resources|/DELETE|ignore", "docpath":self.docpath} 
        pdf = {"make":True}
        dirlist = docdirectory.parseDirectories(directories)
        listoflists = docdirectory.parseDirlist(directories, scrape, dirlist)
        indexlistoflists = docdirectory.parseListofLists(listoflists, scrape)
        docdirectory.parseIndex(indexlistoflists)
        name = createPdf(self.projectdir, self.proj.get('pdflist'))
        docdirectory.parsePdf(pdf, directories, {"docpath":os.path.dirname(self.docpath)}) if name else None
        
    def makeDirectory(self, directory:str) -> None:
        if isinstance(directory, str) and not os.path.exists(directory):
            os.makedirs(directory)
    
    def makeFiles(self, files:tuple) -> None:
        directory = os.path.dirname(files[0]) # make directory if not exist
        filepath = files[0]
        content = files[1]
        class_files.Files(config={}).createFile(filepath, content, directory) if not os.path.exists(filepath) else None

    def pythonPackage(self, custom:dict) -> None:
        dirlist = [ \
            self.packagedir, \
            f"{self.packagedir}/classes", \
            f"{self.packagedir}/jobs", \
            f"{self.packagedir}/json", \
            f"{self.packagedir}/resources", \
            f"{self.packagedir}/tests" \
        ]
        filelist = [ \
            (f"{os.path.dirname(self.packagedir)}/requirements.txt", None), \
            (f"{os.path.dirname(self.packagedir)}/setup.py", None), \
            (f"{self.packagedir}/__init__.py", None), \
            (f"{self.packagedir}/classes/__init__.py", None), \
            (f"{self.packagedir}/jobs/__init__.py", None), \
            (f"{self.packagedir}/tests/__init__.py", None)
        ]
        [(lambda x: Packages(self.config).makeDirectory(x))(x) for x in dirlist]
        [(lambda x: Packages(self.config).makeFiles(x))(x) for x in filelist]
        Packages(self.config).documentPackage(self.packagedir)



