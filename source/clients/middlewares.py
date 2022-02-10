async def get_json(data, handler) -> dict:
    response = await handler(data)
    return response.json()


async def get_text(data, handler) -> str:
    response = await handler(data)
    return response.text


async def get_content(data, handler) -> bytes:
    response = await handler(data)
    return response.content
