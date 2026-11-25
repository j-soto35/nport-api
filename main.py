from fastapi import FastAPI
from controllers.nport_controller import router as nport_router

app = FastAPI(title="SEC N-PORT API")

app.include_router(nport_router, prefix="/nport", tags=["N-PORT"])