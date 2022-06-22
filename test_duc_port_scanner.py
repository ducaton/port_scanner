import duc_port_scanner
from aiohttp.test_utils import AioHTTPTestCase
from random import randrange
from json import loads

ip = "216.58.215.110"

class PortScannerTest(AioHTTPTestCase):

  async def get_application(self):
    return duc_port_scanner.startServer()

  async def testIfPortFromIsInt(self):
    async with self.client.request("GET", "/scan/" + ip + "/uh/300") as resp:
      self.assertEqual(resp.status, 400)
      text = await resp.text()
    self.assertEqual(text, "Порты должны быть цифрами")

  async def testIfPortToIsInt(self):
    async with self.client.request("GET", "/scan/" + ip + "/100/500.5") as resp:
      self.assertEqual(resp.status, 400)
      text = await resp.text()
    self.assertEqual(text, "Порты должны быть цифрами")

  async def testIpValidation(self):
    async with self.client.request("GET", "/scan/216.588.215.110/100/300") as resp:
      self.assertEqual(resp.status, 400)
      text = await resp.text()
    self.assertEqual(text, "Указан некорректный IP")

  async def testIfPortFromInRange(self):
    async with self.client.request("GET", "/scan/" + ip + "/-50/300") as resp:
      self.assertEqual(resp.status, 400)
      text = await resp.text()
    self.assertEqual(text, "Порты должны быть в диапазоне от 0 до 65535")

  async def testIfPortToInRange(self):
    async with self.client.request("GET", "/scan/" + ip + "/0/66666") as resp:
      self.assertEqual(resp.status, 400)
      text = await resp.text()
    self.assertEqual(text, "Порты должны быть в диапазоне от 0 до 65535")

  async def testThatPortsAreFromLessToMore(self):
    async with self.client.request("GET", "/scan/" + ip + "/300/100") as resp:
      self.assertEqual(resp.status, 400)
      text = await resp.text()
    self.assertEqual(text, "Необходимо указывать порты от меньшего к большему")

  async def testOnePort(self):
    port = randrange(0, 65536)
    expected = "\[\{\"port\": \"" + str(port) + "\", \"state\": \"(?:open|close)\"\}\]"
    async with self.client.request("GET", "/scan/" + ip + "/" + str(port) + "/" + str(port) + "") as resp:
      self.assertEqual(resp.status, 200)
      respText = await resp.text()
    self.assertRegex(respText, expected)

  async def testPortRange(self):
    pFrom = randrange(0, 63536)
    pTo = pFrom + 2000
    pRange = []
    err = ""
    for port in range(pFrom, pTo+1):
      pRange.append(str(port))
    async with self.client.request("GET", "/scan/" + ip + "/" + str(pFrom) + "/" + str(pTo) + "") as resp:
      self.assertEqual(resp.status, 200)
      respText = await resp.text()
    respText = loads(respText)
    for element in respText:
      if "port" not in element:
        err = "В " + str(element) + " нет ключа \'port\'"
        break
      if element['port'] not in pRange:
        err = "В " + str(element) + " значение ключа \'port\' выходит за заданный диапазон " + str(pFrom) + "-" + str(pTo)
        break
      if "state" not in element:
        err = "В " + str(element) + " нет ключа \'state\'"
        break
      if (element['state'] != "open") and (element['state'] != "close"):
        err = "В " + str(element) + " значение ключа \'state\' не содержит значений \'open\' или \'close\' "
        break
    self.assertEqual(err, "")