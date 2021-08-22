'''
Process the CSVs from the open data portal and export into the postgresql database.

To minimize memory usage for large files (such as the crash location files),
the data will be processed as it is downloaded and processed in batches of
100 records into the postgresql database.

The datasets being used are:

- Road crash locations
- Road census data
'''
import json
import asyncio
import asyncpg
import aiohttp
import datetime
import sys

import shapely.geometry
import shapely.wkb
from shapely.geometry.base import BaseGeometry


ROAD_CENSUS_URLS = {
    2009: "http://www.tmr.qld.gov.au/-/media/aboutus/corpinfo/Open%20data/trafficcensus/trafficcensus2004-2009.csv",
    2010: "http://www.tmr.qld.gov.au/~/media/aboutus/corpinfo/Open%20data/trafficcensus/trafficcensus2010csv.csv",
    2011: "http://www.tmr.qld.gov.au/~/media/aboutus/corpinfo/Open%20data/trafficcensus/trafficcensus2011csv.csv",
    2012: "http://www.tmr.qld.gov.au/~/media/aboutus/corpinfo/Open%20data/trafficcensus/trafficcensus2012.csv",
    2013: "http://www.tmr.qld.gov.au/~/media/aboutus/corpinfo/Open%20data/trafficcensus/traffic_census_2013.csv",
    2014: "http://www.tmr.qld.gov.au/~/media/aboutus/corpinfo/Open%20data/trafficcensus/trafficcensus2014.csv",
    2015: "http://www.tmr.qld.gov.au/-/media/aboutus/corpinfo/Open%20data/trafficcensus/trafficcensus2015.csv",
    2016: "http://www.tmr.qld.gov.au/-/media/aboutus/corpinfo/Open%20data/trafficcensus/trafficcensus2016_csv.csv",
    2017: "http://www.tmr.qld.gov.au/-/media/aboutus/corpinfo/Open%20data/trafficcensus/trafficcensus2017.csv",
    2018: "http://www.tmr.qld.gov.au/-/media/aboutus/corpinfo/Open%20data/trafficcensus/trafficcensus2018.csv",
    2019: "https://www.data.qld.gov.au/dataset/5d74e022-a302-4f40-a594-f1840c92f671/resource/dc82ec39-4513-437c-8d07-ecb08474a065/download/trafficcensus2019.csv",
    2020: "https://www.data.qld.gov.au/dataset/5d74e022-a302-4f40-a594-f1840c92f671/resource/1f52e522-7cb8-451c-b4c2-8467a087e883/download/trafficcensus2020.csv",
}

ROAD_CRASHES_URL = "https://www.data.qld.gov.au/dataset/f3e0ca94-2d7b-44ee-abef-d6b06e9b0729/resource/e88943c0-5968-4972-a15f-38e120d72ec0/download/1_crash_locations.csv"

CREATE_CRASH_LOCATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS CrashLocations (
    ID INTEGER PRIMARY KEY,
    SeverityIndex INTEGER NOT NULL,
    NearestAADT INTEGER,
    SeverityID SMALLINT NOT NULL,
    NatureID SMALLINT NOT NULL,
    TypeID SMALLINT NOT NULL,
    RoadwayFeatureID SMALLINT,
    TrafficControlID SMALLINT,
    AtmosphericConditionID SMALLINT,
    CrashDate TIMESTAMP NOT NULL,
    Location GEOGRAPHY NOT NULL,
    Street VARCHAR(255),
    StreetIntersecting VARCHAR(255),
    Suburb VARCHAR(255),
    Council VARCHAR(255),
    Postcode INTEGER,
    SpeedLimit SMALLINT, -- upper level speed limit
    Sealed BOOLEAN,
    Dry BOOLEAN,
    Day BOOLEAN,
    Lit BOOLEAN, -- Artificially lit
    PartialDaylight BOOLEAN, -- dawn/dusk
    ApproachBearing VARCHAR(1), -- N,E,S,W
    Description TEXT,
    InvolvedGroupDescription TEXT,
    CasualtyFatality SMALLINT NOT NULL,
    CasualtyHospital SMALLINT NOT NULL,
    CasualtyMedicallyTreated SMALLINT NOT NULL,
    CasualtyMinorInjury SMALLINT NOT NULL,
    InvolvedCar SMALLINT NOT NULL,
    InvolvedMotorcycle SMALLINT NOT NULL,
    InvolvedTruck SMALLINT NOT NULL,
    InvolvedBus SMALLINT NOT NULL,
    InvolvedBicycle SMALLINT NOT NULL,
    InvolvedPedestrian SMALLINT NOT NULL,
    InvolvedOther SMALLINT NOT NULL,
    CONSTRAINT fk_severity
        FOREIGN KEY(SeverityID)
        REFERENCES CrashSeverity(ID),
    CONSTRAINT fk_nature
        FOREIGN KEY(NatureID)
        REFERENCES CrashNature(ID),
    CONSTRAINT fk_type
        FOREIGN KEY(TypeID)
        REFERENCES CrashType(ID),
    CONSTRAINT fk_roadway_feature
        FOREIGN KEY(RoadwayFeatureID)
        REFERENCES RoadwayFeature(ID),
    CONSTRAINT fk_traffic_control
        FOREIGN KEY(TrafficControlID)
        REFERENCES TrafficControl(ID),
    CONSTRAINT fk_atmospheric_condition
        FOREIGN KEY(AtmosphericConditionID)
        REFERENCES AtmosphericCondition(ID)
);
"""

CREATE_ROAD_CENSUS_TABLE = """
CREATE TABLE IF NOT EXISTS CensusLocations (
    ID INTEGER PRIMARY KEY, -- Record ID
    SiteID INTEGER NOT NULL,
    Year SMALLINT NOT NULL,
    Location GEOGRAPHY NOT NULL,
    AADT INTEGER NOT NULL,
    PcntHV NUMERIC(5, 2)
);
"""

CRASH_SEVERITIES = {
    1: "Fatal",
    2: "Hospitalisation",
    3: "Medical treatment",
    4: "Minor injury",
    5: "Property damage only",
}

CRASH_NATURE = {
    1: "Angle",
    2: "Collision - miscellaneous",
    3: "Fall from vehicle",
    4: "Head-on",
    5: "Hit animal",
    6: "Hit object",
    7: "Hit parked vehicle",
    8: "Hit pedestrian",
    9: "Non-collision - miscellaneous",
    10: "Other",
    11: "Overturned",
    12: "Rear-end",
    13: "Sideswipe",
    14: "Struck by external load",
    15: "Struck by internal load",
}

CRASH_TYPES = {
    1: "Hit pedestrian",
    2: "Multi-Vehicle",
    3: "Other",
    4: "Single Vehicle",
}

CRASH_ROADWAY_FEATURES = {
    1: "No Roadway Feature",
    2: "Intersection - Cross",
    3: "Intersection - T-Junction",
    4: "Intersection - Roundabout",
    5: "Bridge/Causeway",
    6: "Median Opening",
    7: "Intersection - Y-Junction",
    8: "Intersection - Interchange",
    9: "Merge Lane",
    10: "Intersection - Multiple Road",
    11: "Bikeway",
    12: "Other",
    13: "Intersection - 5+ way",
    14: "Railway Crossing",
    15: "Forestry/National Park Road",
    16: "Miscellaneous",
}

CRASH_TRAFFIC_CONTROL = {
    1: "No traffic control",
    2: "Operating traffic lights",
    3: "Give way sign",
    4: "Stop sign",
    5: "Police",
    6: "Flashing amber lights",
    7: "Pedestrian crossing sign",
    8: "Road/Rail worker",
    9: "School crossing - flags",
    10: "Railway - lights and boom gate",
    11: "Pedestrian operated lights",
    12: "LATM device",
    13: "Miscellaneous",
    14: "Railway crossing sign",
    15: "Supervised school crossing",
    16: "Railway - lights only",
    17: "Other",
}

CRASH_TRAFFIC_CONTROL = {
    1: "No traffic control",
    2: "Operating traffic lights",
    3: "Give way sign",
    4: "Stop sign",
    5: "Police",
    6: "Flashing amber lights",
    7: "Pedestrian crossing sign",
    8: "Road/Rail worker",
    9: "School crossing - flags",
    10: "Railway - lights and boom gate",
    11: "Pedestrian operated lights",
    12: "LATM device",
    13: "Miscellaneous",
    14: "Railway crossing sign",
    15: "Supervised school crossing",
    16: "Railway - lights only",
    17: "Other",
}

CRASH_LIGHTING_CONDITIONS = {
    "Daylight": {"Day": True, "Lit": True, "PartialDaylight": False},
    "Darkness - Lighted": {"Day": False, "Lit": True, "PartialDaylight": False},
    "Darkness - Not lighted": {"Day": False, "Lit": False, "PartialDaylight": False},
    "Dawn/Dusk": {"Day": False, "Lit": False, "PartialDaylight": True},
}

CRASH_ATMOSPHERIC_CONDITIONS = {
    1: "Clear",
    2: "Raining",
    3: "Fog",
    4: "Smoke/Dust",
}


settings = {}

# Read SQL Auth data
with open('settings.json') as json_file:
    settings = json.load(json_file)

'''
CSV Line Generator.

Accepts a URL and returns a series of dicts for each line in the CSV.
'''
async def read_csv_by_line(url):
    async with aiohttp.ClientSession(raise_for_status=True) as session:
        keys = None
        async with session.get(url) as r:
            async for line in r.content:
                dataline = line.decode("utf-8").strip().split(',')
                if keys == None:
                    keys = dataline
                else:
                    data = dict(zip(keys,dataline))
                    yield data

'''
Reads crash data CSV, calculates the severity index, reformats where
necessary and imports it in batches of 100 rows into the database
'''
async def import_crashdata(db):
    insert_row = """
        INSERT INTO CrashLocations
        (
            ID,
            SeverityIndex,
            NearestAADT,
            SeverityID,
            NatureID,
            TypeID,
            RoadwayFeatureID,
            TrafficControlID,
            AtmosphericConditionID,
            CrashDate,
            Location,
            Street,
            StreetIntersecting,
            Suburb,
            Council,
            Postcode,
            SpeedLimit,
            Sealed,
            Dry,
            Day,
            Lit,
            PartialDaylight,
            ApproachBearing,
            Description,
            InvolvedGroupDescription,
            CasualtyFatality,
            CasualtyHospital,
            CasualtyMedicallyTreated,
            CasualtyMinorInjury,
            InvolvedCar,
            InvolvedMotorcycle,
            InvolvedTruck,
            InvolvedBus,
            InvolvedBicycle,
            InvolvedPedestrian,
            InvolvedOther
        )
        VALUES
        (
            $1,
            (
                30*$24::int4+
                10*$25::int4+
                5*$26::int4+
                1*$27::int4+
                2*(
                    $28::int4+
                    $29::int4+
                    $30::int4+
                    $31::int4+
                    $32::int4+
                    $33::int4+
                    $34::int4
                )
            ),
            1,
            --(
            --    SELECT AADT
            --    FROM CensusLocations cl
            --    WHERE
            --        EXTRACT(YEAR FROM TIMESTAMP $8) <= cl.Year
            --    ORDER BY ST_Distance('SRID=4283;POINT($9 $10)', cl.Locations, false) DESC
            --    LIMIT 1
            --),
            (SELECT ID FROM CrashSeverity WHERE NAME = $2),
            (SELECT ID FROM CrashNature WHERE NAME = $3),
            (SELECT ID FROM CrashType WHERE NAME = $4),
            (SELECT ID FROM RoadwayFeature WHERE NAME = $5),
            (SELECT ID FROM TrafficControl WHERE NAME = $6),
            (SELECT ID FROM AtmosphericCondition WHERE NAME = $7),
            $8, -- CrashDate
            ST_GeographyFromText($9::text),
            $10, -- Street
            $11, -- StreetIntersecting
            $12, -- Suburb
            $13, -- Council
            $14, -- Postcode
            $15, -- SpeedLimit
            $16, -- Sealed
            $17, -- Dry
            $18, -- Day
            $19, -- Lit
            $20, -- PartialDaylight
            $21, -- ApproachBearing
            $22, -- Description
            $23, -- InvolvedGroupDescription
            $24, -- CasualtyFatality
            $25, -- CasualtyHospital
            $26, -- CasualtyMedicallyTreated
            $27, -- CasualtyMinorInjury
            $28, -- InvolvedCar
            $29, -- InvolvedMotorcycle
            $30, -- InvolvedTruck
            $31, -- InvolvedBus
            $32, -- InvolvedBicycle
            $33, -- InvolvedPedestrian
            $34 -- InvolvedOther
        );
    """
    stmt = await db.prepare(insert_row)

    num = 1
    async with db.transaction():
        async for data in read_csv_by_line(ROAD_CRASHES_URL):
            try:
                if data['Crash_Longitude_GDA94'] != '0':
                    unknown_to_zero = (
                            'Crash_Ref_Number',
                            'Loc_Post_Code',
                            'Count_Casualty_Fatality',
                            'Count_Casualty_Hospitalised',
                            'Count_Casualty_MedicallyTreated',
                            'Count_Casualty_MinorInjury',
                            'Count_Unit_Car',
                            'Count_Unit_Motorcycle_Moped',
                            'Count_Unit_Truck',
                            'Count_Unit_Bus',
                            'Count_Unit_Bicycle',
                            'Count_Unit_Pedestrian',
                            'Count_Unit_Other',
                        )
                    for key in unknown_to_zero:
                        if key in data:
                            try:
                                data[key] = int(data[key])
                            except:
                                data[key] = 0

                    args = [
                            data['Crash_Ref_Number'],
                            data['Crash_Severity'],
                            data['Crash_Nature'],
                            data['Crash_Type'],
                            data['Crash_Roadway_Feature'],
                            data['Crash_Traffic_Control'],
                            data['Crash_Atmospheric_Condition'],
                            datetime.datetime.strptime(f"{data['Crash_Year']} {data['Crash_Month']} {data['Crash_Hour']}", "%Y %B %H"),
                            f"SRID=4283;POINT({data['Crash_Longitude_GDA94']} {data['Crash_Latitude_GDA94']})",
                            data['Crash_Street'],
                            data['Crash_Street_Intersecting'],
                            data['Loc_Suburb'],
                            data['Loc_Local_Government_Area'],
                            data['Loc_Post_Code'],
                            int(data['Crash_Speed_Limit'].split(' ')[-2]),
                            data['Crash_Road_Surface_Condition'].startswith('Sealed'),
                            data['Crash_Road_Surface_Condition'].endswith('Dry'),
                            data['Crash_Lighting_Condition'] == 'Daylight',
                            data['Crash_Lighting_Condition'] == 'Darkness - Lighted',
                            data['Crash_Lighting_Condition'] == 'Dawn/Dusk',
                            data['DCA_Key_Approach_Dir'],
                            data['Crash_DCA_Description'],
                            data['Crash_DCA_Group_Description'],
                            data['Count_Casualty_Fatality'],
                            data['Count_Casualty_Hospitalised'],
                            data['Count_Casualty_MedicallyTreated'],
                            data['Count_Casualty_MinorInjury'],
                            data['Count_Unit_Car'],
                            data['Count_Unit_Motorcycle_Moped'],
                            data['Count_Unit_Truck'],
                            data['Count_Unit_Bus'],
                            data['Count_Unit_Bicycle'],
                            data['Count_Unit_Pedestrian'],
                            data['Count_Unit_Other']
                        ]

                    await stmt.executemany([args])
            except:
                print(f"Record failed")

            sys.stdout.write("\r Processing record: %i" % num)
            sys.stdout.flush()
            num += 1

    print(f"Copied crashdata.")

async def run():
    db = await asyncpg.connect(user=settings['psql_user'], password=settings['psql_pass'],
        database=settings['psql_dbname'], host=settings['psql_host'])

    await db.execute(CREATE_CRASH_LOCATIONS_TABLE)
    await db.execute(CREATE_ROAD_CENSUS_TABLE)

    await import_crashdata(db)

loop = asyncio.get_event_loop()
loop.run_until_complete(run())