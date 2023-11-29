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
    cookie_secret: str | None = None


class ActivityModel(BaseModel):
    user_id: int
    title: str
    description: str | None = None
    activity_type: str
    laps: float | None = None
    distance: float | None = None
    date: float
    time_start: float
    time_end: float
    published: bool = True
    visibility: int

