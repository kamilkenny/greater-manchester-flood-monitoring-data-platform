# Environment Agency Source Profile

## Initial monitoring area

The initial extraction uses a 35 km radius centred approximately on Manchester city centre.

This is an operational monitoring area for the prototype and should not be interpreted as the exact administrative boundary of Greater Manchester.

## Initial profile

The first source profile returned:

* 259 monitoring stations
* 0 current flood warnings or alerts
* 98 stations without a populated river name
* 101 stations without a populated town

Frequently represented rivers included the River Calder, River Irwell, River Mersey, River Tame, River Darwen, River Roch and River Bollin.

## Station fields observed

stationReference, label, riverName, town, catchmentName, latitude, longitude, status, measures and stage scale metadata were among the available station attributes.

## Reading fields observed

The latest station reading sample contained:

* measure
* dateTime
* date
* value

## Engineering implications

The pipeline must tolerate optional station metadata, preserve the raw source, reject duplicate business keys, support zero active flood warnings and separate the broad monitoring radius from any future exact Greater Manchester administrative-boundary filter.
