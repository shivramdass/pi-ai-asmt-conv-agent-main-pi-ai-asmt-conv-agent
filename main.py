import uvicorn
from fastapi import FastAPI
from src.routers import IntentResponseRouter
from src.routers import SpeechProcessingRouters

app = FastAPI()

app.include_router(IntentResponseRouter.router)
app.include_router(SpeechProcessingRouters.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)