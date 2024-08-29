from fastapi import APIRouter, Depends
from starlette import status

router = APIRouter()


@router.get(
    "",
    name="ping",
    status_code=status.HTTP_200_OK,
)
def ping():
    return("pong")