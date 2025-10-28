import aiohttp
import asyncio

AUTH_HEADER_VALUE = "Basic YWRtaW46YWlmdTFxMnczZTRyQA=="
host = "http://172.16.110.15"


async def check_raw():
    async with aiohttp.ClientSession() as s:
        url = (
            f"{host}/webs/getWhitelist?"
            "action=list&group=LIST&uflag=0&uage=0-100&MjCardNo=0"
            "&begintime=2023-01-24/00:00:00&endtime=2025-03-16/23:59:59"
            "&utype=3&sequence=0&beginno=0&reqcount=10000&usex=0"
            "&sessionid=0&RanId=123456"
        )

        headers = {
            "x-request-id": "f77e4be4-b9e0-4fdd-9f27-370cbbbffb82",
            "Authorization": AUTH_HEADER_VALUE
        }

        async with s.get(url, headers=headers, timeout=20) as r:
            text = await r.text()
            print("=== JAVOB ===")
            print(text[-300:])  # faqat oxirgi 300 ta qator chiqadi


asyncio.run(check_raw())
