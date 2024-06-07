# README

This code can be used to generate a geoviews plot of a satellite given its NORAD Catalog Number if it exists on 

The track starts at a given time and extends 1.5 hours from there.
![image](https://github.com/rocheseb/satloc/assets/22297924/1deb0968-9e4b-46dd-a5f2-677a711c2b5c)

## Install

`git clone https://github.com/rocheseb/satloc`

`pip install -e satloc`

## Usage

`satloc -h`

By default the track will start at the current time.

`satloc 25544 --title "ISS orbit track"`

You can also have it start at a given UTC time in YYYYMMDDTHHMMSS format with the **--date** argument.

The track will be more imprecise the further in time from the last time the satellite TLE was updated on the celestrak website.


## Contact

sroche@g.harvard.edu
