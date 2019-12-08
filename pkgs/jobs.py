#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os
from time import time

from aiocron import crontab
from aiohttp import ClientSession

from pkgs.repositories import LastAccessTimeRepository

SERVICE_NAME = 'emoji-generator'
URL = 'https://api.mackerelio.com/api/v0/services/{}/tsdb'.format(SERVICE_NAME)
METRIC_NAME = 'web_redirector.elapsed_seconds_since_last_access'
API_KEY = os.getenv('MACKEREL_API_KEY')


class MetricJob:
    def __init__(self, last_access_time_repository: LastAccessTimeRepository):
        self._last_access_time_repository = last_access_time_repository

        crontab('* * * * *', func=self.execute, start=True)

    async def execute(self):
        last_access_time = await self._last_access_time_repository.get()
        if last_access_time is None:
            return

        headers = {
            'conte-type': 'application/json',
            'x-api-key': API_KEY,
        }
        now_millis = int(time() * 1000)
        async with ClientSession() as session:
            metric_value = {
                'name': METRIC_NAME,
                'time': now_millis // 1000,
                'value': (now_millis - int(last_access_time.timestamp() * 1000)) // 1000,
            }
            print(metric_value)
            await session.post(URL, json=[metric_value], headers=headers)