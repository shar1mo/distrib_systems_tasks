from fastapi import FastAPI

app = FastAPI()

@app.get("/other")
def get_other():
    return {"message": "Other service works"}