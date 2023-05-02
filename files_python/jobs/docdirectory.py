#!/usr/bin/python3

import argparse, datetime, json, os, platform, re, sys, time
from typing import Any, Callable, Dict, Optional, Union
from pprint import pprint

package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir = os.path.dirname(package_dir)
sys.path.insert(0, project_dir)
from files_python.classes import class_converttime, class_files, class_subprocess

#timestamp_numeric = int(time.time() * 1000.0)

def main():
    directories, scrape, pdf = parseArgs(sys.argv)
    dirlist = parseDirectories(directories)
    listoflists = parseDirlist(directories, scrape, dirlist)
    indexlistoflists = parseListofLists(listoflists, scrape)
    parseIndex(indexlistoflists)
    parsePdf(pdf, directories, scrape)

def parseArgs(argv) -> tuple:
    parser = argparse.ArgumentParser()
    parser.add_argument('-di', '--directories', dest='directories')
    parser.add_argument('-pd', '--pdf', dest='pdf')
    parser.add_argument('-sc', '--scrape', dest='scrape')
    namespace = parser.parse_known_args(argv)[0]
    
    args = {k: v for k, v in vars(namespace).items() if v is not None}
    directories = json.loads(args.get('directories')) if isinstance(args.get('directories'), str) else None
    pdf = json.loads(args.get('pdf')) if isinstance(args.get('pdf'), str) else None
    scrape = json.loads(args.get('scrape')) if isinstance(args.get('scrape'), str) else None
    return directories, scrape, pdf

# 4. make PDF
def parsePdf(pdf, directories:dict, scrape:dict) -> list:
    if isinstance(pdf, dict) and pdf.get('make') == True and isinstance(directories.get('pathlist'), list):
        [(lambda x: makePdf(scrape, x))(x) for x in directories.get('pathlist')] if len(directories.get('pathlist')) > 0 else None
            
def makePdf(scrape:dict, directory) -> None:
    def create(d:tuple) -> None:
        print(f"\033[1;33m{d[1]}\033[0m")
        makeDirectory(os.path.dirname(d[1]))
        s = []
        s.append("asciidoctor-pdf ")
        s.append("-a scripts=cjk ")
        s.append("-a pdf-fontsdir=GEM_FONTS_DIR,`ruby ")
        s.append("-r asciidoctor-pdf-cjk-kai_gen_gothic ")
        s.append("-e \"print File.expand_path '../fonts', (Gem.datadir 'asciidoctor-pdf-cjk-kai_gen_gothic')\"` ")
        s.append(f"{d[1]} ")
        s.append(f"--out-file {d[2]} ")
        command = " ".join(s)
        class_subprocess.Subprocess({}).run(command)
    
    timestamp_numeric = int(time.time() * 1000.0)
    properties = class_files.Files({}).fileProperties(directory)
    dir_document = scrape.get('docpath') if isinstance(scrape.get('docpath'), str) else f"{project_dir}/myfolder/docadoc"
    dir_output = scrape.get('docpath') if isinstance(scrape.get('docpath'), str) else f"{project_dir}/myfolder/pdf"
    pdflist = [
        (dir_document, f"{dir_document}/{properties.get('name')}/index.adoc", f"{dir_output}/{properties.get('name')}-{timestamp_numeric}.pdf"),
        (dir_document, f"{dir_document}/{properties.get('name')}/index.adoc", f"{dir_output}/{properties.get('name')}.pdf")
    ]
    [(lambda x: create(x))(x) for x in pdflist]

# 3. create index
def parseIndex(listoflists:list) -> list:
    if isinstance(listoflists, list):
        [(lambda x: createIndex(x))(x) for x in listoflists]

def createIndex(filelist:list) -> list:
    if isinstance(filelist, list) and len(filelist) > 0:
        indexfile = list(set([x[0] for x in filelist]))[0]
        indexfilelist = [x[1] for x in filelist]
        os.remove(indexfile) if os.path.exists(indexfile) else None
        header = ":toc: left\n:source-highlighter: rouge\n:sectnums:\n\n"
        class_files.Files({}).writeFile({"file":indexfile, "content":header})
        [(lambda x: class_files.Files({}).writeFile({"file":indexfile, "content":f"include::{x}[]\n"}))(x) for x in indexfilelist]


# 1. get files
def parseDirectories(d:dict):
    return d.get('pathlist') if isinstance(d, dict) and isinstance(d.get('pathlist'), list) else None

def parseDirlist(directories:dict, scrape:dict, dirlist:list):
    if isinstance(dirlist, list) and len(dirlist) > 0:
        return list(filter(None, [(lambda x: getListOfFiles(scrape, x))(x) for x in dirlist])) 

def getListOfFiles(scrape:dict, directory:list) -> list:
    if os.path.exists(directory):
        include = scrape.get('include') if isinstance(scrape.get('include'), str) else ".cpp$|.js$|.json$|.py$|.rs$|.sh$|.sql$|.txt$"
        exclude = scrape.get('exclude') if isinstance(scrape.get('exclude'), str) else "__init__.py$|_01.py$|_02.py$|.swp$|__pycache__|DELETE|ignore|tests/|test_"
        result = class_files.Files({}).listDirectory(directory)    
        a = [x for x in result if re.search(include, x)]
        return [(directory, x) for x in a if not re.search(exclude, x)] if len(a) > 0 else None


# 2. scrape pages
def parseListofLists(listoflists:list, scrape:dict) -> list:
    if isinstance(listoflists, list) and len(listoflists) > 0:
        return [(lambda x: parseFiles(x, scrape))(x) for x in listoflists]
    
def parseFiles(filelist:list, scrape:dict) -> list:
    def sortList(filelist):
        #filelist.sort()
        #sorted(set(filelist), key=filelist.index)
        return filelist
    
    directory = list(set([x[0] for x in filelist]))[0]
    sortedlist = sortList([x[1] for x in filelist])
    return list(filter(None, [(lambda x: openPage(directory, x, scrape))(x) for x in sortedlist]))

def openPage(directory:str, filepath:str, scrape:dict) -> tuple:
    properties_dir = class_files.Files({}).fileProperties(directory) 
    properties = class_files.Files({}).fileProperties(filepath)
    d = {}
    d["title"] = properties.get('name') 
    d["directory"] = directory
    d["properties"] = class_files.Files({}).fileProperties(filepath)
    d["dir_documentation"] = scrape.get('docpath') if isinstance(scrape.get('docpath'), str) else f"{project_dir}/myfolder/docadoc/{properties_dir.get('name')}"
    d["dir_relative"]  = re.sub('^/', '', re.sub(directory, '', properties.get('path')) )
    d["dir_sub"] = d.get('dir_relative').split("/")[0] # api
    d["lang"] = properties.get('file_extension').replace('.', '') # py
    d["includepath"] =  filepath
    d["page_adoc"] =  f"{d.get('dir_documentation')}/{d.get('dir_relative')}/{properties.get('name')}.adoc"
    d["page_adoc_relative"] = re.sub('^/', '', f"{d.get('dir_relative')}/{properties.get('name')}.adoc") 
    d["page_index_list"] = f"{scrape.get('docpath')}/index.adoc" if isinstance(scrape.get('docpath'), str) else f"{d.get('dir_documentation')}/index.adoc" 

    try:
        contentlist = class_files.Files({}).readFile(filepath)
        contentstr = " ".join(contentlist)
        images = scrapeImage([], d, contentstr)
        taglist = list(filter(None, [(lambda x: scrapeTags(x, d, contentstr, scrape))(x) for x in contentlist ])) if len(contentlist) > 0 else None
        tags = "".join(taglist) if isinstance(taglist, list) and len(taglist) > 0 else None
        createFile(tags, d) if tags else createFile(entirePage(d, images), d) 
        return (d.get("page_index_list"), d.get("page_adoc_relative"))
    
    except Exception as e:
        print(f"\033[1;31m{filepath}\033[0m") 
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        

def entirePage(d:dict, images:list):
    s = []
    s.append(f"[source%nowrap, {d.get('lang')}]\n")
    s.append("----\n")
    s.append(f"include::{d.get('includepath')}[]\n\n") if not d.get('lang') == "json" else s.append(f"include::{d.get('properties',{}).get('fullpath')}[]\n\n")
    s.append("----\n\n")
    s.append("/n".join(images)) if isinstance(images, list) else None
    return "".join(s)

def scrapeTags(line:str, d:dict, contentstr:str, scrape:dict):
    match = re.search(r"tag\:\:(.*?)\[\]", line, re.I)
    if match:
        s = []
        s.append(f"=== {match[1]}\n")
        s.append(f"[source%nowrap, {d.get('lang')}]\n")
        s.append("----\n")
        s.append(f"include::{d.get('includepath')}[tag={match[1]}]\n\n")
        s.append("----\n\n")
        
        # cpp, create command to compile and run
        if re.search('test_(.*?).cpp', d.get('properties').get('filename')): 
            s.append(f"==== compile\n")
            s.append(f"[source%nowrap, bash]\n")
            s.append("----\n")
            s.append(f"cd {properties.get('path')}\n")
            s.append(f"g++ -o {d.get('properties').get('name')} {d.get('properties').get('filename')}\n")
            s.append(f"./{d.get('properties').get('name')}\n")
            s.append("----\n\n")
        
        # get codeblock for each tag to scrape additional elements
        codeblock = getCodeblock(match[1], d, contentstr)
        image = scrapeImage(s, d, codeblock)
        return "".join(s)

def getCodeblock(tag:str, d:str, content) -> tuple:
    match = re.findall(fr"tag\:\:{tag}\[\](.*?)end\:\:{tag}\[\]", content, re.I)
    return match[0] if match else None

def scrapeImage(s:list, d:dict, codeblock:str) -> str:
    if isinstance(codeblock, str):
        match = re.findall(fr"screens\/(.*?)\[\]", codeblock, re.I)
        if match:
            c = list(filter(None, [(lambda x: addImage(d, x))(x) for x in match] ))
            if len(c) > 0:
                s.append("".join(c) + "\n")
    return s 

def addImage(d:dict, image) -> str:
    fullpath = f"{d.get('directory')}/screens/{image}"
    adocpath = f"image::{fullpath}[]\n"
    return adocpath if os.path.exists(fullpath) else f"[red yellow-background]#{fullpath}#\n"

def createFile(tags:str, d:dict) -> None:
    if isinstance(tags, str):
        title = re.sub('^/', '', f"{d.get('title')}.{d.get('lang')}")
        filepath = re.sub('^/', '', f"{d.get('dir_relative')}/{d.get('properties').get('filename')}")
        s = []
        s.append(f"== {title}\n:title-page:\n\n")
        s.append(f"{filepath}\n\n")
        header = "".join(s)
        page_content = header + tags
        os.remove(d.get('page_adoc')) if os.path.exists(d.get('page_adoc')) else None
        makeDirectory(os.path.dirname(d.get('page_adoc')))
        class_files.Files({}).writeFile({"file":d.get('page_adoc'), "content":page_content})
        return (d.get('page_index_list'), d.get('page_adoc'), d.get('page_adoc_relative'))

def makeDirectory(directory:str) -> None:
    if isinstance(directory, str) and not os.path.exists(directory):
        os.makedirs(directory)


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


