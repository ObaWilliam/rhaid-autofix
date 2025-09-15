@echo off
REM Force tests to import local src and run pytest for markdown tests
set PYTHONPATH=src
REM Print which module file is imported
.%\venv\Scripts\python.exe -c "import sys,importlib; sys.path.insert(0,'src'); m=importlib.import_module('rhaid'); print('imported:', m.__file__)"
REM Run pytest for markdown tests
.%\venv\Scripts\python.exe -m pytest tests/test_markdown.py -q -r a
pause
