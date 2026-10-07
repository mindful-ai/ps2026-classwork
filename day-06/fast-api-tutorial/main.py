from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def hello():
    return {"message": "Hello everyone!!"}

@app.get('/world')
def hello2():
    return {"message": "Hello World!!"}