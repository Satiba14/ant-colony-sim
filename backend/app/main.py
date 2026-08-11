from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.websocket import router as websocket_router

app = FastAPI(title="Ant Colony Simulation API")

# Allowing all origins for local dev simplicity. Tighten this to your actual
# frontend URL before deploying anywhere public (same pattern you used for
# WorkPulse's CORS setup).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(websocket_router)


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Ant colony simulation backend is running"}
