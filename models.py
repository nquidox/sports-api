from pydantic import BaseModel


class UserModel(BaseModel):
    username: str
    first_name: str | None = None
    last_name: str | None = None
    birthday: float | None = None
    gender: str | None = None
    disabled: bool = False
    hashed_password: str
    is_superuser: bool = False


# TODO: move sessions to separate table
# class UserSessions(BaseModel):
#     hashed_password: str

