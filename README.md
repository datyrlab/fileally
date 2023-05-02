# files-python

A cross platform toolkit for handling files


## Asciidoc the contents of a directory

### Linux
```
python3 fileally/files_python/jobs/docdirectory.py \
--directories '{"pathlist":["/path/to/directory"}' \
--scrape '{"include":".cpp$|.js$|.json$|.html$|.md$|.py$|.sh$|.sql$|.txt$", "exclude":"__init__.py$|.github|gitignore|.lock$|.npy$|__pycache__"}' \
--pdf '{"make":true}'

```

### Windows
```
python fileally/files_python/jobs/docdirectory.py `
--directories '{\"pathlist\":[\"/path/to/directory\"]}' `
--scrape '{\"include\":\".cpp$|.js$|.json$|.html$|.md$|.py$|.sh$|.sql$|.txt$\", \"exclude\":\"__init__.py$|.github|gitignore|.lock$|.npy$|__pycache__\"}' `
--pdf '{\"make\":true}'

```

## Create/update a project directory

### Linux
```
python3 fileally/files_python/jobs/projectsupdate.py \
--proj '{"filepath":"files_python/json/projects/projectlisttest.json", "pdflist":[]}'
```

### Windows
```
python fileally/files_python/jobs/projectsupdate.py `
--proj '{\"filepath\":\"files_python/json/projects/projectlisttest.json\", \"pdflist\":[]}'
```
