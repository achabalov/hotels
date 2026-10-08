from redis.asyncio import Redis


class RedisManager:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        # db: int = 0,
    ):
        self.host = host
        self.port = port
        # self.db = db
        self.redis: Redis | None = None

    async def connect(self):
        self.redis = Redis(
            host=self.host,
            port=self.port,
            # db=self.db,
            decode_responses=True,
        )

        await self.redis.ping()

    async def set(
        self,
        key: str,
        value: str,
        expire: int | None = None,
    ):
        if self.redis is None:
            raise RuntimeError("Redis is not connected")

        await self.redis.set(
            name=key,
            value=value,
            ex=expire,
        )

    async def get(self, key: str) -> str | None:
        if self.redis is None:
            raise RuntimeError("Redis is not connected")

        return await self.redis.get(key)

    async def delete(self, key: str):
        if self.redis is None:
            raise RuntimeError("Redis is not connected")

        await self.redis.delete(key)

    async def close(self):
        if self.redis is not None:
            await self.redis.aclose()