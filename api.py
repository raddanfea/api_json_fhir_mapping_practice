from uvicorn import run
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException

from ge_interview.model import InputModel

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)


@app.post("/convert")
async def map_json(input_data: InputModel):
    return bool(input_data)


if __name__ == "__main__":
    run("api:app", host="0.0.0.0", port=3000, reload=True)
