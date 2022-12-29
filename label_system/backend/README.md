# messageWOZ Backend
## Build enviroment
```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```
## Execute
```
$ uvicorn --host 127.0.0.1 --reload main:app
```
or
```
$ python3 main.py
```