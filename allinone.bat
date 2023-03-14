@echo on
start cmd /k "cd/d .\venv\Scripts &&activate && cd/d ..\..\ &&py manage.py runserver 127.0.0.1:8000"