import asyncio
import asyncpg
import json
from aiohttp import web

import shapely.geometry
import shapely.wkb
from shapely.geometry.base import BaseGeometry

settings = {}

# Read SQL Auth data
with open('settings.json') as json_file:
    settings = json.load(json_file)

class Webserver:
    def __init__(self, pool, loop):
        self.pool = pool
        self.loop = loop

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
    async def list_crashes(self, request):
        request_json = request.json()

        sql = """
        SELECT ID, SeverityIndex, NearestAADT, Location
        FROM CrashLocations
        WHERE
            {}
        ORDER BY SeverityIndex DESC
        LIMIT 1000
        """

        # List of tuples, with first value being the SQL, second being a list of arguments
        conditions = []

        # Boundaries
        if 'corner1' in request_json and 'corner2' in request_json:
             conditions.append(
                ("Location @ ST_MakeEnvelope ({}, {}, {}, {}, 4283)",
                    [request_json['corner1'][0], request_json['corner1'][1],
                    request_json['corner2'][0], request_json['corner2'][1]]))

        # Years
        if 'yearmax' in request_json:
            conditions.append(("EXTRACT(YEAR FROM TIMESTAMP CrashDate) <= {}",
                [request_json['yearmax']]))

        if 'yearmin' in request_json:
            conditions.append(("EXTRACT(YEAR FROM TIMESTAMP CrashDate) >= {}",
                [request_json['yearmin']]))

        conditions_compiled = "\nAND ".join([c[0] for c in conditions])

        current_var = 1
        condition_variables = []
        for condition in conditions:
            condition_variables.extend(condition[1])
            current_var += len(condition[1])

        conditions_compiled.format(*[f'${n}' for n in range(current_var)])

        sql.format(conditions_compiled)

        async with self.pool.acquire() as con:
            results = await con.fetch(sql, *condition_variables)

        return aiohttp.web.json_response(results, status=200)

    '''
    Get a specific crash by ID

    JSON Post request with format:

    {
        "id": <crash ID>,
    }
    id required

    Returns all data with the same keys as the database.
    '''
    async def get_crash(self, request):
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
    async def list_census_sites(self, request):
        pass

    '''
    Build the web server and setup routes
    '''
    async def build_server(self, address, port):
        app = web.Application(loop=self.loop)
        app.router.add_route('POST', "/list_crashes", self.list_crashes)
        app.router.add_route('POST', "/get_crash", self.list_crashes)
        app.router.add_route('POST', "/list_census_sites", self.list_crashes)

        return await self.loop.create_server(app.make_handler(), address, port)

async def start_webserver(loop):
    async def init_connection(conn):
        def encode_geometry(geometry):
            if not hasattr(geometry, '__geo_interface__'):
                raise TypeError('{g} does not conform to '
                                'the geo interface'.format(g=geometry))
            shape = shapely.geometry.asShape(geometry)
            return shapely.wkb.dumps(shape)

        def decode_geometry(wkb):
            return shapely.wkb.loads(wkb)

        await conn.set_type_codec(
            'geography',
            encoder=encode_geometry,
            decoder=decode_geometry,
            format='binary',
        )

    pool = await asyncpg.create_pool(user=settings['psql_user'], password=settings['psql_pass'],
        database=settings['psql_dbname'], host=settings['psql_host'], init=init_connection)

    webserver = Webserver(pool, loop)
    await webserver.build_server('localhost', 9999)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_webserver(loop))
    print("Server ready!")

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Shutting Down!")
        loop.close()