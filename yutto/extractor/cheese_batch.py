from __future__ import annotations

import argparse
import re
from collections.abc import Coroutine
from typing import Any

import aiohttp

from yutto._typing import EpisodeData, EpisodeId, SeasonId
from yutto.api.cheese import get_cheese_list, get_season_id_by_episode_id
from yutto.extractor._abc import BatchExtractor
from yutto.extractor.common import extract_cheese_data
from yutto.processor.selector import parse_episodes_selection
from yutto.utils.console.logger import Badge, Logger


class CheeseBatchExtractor(BatchExtractor):
    """番剧全集"""

    REGEX_EP = re.compile(r"https?://www\.bilibili\.com/cheese/play/ep(?P<episode_id>\d+)")
    REGEX_SS = re.compile(r"https?://www\.bilibili\.com/cheese/play/ss(?P<season_id>\d+)")

    REGEX_EP_ID = re.compile(r"ep(?P<episode_id>\d+)")
    REGEX_SS_ID = re.compile(r"ss(?P<season_id>\d+)")

    _match_result: re.Match[Any]
    season_id: SeasonId

    def resolve_shortcut(self, id: str) -> tuple[bool, str]:
        matched = False
        url = id
        if match_obj := self.REGEX_EP_ID.match(id):
            url = f"https://www.bilibili.com/cheese/play/ep{match_obj.group('episode_id')}"
            matched = True
        elif match_obj := self.REGEX_SS_ID.match(id):
            url = f"https://www.bilibili.com/cheese/play/ss{match_obj.group('season_id')}"
            matched = True
        return matched, url

    def match(self, url: str) -> bool:
        if (match_obj := self.REGEX_SS.match(url)) or (match_obj := self.REGEX_EP.match(url)):
            self._match_result = match_obj
            return True
        else:
            return False

    async def _parse_ids(self, session: aiohttp.ClientSession):
        if "episode_id" in self._match_result.groupdict().keys():
            episode_id = EpisodeId(self._match_result.group("episode_id"))
            self.season_id = await get_season_id_by_episode_id(session, episode_id)
        else:
            self.season_id = SeasonId(self._match_result.group("season_id"))

    async def extract(
        self, session: aiohttp.ClientSession, args: argparse.Namespace
    ) -> list[Coroutine[Any, Any, EpisodeData | None] | None]:
        await self._parse_ids(session)

        cheese_list = await get_cheese_list(session, self.season_id)
        Logger.custom(cheese_list["title"], Badge("课程", fore="black", back="cyan"))
        # 如果没有 with_section 则不需要专区内容
        cheese_list["pages"] = list(
            filter(lambda item: args.with_section or not item["is_section"], cheese_list["pages"])
        )
        # 选集过滤
        episodes = parse_episodes_selection(args.episodes, len(cheese_list["pages"]))
        cheese_list["pages"] = list(filter(lambda item: item["id"] in episodes, cheese_list["pages"]))
        return [
            extract_cheese_data(
                session,
                cheese_item["episode_id"],
                cheese_item,
                args,
                {
                    "title": cheese_list["title"],
                },
                "{title}/{name}",
            )
            for cheese_item in cheese_list["pages"]
        ]
