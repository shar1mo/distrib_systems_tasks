from fastapi import FastAPI

app = FastAPI()

@app.get("/items")
def get_items():
    return {"message": "Items service works"}