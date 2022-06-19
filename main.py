import asyncio
from aiohttp import web
from ipaddress import ip_address
from json import dumps
from syslog import syslog

routes = web.RouteTableDef()

async def portStatus(ip, port):
  try:
    s = asyncio.open_connection(ip, port)
    try:
      await asyncio.wait_for(s, timeout=1)
      s.close()
      return {"port": port, "state": "open"}
    except asyncio.TimeoutError:
      s.close()
      return {"port": port, "state": "close"}
  except:
    return {"port": port, "state": "close"}

async def portScan(ip, pFrom, pTo):
  tasks = []
  for port in range(pFrom, pTo):
    tasks.append(asyncio.create_task(portStatus(ip, port)))
  results = asyncio.gather(*tasks)
  return await results

#GET /scan/<ip>/<begin_port>/<end_port>
@routes.get("/scan/{tail:.*}")
async def portScanner(request):
  syslog(6, request.remote + " " + request.method + " " + request.path)

  link = request.path.split("/")

  if len(link) != 5:
    err = "Необходимый вид запроса: /scan/<ip>/<begin_port>/<end_port>"
    syslog(6, request.remote + " - некорректный запрос: " + err)
    return web.Response(text=err, status=400)
  ip = link[2]

  try:
    pFrom = int(link[3])
    pTo = int(link[4])
  except ValueError:
    err = "Порты должны цифрами"
    syslog(6, request.remote + " - некорректный запрос: " + err)
    return web.Response(text=err, status=400)

  try:
    ip_address(ip)
  except:
    err = "Указан некорректный IP"
    syslog(6, request.remote + " - некорректный запрос: " + err)
    return web.Response(text=err, status=400)

  if not ((0 <= pFrom <= 65535) and (0 <= pTo <= 65535)):
    err = "Порты должны быть в диапазоне от 0 до 65535"
    syslog(6, request.remote + " - некорректный запрос: " + err)
    return web.Response(text=err, status=400)

  if pFrom > pTo:
    err = "Необходимо указывать порты от меньшего к большему"
    syslog(6, request.remote + " - некорректный запрос: " + err)
    return web.Response(text=err, status=400)

  scanResult = []
  # Больше значение = выше производительность, но слабые устройства могут не выдержать
  # Ограничено операционной системой (ulimit -n)
  # Значения: 1-65535
  scanChunkSize = 1000

  # Если диапазон превышает размер куска, то сканировать по частям
  if pTo - pFrom > scanChunkSize:
    for reqPart in range(pFrom, pTo, scanChunkSize):
      # Если осталось сканировать меньше, чем ограничено куском, то его не использовать
      if pTo - reqPart < scanChunkSize:
        scanResult += await portScan(ip, reqPart, pTo)
      # Сканирование по размеру куска
      else:
        scanResult += await portScan(ip, reqPart, reqPart+scanChunkSize)
    # Чтобы range() не игнорировал последнее число
    scanResult += await portScan(ip, pTo, pTo+1)
  else:
    scanResult += await portScan(ip, pFrom, pTo+1)

  syslog(6, request.remote + " - диапазон просканирован и отправлен")
  return web.Response(text=dumps(scanResult), headers={"content-type": "application/json"})

app = web.Application()
app.add_routes(routes)
web.run_app(app)
