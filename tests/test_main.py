from unittest import TestCase
from main import Scanner


class TestScanner(TestCase):
    def test_process_response(self):
        data = [{
            "A": "B121"
        }, {
            "A": "B124"
        }, {
            "A": "B123"
        }, {
            "A": "B122"
        }, {
            "A": "B121"
        }]
        y = Scanner.process_response(data)
        self.assertTrue(y == ['B121', 'B124', 'B123', 'B122', 'B121'])

        data2 = {'args': {}, 'data': '', 'form': {}, 'headers': {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate',
                                                                 'User-Agent': 'Python/3.9 aiohttp/3.8.1',
                                                                 'X-Amzn-Trace-Id': 'Root=1-62248d95-52d1c5bb1f7d10141e4e5d13'},
                 'json': None, 'url': 'https://httpbin.org/post'}
        y = Scanner.process_response(data2)
        self.assertTrue(
            y == ['*/*', 'gzip, deflate', 'Python/3.9 aiohttp/3.8.1', 'Root=1-62248d95-52d1c5bb1f7d10141e4e5d13'])
