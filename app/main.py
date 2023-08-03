from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings
from app.utils.logger import logzz
from app import schemas


app = FastAPI(
    title=settings.PROJECT_NAME, 
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)


# Set all CORS enabled origins
'''
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
'''
@app.get("/", tags=['home'], response_model=schemas.Msg)
def root():
    return JSONResponse({"home": "Waiting for frontend..."})
    

app.include_router(
    api_router, 
    prefix=settings.API_V1_STR
)

logzz.info("Application Started.", timestamp=1)