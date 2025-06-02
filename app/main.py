from seedx import seedx_router
from fastapi import FastAPI
import uvicorn
from db.database import init_db


app = FastAPI(
    title="SeedX API",
    description="API for SeedX application",
    version="1.0.0",
)

@app.on_event("startup")
async def startup_event():
    await init_db()

app.include_router(seedx_router, prefix="/seedx", tags=["seedx"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 