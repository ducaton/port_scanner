from aiohttp.test_utils import AioHTTPTestCase
import main

class PortScannerTest(AioHTTPTestCase):

  async def get_application(self):
    return main.startServer()

  async def testOnePort(self):
    async with self.client.request("GET", "/scan/216.58.215.110/80/80") as resp:
      self.assertEqual(resp.status, 200)
      text = await resp.text()
    self.assertRegex(text, "\[\{\"port\": \"[0-9]+\", \"state\": \"(?:open|close)\"\}\]")