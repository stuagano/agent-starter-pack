from fastapi import FastAPI
from .routes_pdf import router as pdf_router
from .routes_lists import router as lists_router
from .routes_calendar import router as calendar_router

app = FastAPI()

app.include_router(pdf_router)
app.include_router(lists_router)
app.include_router(calendar_router)

@app.get("/healthz")
def health_check():
    return {"status": "ok"} 