import httpx

async def proxy_request(url:str, method:str, data=None, params=None):
    
    async with httpx.AsyncClient() as client:
        if method == "GET":
            response = await client.get(url, params=params)
        elif method == "POST":
            response = await client.post(url, data=data)
        elif method == "PUT":
            response = await client.put(url, data=data)
        elif method == "DELETE":
            response = await client.delete(url)
        else:
            raise ValueError("Unsupported HTTP method")
    return response