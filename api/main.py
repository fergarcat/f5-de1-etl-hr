## main.py
import os
from fastapi import FastAPI
import uvicorn
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API up and running"}

if __name__ == "__main__":
    uvicorn.run("main:app", host=os.getenv("API_HOST", "0.0.0.0"), port=int(os.getenv("API_PORT", 8000)))
