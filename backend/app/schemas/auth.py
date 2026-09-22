from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Register(Input):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(pattern=r"^\+?[0-9]{10,15}$")
    password: str = Field(min_length=12, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value):
        return value.lower()


class Login(Input):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class ProfileUpdate(Input):
    name: str = Field(min_length=2, max_length=100)
    phone: str = Field(pattern=r"^\+?[0-9]{10,15}$")


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str
    phone: str
    role: str
    is_active: bool


class LoginOut(BaseModel):
    user: UserOut
    csrf_token: str
