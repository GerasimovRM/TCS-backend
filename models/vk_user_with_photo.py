from pydantic import BaseModel


class VkUserWithPhoto(BaseModel):
    first_name: str
    last_name: str
    vk_id: str
    avatar_url: str
