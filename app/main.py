from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

import os

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.faculty import router as faculty_routes
from app.api.v1.routes.cafedra import router as cafedra_routes
from app.api.v1.routes.specialty import router as specialty_routes
from app.api.v1.routes.university import router as university_routes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=['Auth'])
app.include_router(faculty_routes, prefix="/api", tags=['Faculty'])
app.include_router(cafedra_routes, prefix="/api", tags=['Cafedra'])
app.include_router(university_routes, prefix="/api", tags=['University'])
app.include_router(specialty_routes, prefix="/api", tags=['Specialty'])

@app.get("/")
def read_root():
    return {"message": "API Running"}

# from fastapi import FastAPI, Depends, HTTPException, status
# from fastapi.security import HTTPBasic, HTTPBasicCredentials
# from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html

# app = FastAPI(docs_url=None, redoc_url=None)  # Disable default docs

# security = HTTPBasic()

# USERNAME = os.getenv("SWAGGER_USERNAME")
# PASSWORD = os.getenv("SWAGGER_PASSWORD")

# def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
#     correct_username = credentials.username == USERNAME
#     correct_password = credentials.password == PASSWORD
#     if not (correct_username and correct_password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid credentials",
#             headers={"WWW-Authenticate": "Basic"},
#         )

# @app.get("/docs", include_in_schema=False)
# def get_swagger_documentation(credentials: HTTPBasicCredentials = Depends(verify_credentials)):
#     return get_swagger_ui_html(openapi_url="/openapi.json", title="Secure API Docs")

# @app.get("/redoc", include_in_schema=False)
# def get_redoc_documentation(credentials: HTTPBasicCredentials = Depends(verify_credentials)):
#     return get_redoc_html(openapi_url="/openapi.json", title="Secure API Docs")