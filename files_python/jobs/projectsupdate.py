#!/usr/bin/python3

import argparse, datetime, json, os, platform, re, sys, time
from typing import Any, Callable, Dict, Optional, Union
from pprint import pprint

package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir = os.path.dirname(package_dir)
sys.path.insert(0, project_dir)
from files_python.classes import class_converttime, class_files, class_packages

docdirrelative = "myfolder/documentation"

def main():
    proj, docdirectory = parseArgs(sys.argv)
    parseProjects(proj)

def parseArgs(argv) -> tuple:
    parser = argparse.ArgumentParser()
    parser.add_argument('-pu', '--proj', dest='proj')
    parser.add_argument('-dd', '--docdirectory', dest='docdirectory')
    namespace = parser.parse_known_args(argv)[0]
    
    args = {k: v for k, v in vars(namespace).items() if v is not None}
    proj = json.loads(args.get('proj')) if isinstance(args.get('proj'), str) else None
    docdirectory = json.loads(args.get('docdirectory')) if isinstance(args.get('docdirectory'), str) else None
    return proj, docdirectory

# 1. parse list of projects and create directories and files
def parseProjects(proj):
    if isinstance(proj, dict):
        filepath = f"{project_dir}/{proj.get('filepath')}"
        linelist = class_files.Files({}).readJson(filepath) if os.path.exists(filepath) else None
        [(lambda x: createProject(proj, x))(x) for x in linelist] if isinstance(linelist, list) and len(linelist) > 0 else None

def createProject(proj:dict, item:dict) -> None:
    if isinstance(item.get('project'), str):
        print(f"\033[1;30;47mproject: {item.get('project')}\033[0m") if not re.search("^Windows", platform.platform()) else print(f"project: {item.get('project')}")
        directory = f"{os.path.dirname(project_dir)}/{item.get('project')}"
        functionlist = [projectDir, documentationDir, parsePackages, documentationUpdate]
        f = [f(proj, directory, item) for f in functionlist]

def projectDir(proj:dict, directory:str, item:dir) -> None:
    if isinstance(directory, str):
        filelist = [ \
            (f"{directory}/.gitignore", contentGitignore(directory)), \
            (f"{directory}/LICENCE.md", None), \
            (f"{directory}/README.md", None), \
        ]
        [(lambda x: class_packages.Packages({}).makeFiles(x))(x) for x in filelist]

def parsePackages(proj:dict, directory:str, item:dict) -> None:
    [(lambda x: createPackage(proj, directory, x))(x) for x in item.get('packagelist')] if isinstance(item.get('packagelist'), list) and len(item.get('packagelist')) > 0 else None
     
def createPackage(proj:dict, directory:str, packagename:str):
    """ use class to document package directory """
    l = packagename.split("_")
    
    obj = class_packages.Packages({"proj":proj, "projectdir":directory, "packagename":packagename, "docpath":f"{directory}/{docdirrelative}/custom/{packagename}"})
    if hasattr(obj, f"{l[-1]}Package"):
        print(f"\033[1;36;40mpackagename: {packagename}\033[0m") if not re.search("^Windows", platform.platform()) else print(f"packagename: {packagename}")
        getattr(obj,f"{l[-1]}Package")({})
    else:
        print(f"\033[1;31;40mpackagename: {packagename}, add {l[-1]}Package to class_packages.Packages\033[0m")  if not re.search("^Windows", platform.platform()) else print(f"packagename: {packagename}, add {l[-1]}Package to class_packages.Packages")

def documentationDir(proj:dict, directory:str, item:dict):
    from os.path import expanduser
    homedir = expanduser("~")

    pathlist = directory.split("/")
    runtext = []
    runtext.append(f"if [ ! -d \"{homedir}/Documents/textfiles/{pathlist[-1]}\" ]; then mkdir -p \"{homedir}/Documents/textfiles/{pathlist[-1]}\"; fi ")
    runtext.append(f"&& cp {directory}/{docdirrelative}/run/xxxx.txt {homedir}/Documents/textfiles/{pathlist[-1]}/xxxx.txt\n")
    runtext.append(f"xdg-open {homedir}/Documents/textfiles/{pathlist[-1]}/xxxx.txt")
    runtext.append("\n\n\n")
    rt = "".join(runtext)

    d = f"{directory}/{docdirrelative}"
    dirlist = [ \
        f"{d}/books", \
        f"{d}/classes", \
        f"{d}/custom", \
        f"{d}/custom/ebook", \
        f"{d}/jobs", \
        f"{d}/json", \
        f"{d}/links", \
        f"{d}/resources", \
        f"{d}/run", \
        f"{d}/screens", \
        f"{d}/tests", \
        f"{d}/themes"
    ]
    filelist = [ \
        (f"{d}/custom.adoc", contentCustom(directory)), \
        (f"{d}/index.adoc", contentIndex(directory)), \
        (f"{d}/links.adoc", contentLinks(directory)), \
        (f"{d}/run.adoc", contentRun(directory)), \
        (f"{d}/navigation.adoc", contentNavigation(directory)), \
        (f"{d}/variables.adoc", contentVariables(directory)), \
        (f"{d}/links/xxxx.adoc", None),
        (f"{d}/run/xxxx.txt", rt),
        (f"{d}/custom/ebook/index.adoc", None)
    ]

    [(lambda x: class_packages.Packages({}).makeDirectory(x))(x) for x in dirlist]
    [(lambda x: class_packages.Packages({}).makeFiles(x))(x) for x in filelist]

def contentGitignore(directory:str) -> None:
    s = []
    s.append(f"__pycache__\n")
    s.append(".gitignore*\n")
    s.append("*_01.*\n")
    s.append("*_02.*\n")
    s.append("*.crc\n")
    s.append("*.log\n")
    s.append("*.part\n")
    s.append("*.swp\n")
    s.append("DELETE/\n")
    s.append("myfolder/\n")
    return "".join(s)

def contentIndex(directory:str):
    def getTitle(directory:str) -> str:
        properties = class_files.Files({}).fileProperties(directory)
        return properties.get('name')

    title = getTitle(directory)
    s = []
    s.append(f"= {title}\n")
    s.append("include::variables.adoc[]\n\n")
    s.append("include::navigation.adoc[]\n\n")
    s.append("include::run.adoc[]\n\n")
    s.append("include::custom.adoc[]\n\n")
    s.append("include::links.adoc[]\n\n")
    return "".join(s)

def contentCustom(directory:str):
    return " "

def contentRun(directory:str):
    s = []
    s.append(f"== Run\n")
    s.append("[source%nowrap, bash]\n")
    s.append("----\n")
    s.append("\n")
    s.append("----\n")
    return "".join(s)

def contentLinks(directory:str):
    s = []
    s.append(f"== Links\n")
    s.append(".title description\n")
    s.append("* http...")
    return "".join(s)

def contentNavigation(directory:str):
    s = []
    s.append(f"== index\n")
    s.append("link:../[directory]\n")
    s.append(f"\n\n[source%nowrap, bash]\n----\nxdg-open {directory}/{docdirrelative}\n----\n")
    return "".join(s)
    
    return getContent()

def contentVariables(directory:str):
    s = []
    s.append(f":toc: left\n")
    s.append(":source-highlighter: rouge\n")
    s.append(":sectnums:\n")
    s.append(":front-cover-image: image:screens/ebook.png[]\n")
    return "".join(s)


# 2. update documentation for run, links, custom
def documentationUpdate(proj:dict, directory:str, item:dict) -> list:
    d = f"{directory}/{docdirrelative}"
    createCustomIndex(f"{d}/custom")
    createLinkIndex(f"{d}/links")
    createRunIndex(f"{d}/run")

def createCustomIndex(directory:str) -> None:
    def write(directory, x):
        c = f"link:custom/{x}[{x}, window=_blank]\n" if re.search(".pdf$", x) else f"link:custom/{x}/index.adoc[{x}, window=_blank]\n"
        class_files.Files({}).writeFile({"file":f"{directory}.adoc", "content":c})

    if isinstance(directory, str):
        os.remove(f"{directory}.adoc") if os.path.exists(f"{directory}.adoc") else None
        y = os.listdir(directory) if os.path.exists(directory) else None
        l = [x for x in y if not re.search("DELETE|ignore", x)]
        if len(l) > 0:
            l.sort()
            os.remove(f"{directory}.adoc") if os.path.exists(f"{directory}.adoc") else None
            class_files.Files({}).writeFile({"file":f"{directory}.adoc", "content":f"== Custom\n\n"})
            #[(lambda x: class_files.Files({}).writeFile({"file":f"{directory}.adoc", "content":f"link:custom/{x}/index.adoc[{x}, window=_blank]\n"}))(x) for x in l]
            [(lambda x: write(directory, x))(x) for x in l]
        else:
            class_files.Files({}).writeFile({"file":f"{directory}.adoc", "content":None})
        
def createLinkIndex(directory:str) -> None:
    if isinstance(directory, str):
        os.remove(f"{directory}.adoc") if os.path.exists(f"{directory}.adoc") else None
        y = os.listdir(directory) if os.path.exists(directory) else None
        l = [x for x in y if not re.search("DELETE|ignore|xxxx.adoc", x)]
        if len(l) > 0:
            l.sort()
            class_files.Files({}).writeFile({"file":f"{directory}.adoc", "content":f"== Links\n\n"})
            [(lambda x: class_files.Files({}).writeFile({"file":f"{directory}.adoc", "content":f"include::links/{x}[]\n"}))(x) for x in l]
        else:
            class_files.Files({}).writeFile({"file":f"{directory}.adoc", "content":None})

def createRunIndex(directory:str) -> None:
    if isinstance(directory, str):
        os.remove(f"{directory}.adoc") if os.path.exists(f"{directory}.adoc") else None
        y = os.listdir(directory) if os.path.exists(directory) else None
        l = [x for x in y if not re.search("DELETE|ignore|xxxx.txt", x)]
        if len(l) > 0:
            l.sort()
            os.remove(f"{directory}.adoc") if os.path.exists(f"{directory}.adoc") else None
            properties = class_files.Files({}).fileProperties(directory)
            class_files.Files({}).writeFile({"file":f"{directory}.adoc", "content":f"== Run\n\n"})
            [(lambda x: class_files.Files({}).writeFile({"file":f"{directory}.adoc", "content":f"=== {x}\n[source%nowrap, bash]\n----\ninclude::run/{x}[]\n----\n"}))(x) for x in l]
        else:
            class_files.Files({}).writeFile({"file":f"{directory}.adoc", "content":None})

if __name__ == '__main__':
    time_start = time.time()
    main()
    if not re.search("^Windows", platform.platform()):
        time_finish = time.time()
        start_time = datetime.datetime.fromtimestamp(int(time_start)).strftime('%Y-%m-%d %H:%M:%S')
        finish_time = datetime.datetime.fromtimestamp(int(time_finish)).strftime('%Y-%m-%d %H:%M:%S')
        finish_seconds = round(time_finish - time_start,3)
        t = class_converttime.Converttime(config={}).convert_time({"timestring":finish_seconds}) 
        print(f"Time start: {start_time}")
        print(f"Time finish: {finish_time} | Total time: {t.get('ts')}")


