import asyncio
from aiohttp import web
from ipaddress import ip_address
from json import dumps

routes = web.RouteTableDef()

async def portStatus(ip, port):
  s = asyncio.open_connection(ip, port)
  try:
    await asyncio.wait_for(s, timeout=1)
    s.close()
    return {"port": port, "state": "open"}
  except asyncio.TimeoutError:
    s.close()
    return {"port": port, "state": "close"}

def portScan(ip, pFrom, pTo):
  tasks = []
  for port in range(pFrom, pTo):
    tasks.append(asyncio.create_task(portStatus(ip, port)))
  results = asyncio.gather(*tasks)
  return results

#GET /scan/<ip>/<begin_port>/<end_port>
@routes.get("/scan/{tail:.*}")
async def portScanner(request):
  link = request.path.split("/")

  if len(link) != 5:
    return web.Response(text="Необходимый вид запроса: /scan/<ip>/<begin_port>/<end_port>", status=400)
  ip = link[2]

  try:
    pFrom = int(link[3])
    pTo = int(link[4])
  except ValueError:
    return web.Response(text="Порты должны цифрами", status=400)

  try:
    ip_address(ip)
  except:
    return web.Response(text="Указан некорректный IP", status=400)

  if not ((0 <= pFrom <= 65535) and (0 <= pTo <= 65535)):
    return web.Response(text="Порты должны быть в диапазоне от 0 до 65535", status=400)

  if pFrom > pTo:
    return web.Response(text="Необходимо указывать порты от меньшего к большему", status=400)
  
  scanResult = []
  # Больше значение = выше производительность, но слабые устройства могут не выдержать
  # Значения: 1-65535
  scanChunk = 65535

  if pTo - pFrom > scanChunk:
    for reqPart in range(pFrom, pTo, scanChunk):
      if pTo - reqPart < scanChunk:
        scanResult += await portScan(ip, reqPart, pTo)
      else:
        scanResult += await portScan(ip, reqPart, reqPart+scanChunk)
    # Чтобы range() не игнорировал последнее число
    scanResult += await portScan(ip, pTo, pTo+1)
  else:
    scanResult = await portScan(ip, pFrom, pTo+1)

  return web.Response(text=dumps(scanResult), headers={"content-type": "application/json"})

app = web.Application()
app.add_routes(routes)
web.run_app(app)