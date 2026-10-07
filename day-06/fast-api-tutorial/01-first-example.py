# main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}


@app.get("/hello/{name}")
def say_hello(name: str):
    return {"message": f"Hello {name}, welcome to FastAPI!"}


'''
COMMANDS:
>uvicorn 01-first-example:app --reload

http://127.0.0.1:8000
http://127.0.0.1:8000/hello/purushotham

'''