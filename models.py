from pydantic import BaseModel


class UserModel(BaseModel):
    username: str
    first_name: str | None = None
    last_name: str | None = None
    birthday: float | None = None
    gender: str | None = None
