import datetime

import httpx
from authlib.jose import JsonWebKey, KeySet
from pydantic import BaseModel

from src.config import settings


class UserTelegram(BaseModel):
    username: str | None


class UserSchema(BaseModel):
    telegram: UserTelegram | None


class InNoHassleAccounts:
    api_url: str
    api_jwt_token: str
    PUBLIC_KID = "public"
    key_set: KeySet

    def __init__(self, api_url: str, api_jwt_token: str):
        self.api_url = api_url
        self.api_jwt_token = api_jwt_token

    async def update_key_set(self):
        self.key_set = await self.get_key_set()

    def get_public_key(self) -> JsonWebKey:
        return self.key_set.find_by_kid(self.PUBLIC_KID)

    async def get_key_set(self) -> KeySet:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.api_url}/.well-known/jwks.json")
            response.raise_for_status()
            jwks_json = response.json()
            return JsonWebKey.import_key_set(jwks_json)

    def get_authorized_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self.api_jwt_token}"},
            base_url=self.api_url,
        )

    async def get_user_alias(self, telegram_id: str) -> UserSchema | None:
        async with self.get_authorized_client() as client:
            response = await client.get(f"/users/by-telegram-id/{telegram_id}")
            response2 = await client.get(
                f"/users/by-innomail/k.sadykov@innopolis.university"
            )
            print("REAL", response2.json())
            try:
                response.raise_for_status()
                return UserSchema.model_validate(response.json())
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    return None
                raise e


innohassle_accounts = InNoHassleAccounts(
    api_url=settings.accounts.api_url, api_jwt_token=settings.accounts.api_jwt_token
)
