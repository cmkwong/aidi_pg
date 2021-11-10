import asyncio
import time
import aiohttp
import requests
from aiohttp.client import ClientSession

mainUrl = "https://aidi-work-helper.herokuapp.com/"
get_project_list_url = mainUrl + "api/v1/project/list"
prj_finish_url = mainUrl + "api/v1/project/status"

async def download_link_async(url, session):
    async with session.get(url) as response:
        result = await response.text()
        print(f'Read {len(result)} from {url}')

async def download_all_async(urls):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            task = asyncio.ensure_future(download_link_async(url=url,session=session))
            tasks.append(task)
        await asyncio.gather(*tasks,return_exceptions=True) # the await must be nest inside of the session

async def get_project_list_async():
    async with aiohttp.ClientSession() as session:
        async with session.get(get_project_list_url) as res:
            jsonBody = await res.json()
            return jsonBody['data']

def get_project_list():
    project_info = requests.get(get_project_list_url).json()['data']
    return project_info

def project_finish_update(project_id, locale, grader_name):
        data = {
            "project_id": project_id,
            "locale": locale,
            "grader": grader_name,
        }
        res = requests.post(prj_finish_url, data=data)

async def project_finish_update_async(project_id, locale, grader_name):
    async with aiohttp.ClientSession() as session:
        data = {
            "project_id": project_id,
            "locale": locale,
            "grader": grader_name,
        }
        res = await session.post(prj_finish_url, data=data)

# url_list = ["https://www.google.com","https://www.bing.com"]*10
# print(url_list)
# start = time.time()
# asyncio.run(download_all_async(url_list))
# end = time.time()
# print(f'download {len(url_list)} links in {end - start} seconds')
start = time.time()
project_list = asyncio.run(get_project_list_async())
end = time.time()
print(f'get project list async in {end - start} seconds')
start = time.time()
project_list = get_project_list()
end = time.time()
print(f'get project list in {end - start} seconds')

project_id = "CEval-random-open-2021-relevance-saf-2021-10-28-a"
locale = 'zh_HK'
grader = "ChrisCheung"
start = time.time()
project_list = asyncio.run(project_finish_update_async(project_id, locale, grader))
end = time.time()
print(f'post project finished async in {end - start} seconds')
start = time.time()
project_list = project_finish_update(project_id, locale, grader)
end = time.time()
print(f'post project finished in {end - start} seconds')
