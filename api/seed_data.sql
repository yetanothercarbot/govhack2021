IF EXISTS (SELECT FROM pg_catalog.pg_tables
              WHERE  tablename  = 'CrashSeverity') THEN
      RAISE NOTICE 'Table CrashSeverity already exists.';
ELSE
    CREATE TABLE CrashSeverity (
        ID INTEGER PRIMARY KEY,
        Name VARCHAR(128) UNIQUE
    );

    INSERT INTO CrashSeverity (ID, Name)
    VALUES
    (1, 'Fatal'),
    (2, 'Hospitalisation'),
    (3, 'Medical treatment'),
    (4, 'Minor injury'),
    (5, 'Property damage only');
END IF;

IF EXISTS (SELECT FROM pg_catalog.pg_tables
              WHERE  tablename  = 'CrashNature') THEN
      RAISE NOTICE 'Table CrashNature already exists.';
ELSE
    CREATE TABLE CrashNature (
        ID INTEGER PRIMARY KEY,
        Name VARCHAR(128) UNIQUE
    );

    INSERT INTO CrashNature (ID, Name)
    VALUES
    (1, 'Angle'),
    (2, 'Collision - miscellaneous'),
    (3, 'Fall from vehicle'),
    (4, 'Head-on'),
    (5, 'Hit animal'),
    (6, 'Hit object'),
    (7, 'Hit parked vehicle'),
    (8, 'Hit pedestrian'),
    (9, 'Non-collision - miscellaneous'),
    (10, 'Other'),
    (11, 'Overturned'),
    (12, 'Read-end'),
    (13, 'Sideswipe'),
    (14, 'Struck by external load'),
    (15, 'Struck by internal load');
END IF;

IF EXISTS (SELECT FROM pg_catalog.pg_tables
              WHERE  tablename  = 'CrashType') THEN
      RAISE NOTICE 'Table CrashType already exists.';
ELSE
    CREATE TABLE CrashType (
        ID INTEGER PRIMARY KEY,
        Name VARCHAR(128) UNIQUE
    );

    INSERT INTO CrashType (ID, Name)
    VALUES
    (1, 'Hit pedestrian'),
    (2, 'Multi-Vehicle'),
    (3, 'Other'),
    (4, 'Single Vehicle');
END IF;

IF EXISTS (SELECT FROM pg_catalog.pg_tables
              WHERE  tablename  = 'RoadwayFeature') THEN
      RAISE NOTICE 'Table RoadwayFeature already exists.';
ELSE
    CREATE TABLE RoadwayFeature (
        ID INTEGER PRIMARY KEY,
        Name VARCHAR(128) UNIQUE
    );

    INSERT INTO RoadwayFeature (ID, Name)
    VALUES
    (1, 'No Roadway Feature'),
    (2, 'Intersection - Cross'),
    (3, 'Intersection - T-Junction'),
    (4, 'Intersection - Roundabout'),
    (5, 'Bridge/Causeway'),
    (6, 'Median Opening'),
    (7, 'Intersection - Y-Junction'),
    (8, 'Intersection - Interchange'),
    (9, 'Merge Lane'),
    (10, 'Intersection - Multiple Road'),
    (11, 'Bikeway'),
    (12, 'Other'),
    (13, 'Intersection - 5+ way'),
    (14, 'Railway Crossing'),
    (15, 'Forestry/National Park Road'),
    (16, 'Miscellaneous');
END IF;

IF EXISTS (SELECT FROM pg_catalog.pg_tables
              WHERE  tablename  = 'TrafficControl') THEN
      RAISE NOTICE 'Table TrafficControl already exists.';
ELSE
    CREATE TABLE TrafficControl (
        ID INTEGER PRIMARY KEY,
        Name VARCHAR(128) UNIQUE
    );

    INSERT INTO TrafficControl (ID, Name)
    VALUES
    (1, 'No traffic control'),
    (2, 'Operating traffic lights'),
    (3, 'Give way sign'),
    (4, 'Stop sign'),
    (5, 'Police'),
    (6, 'Flashing amber lights'),
    (7, 'Pedestrian crossing sign'),
    (8, 'Road/Rail worker'),
    (9, 'School crossing - flags'),
    (10, 'Railway - lights and boom gate'),
    (11, 'Pedestrian operated lights'),
    (12, 'LATM device'),
    (13, 'Miscellaneous'),
    (14, 'Railway crossing sign'),
    (15, 'Supervised school crossing'),
    (16, 'Railway - lights only'),
    (17, 'Other');
END IF;

IF EXISTS (SELECT FROM pg_catalog.pg_tables
              WHERE  tablename  = 'AtmosphericCondition') THEN
      RAISE NOTICE 'Table AtmosphericCondition already exists.';
ELSE
    CREATE TABLE AtmosphericCondition (
        ID INTEGER PRIMARY KEY,
        Name VARCHAR(128) UNIQUE
    );

    INSERT INTO AtmosphericCondition (ID, Name)
    VALUES
    (1, 'Clear'),
    (2, 'Raining'),
    (3, 'Fog'),
    (4, 'Smoke/Dust');
END IF;