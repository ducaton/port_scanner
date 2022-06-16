from aiohttp import web
from ipaddress import ip_address

routes = web.RouteTableDef()

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

  if pFrom >= pTo:
    return web.Response(text="Необходимо указывать порты от меньшего к большему. Разница между портами не должна быть нулевой", status=400)

  return web.Response(text="Проверка портов у "+ip+" от "+str(pFrom)+" до "+str(pTo))

app = web.Application()
app.add_routes(routes)
web.run_app(app)