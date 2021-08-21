import asyncio
from aiohttp import web

'''
List crashes given filters and lat/long

JSON Post request with format:

{
    "corner1": [lat, long],
    "corner2": [lat, long],
    "vehicle_types": ['car', 'motorcycle', 'truck', 'bus', 'bicycle', 'pedestrian', 'other'],
    "yearmax": year,
    "yearmin": year,
    "severity": [list of IDs],
    "nature": [list of IDs],
    "type": [list of IDs],
    "sealed": True/False,
    "dry": True/False,
    "weather": [list of IDs],
    "day": True/False,
    "partialday": True/False,
    "lit": True/False
}
If any fields are not used, they will not be filtered. This will return the top X number of records,
ordered from least to most severe in JSON format.
'''
async def list_crashes(request):
    pass

'''
Get a specific crash by ID

JSON Post request with format:

{
    "id": <crash ID>,
}
id required

Returns all data with the same keys as the database.
'''
async def get_crash(request):
    pass

'''
List crashes given filters and lat/long

JSON Post request with format:

{
    "corner1": [lat, long],
    "corner2": [lat, long],
    "yearmax": year,
    "yearmin": year,
    "onlylatest": True/False
}

Returns a list of the top X most used census sites. If onlylatest is true, only the most recent data at that site is sent.
The returned values are
'''
async def list_census_sites(request):
    pass

'''
Build the web server and setup routes
'''
async def build_server(loop, address, port):

    app = web.Application(loop=loop)
    app.router.add_route('POST', "/list_crashes", list_crashes)
    app.router.add_route('POST', "/get_crash", list_crashes)
    app.router.add_route('POST', "/list_census_sites", list_crashes)

    return await loop.create_server(app.make_handler(), address, port)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(build_server(loop, 'localhost', 9999))
    print("Server ready!")

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Shutting Down!")
        loop.close()