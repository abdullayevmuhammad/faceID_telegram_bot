import asyncio
async def test_all():
    urls = [
        "http://172.16.110.15/webs/addWhiteList",
        "http://172.16.110.15/webs/addPerson",
        "http://172.16.110.15/webs/addUser",
        "http://172.16.110.15/face/add",
        "http://172.16.110.15/face/user/add"
    ]

    for url in urls:
        print(f"\n🔍 Testing: {url}")
        from src.bot.config import FACEID_USERNAME, FACEID_PASSWORD
        import aiohttp, os

        form = aiohttp.FormData()
        form.add_field("username", FACEID_USERNAME)
        form.add_field("password", FACEID_PASSWORD)
        form.add_field("personId", "AB1234567")
        form.add_field(
            "photo",
            open("tmp_photos/AB1234567_2007357355.jpg", "rb"),
            filename="test.jpg",
            content_type="image/jpeg"
        )

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=form, timeout=15) as resp:
                    text = await resp.text()
                    print(f"Status: {resp.status}\n{text[:300]}...")
        except Exception as e:
            print(f"❌ Exception: {e}")

asyncio.run(test_all())
