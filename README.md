# README

This code can be used to generate a geoviews plot of a satellite given its NORAD Catalog Number if it exists on celestrak.org 

The track starts at a given time (**--date**, defaults to current time) and extends for **--forecast-hours** hours (defaults to 1.5 hours).

Example plot for the ISS generated with `satloc 25544 --title ISS --forecast-hours 3`:
![image](https://github.com/rocheseb/satloc/assets/22297924/72df3935-078e-4027-9adf-e3fd7b74a12c)


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
