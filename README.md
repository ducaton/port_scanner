# Сканер портов
## Задание
Разработать web-приложение, занимающееся сканированием открытых TCP портов указанного хоста.
Сканирование запускается следующим REST запросом:

    * GET /scan/<ip>/<begin_port>/<end_port>

* ip - хост, который необходимо просканировать
* begin_port - начала диапозона портов для сканирования
* end_port - конец диапозона портов для сканирования

Ожидаемый ответ:  [{"port": "integer", "state": "(open|close)"}]
    
Требования:

* Aiohttp, Python3.9 или выше;
* логи в syslog - входящие запросы, ошибки и т.д.

Дополнительно:

* тесты AioHTTPTestCase;
* .spec для сборки RPM-пакета под Fedora 35.

## Тестирование
* указать IP для сканирования в `test_duc_port_scanner.py`
* `python -m unittest -v`
## Запуск
`python duc_port_scanner.py`
## Использование
`GET localhost:54321/scan/<ip>/<begin_port>/<end_port>`

Например командой:

`curl localhost:54321/scan/127.0.0.1/0/200`