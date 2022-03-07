import asyncio
import os
from datetime import datetime
from glob import glob
from typing import Union
import argparse

import aiohttp
import requests

from db import Listing, init_db

APIURL = 'https://httpbin.org/post'
DBURL = "sqlite:///documents.sqlite"
BASEPATH = os.getcwd()
DATAPATH = r'\data'
CONCURRENCY = 5

os.chdir(BASEPATH)
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class Scanner(object):
    def __init__(self, path, concurrency):
        self.filenames = glob(fr'{path}\*.pdf')
        self.concurrency = concurrency
        init_db(DBURL)
        self._filenames_in_db()

    def _filenames_in_db(self):
        Listing.query.session.flush()
        for pdf_file_name in self.filenames:
            item = Listing.query_doc(pdf_file_name).one_or_none()
            try:
                size = os.path.getsize(pdf_file_name) * 1e-6
            except OSError:
                size = 0

            if not item:
                listing_for_db = Listing(doc_name=pdf_file_name,
                                         scan_date=None,
                                         scan_results=None,
                                         size_in_mb=size
                                         )
                Listing.query.session.add(listing_for_db)
                Listing.query.session.flush()

    def scan(self, number, sync):
        now = datetime.now()
        if sync:
            self.send_files_to_api_sync(number)
        else:
            self.send_files_to_api_async(number)
        elapsed = datetime.now()
        seconds = (elapsed - now).seconds
        print(f'Processed {number} documents in {seconds=}. Average {round(number / seconds, 3)} documents per second')

    def send_files_to_api_async(self, number):
        filenames = self._pick_files_to_process(number)
        asyncio.run(self.send_to_api_multiple(filenames))

    def send_files_to_api_sync(self, number):
        filenames = self._pick_files_to_process(number)
        for filename in filenames:
            try:
                file = open(filename, 'rb')
            except (OSError, TypeError) as e:
                print(f'file {filename} cannot be opened')
                raise ValueError('Os error') from e
            try:
                result = requests.post(url=APIURL, verify=False, files={'file': file})
                result.raise_for_status()
                data = self.process_response(result.json())
                self._update_db(filename, data)
            except (requests.HTTPError, requests.Timeout) as e:
                print(f'exception {e}')
                raise ValueError('Connection error') from e

    async def send_to_api_multiple(self, filenames):
        conn = aiohttp.TCPConnector(ssl=False, limit=self.concurrency)

        async with aiohttp.ClientSession(connector=conn) as session:
            tasks = []
            for filename in filenames:
                try:
                    file = open(filename, 'rb')
                except (OSError, TypeError) as e:
                    print(f'file {filename} cannot be opened')
                    raise ValueError('Os error') from e
                task = asyncio.ensure_future(self.async_call_api(file=file, session=session, filename=filename))
                tasks.append(task)
            return await asyncio.gather(*tasks, return_exceptions=True)

    async def async_call_api(self, session, file, filename):
        async with session.post(APIURL, data={'file': file}) as response:
            try:
                k = await response.json()
                data = self.process_response(k)
                self._update_db(filename, data)
            except Exception as e:
                print(f'exception {e}')
                raise ValueError('Connection error') from e

    @staticmethod
    def _update_db(item_name, api_result):
        item = Listing.query_doc(item_name).one()
        item.scan_date = datetime.now()
        item.scanned = True
        item.scan_results = ' , '.join(api_result)
        Listing.query.session.add(item)
        Listing.query.session.flush()

    @staticmethod
    def process_response(data: Union[list, dict]) -> list:
        if isinstance(data, dict) and data.get('headers'):
            data = data['headers']
            return list(data.values())
        elif isinstance(data, list):
            key = list(data[0].keys())[0]
            data = [f[key] for f in data]
            return data
        return data

    @staticmethod
    def _pick_files_to_process(number: int) -> list:
        item = []
        for _ in range(3):
            if item := Listing.query_doc(scanned=False).limit(number).all():
                for x in item:
                    if x.size_in_mb > 10:
                        item.scanned = True
                        Listing.query.session.add(item)
                        Listing.query.session.flush()
            if len(item) == number:
                return [file.doc_name for file in item]
        return [file.doc_name for file in item]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-sync', action="store_true", default=False, help="Sync or async operation")
    parser.add_argument('-number', type=int, default=5, help='Number of documents to scan')
    parser.add_argument('-rate', type=int, default=CONCURRENCY, help='Max concurrency for asyncio')
    args = parser.parse_args()
    scanner = Scanner(f'{BASEPATH}{DATAPATH}', args.rate)
    scanner.scan(args.number, sync=args.sync)
