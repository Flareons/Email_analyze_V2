from fastapi import APIRouter, Request, HTTPException

router = APIRouter(
    prefix="/report",
    tags=["Report Data Analysis"],
)

