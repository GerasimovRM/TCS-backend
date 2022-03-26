import aiohttp

from models.vk_user_with_photo import VkUserWithPhoto


async def get_vk_user_with_photo(access_token: str) -> VkUserWithPhoto:
    async with aiohttp.ClientSession() as session:
        data = {
            "access_token": access_token,
            "fields": "photo_400",
            "v": "5.130"
        }
        async with session.get("https://api.vk.com/method/users.get", params=data) as response:
            response_data = await response.json()
            response_data = response_data["response"][0]
            vk_user = VkUserWithPhoto(first_name=response_data["first_name"],
                                      last_name=response_data["last_name"],
                                      avatar_url=response_data["photo_400"],
                                      vk_id=response_data["id"])
            return vk_user
