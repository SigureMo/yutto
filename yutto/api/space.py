import math
import random

from aiohttp import ClientSession

from yutto.typing import AvId, BvId, MId, FavouriteMetadata
from yutto.utils.fetcher import Fetcher


async def get_uploader_space_all_videos_avids(session: ClientSession, mid: MId) -> list[AvId]:
    ps: int = random.randint(3, 10) * 10
    space_videos_api = (
        "https://api.bilibili.com/x/space/arc/search?mid={mid}&ps={ps}&tid=0&pn={pn}&order=pubdate&jsonp=jsonp"
    )
    pn = 1
    total = 1
    all_avid: list[AvId] = []
    while pn <= total:
        space_videos_url = space_videos_api.format(mid=mid, ps=ps, pn=pn)
        json_data = await Fetcher.fetch_json(session, space_videos_url)
        total = math.ceil(json_data["data"]["page"]["count"] / ps)
        pn += 1
        all_avid += [BvId(video_info["bvid"]) for video_info in json_data["data"]["list"]["vlist"]]
    return all_avid


async def get_uploader_name(session: ClientSession, mid: MId) -> str:
    space_info_api = "https://api.bilibili.com/x/space/acc/info?mid={mid}&jsonp=jsonp"
    space_info_url = space_info_api.format(mid=mid)
    uploader_info = await Fetcher.fetch_json(session, space_info_url)
    return uploader_info["data"]["name"]


async def get_fav_info(session: ClientSession, fid: str) -> FavouriteMetadata:
    api = f"https://api.bilibili.com/x/v3/fav/folder/info?media_id={fid}"
    json_data = await Fetcher.fetch_json(session, api)
    data = json_data["data"]
    return FavouriteMetadata(media_count=data["media_count"], title=data["title"])


async def get_fav_ids(session: ClientSession, fid: str) -> list[AvId]:
    api = f"https://api.bilibili.com/x/v3/fav/resource/ids?media_id={fid}"
    json_data = await Fetcher.fetch_json(session, api)
    rtn: list[AvId] = [BvId(video_info["bvid"]) for video_info in json_data["data"]]
    return rtn
