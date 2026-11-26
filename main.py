from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from controllers.nport_controller import router as nport_router

app = FastAPI(title="SEC N-PORT API")

# CORS configuration
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://nport-ui.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(nport_router, prefix="/nport", tags=["N-PORT"])