# Figures
Make figures like on mcr.unibas.ch/dolueg2 in terms of layout and filenaming so they may automatically be found by the PHP script employed by the webserver

# Types of figures
Available types are:
- 'timeseries', 'linear' (default)
- 'xy'
- 'profile', 'profiles'
- 'iso', 'ispohypses', 'isolines'
- 'mesh'
- 'wind', 'windrose', 'windmap'
- 'stationnetwork', 'stationnetworks', 'station', 'stationmap'

You can find examples in the related, published BAMS article and at the above URL
 
# Installation
For proper functionality a few adjustments have to be made, dependent on your use-case:
- You need to have a getdata function that returns data and metadata for the timeseries. Since our database still has columnheaders in german, some adjustments in the plot.py file might be in order for what you want to have displayed. 
- Automatic creation in our case is done via creating a crontab that runs every hour, and the dolueg2.py defines which plots of a project and which timespans (e.g. hourly, weekly, monthly, yearly) are created at that time, depending on the time of day the dolueg2.py is run. Adjust as needed.
- dolueg2.py contains several functions which need to be adjusted:
  - def move2webserver() needs the mounted webserver (or rewritten in case you use an FTP or want to use wput)
  - def example() (an example project) contains a setup similar to ours, i.e. a loop over the timespans that are defined in definetimes() as day/week/month/year, and holds the plots. We define the directory of the project in the call and expect the timespans to be passed in as we check those against the known ones in definetimes(). This slightly convoluted approach allows proper definition of a month and a year back since we do not just go 30 days back but choose the same date of the previous month/year when possible.
  - at the end of a project we call move2webserver with the passed in variables which results in the proper order for the webserver.
  - all these can be adjusted as needed for your setup and serve as an initial sketch for you
- If you wish for stationmap/windmaps with a google maps background you will need an API key. Take care that this API key is kept private. Alternatively and by default the statis maps use openstreetmap background so it works out of the box. The API key needs to be used in map/mapurl.py in the function definiton.
 
 ## Needed adjustments/scripts that you need
 We use a "getdata" function that returns the timeseries of a/several database code/s and the related information about the series, such as (device, measurement height, location ..). As it is likely that your data is in another form than ours, the relevant function is available on requests but keep in mind it is based on a specific organisation of meta and data tables on a SQL-Server we use that requires setup of the server, the dataflow and quality checks.
 
 ## Optional adjustments
 The list given in script/dolueg2 is meant to contain commands to create the figures as needed with the optional adjustments. 
 The main choice for new figures/alterations is the identifier that follows a "_station_variable_" scheme, e.g.:
 1 basel_0_a_ -> Will be shown in Basel at the "overview" (no station selected) and with "Temperature and relative humidity"
 2 basel_1_2_3_b_c_ -> Shown in stations 1, 2 and 3 as well as at "Precipitation and evaporation" and "Wind and air pressure"
 3 basel_a_ -> Shown only for temperature
 
 This allows one figure to be placed specifically or as broadly as needed without creating the same figure several times
 
 Further adjustments that may be use:
 - Create a certain plot only with a certain data range (e.g. isopleths only for month/year data range) -> Adjust in the script
 - Specific name for a figure (like overview) -> Figure created and exists, but never shown until directly link -> Useful for testing/overview/specific information
 
 
 # Dependencies
 We tried to keep dependencies as limited as possible, but the following are required:
 - numpy
 - pandas
 - matplotlib
 - requests (for webmaps)
 - pysolar (for sunup/down in background or on top)
 - scipy (only one distance function is needed that can be replaced by your own distance function)
 - socket, to disentangle development and deployment

# Examples
## Linear time series examples
#### Simple case
![Relative humidity at several locations](https://raw.githubusercontent.com/spirrobe/dolueg2figures/master/examples/basel_0_a_relhum.svg "Relative humidity at several locations")
```python
humcol = ['#0000ff', '#00A6ff', '#00ffff',
          '#00B2B2', '#006666', '#003333', '#99ccff']
          
plot(['BLERRHA1', 'BKLIRHA9', 'BKLIRHA7', 'BLEORHA1', 'BLERRHA8', 'BKLSRHA2', 'BKLBRHA2'],
     t0=datetime.datetime.now()-datetime.timedelta(days=7),
     t1=datetime.datetime.now(),
     dt='30Min',
     outfile='basel_0_a_relhum.svg',
     colors=humcol,
     minvalue=-999,
     figopt={'yrange': [0, 100]},
             )   
```
Select which codes (all relative humidity in this case) and the t0, t1 (here with the datetime module from the stdlib) and the dt as resolution of 30 minutes. Define the outputfile (change ending to .png if you want PNG files instead as it is passed directly to matplotlib).
Create some blue shades/colors for use and explicitly set the yrange to avoid the autoscaling to only the existing range (sensible here for relative humidity).

#### Bars instead of markers/lines
![Rain as bars instead of line](https://raw.githubusercontent.com/spirrobe/dolueg2figures/master/examples/basel_0_b_precipitation.svg "Rain as bars instead of line")
```python

plot(['BKLIPCT2', 'BLEOPCT1', 'BBINPCT1', 'BKLSPCT2', 'BKLBPCT2', ],
     t0=datetime.datetime.now()-datetime.timedelta(days=7),
     t1='*',
     dt='1H',
     outfile='basel_0_b_precipitation.svg', 
     figopt={'yrange': [0, -9999],   
             'barcodes': ['BKLIPCT2', 'BLEOPCT1', 'BBINPCT1', 'BKLSPCT2', 'BKLBPCT2'],
            },
     colors=humcol,
     ) 
```            

Select which codes (in this case precipitation, PCT) to choose and again select a timerange where '*' is interpreted as now with our getdata function. Set dt to be 1H instead and define an outfile where to save. 
Set the ylim/yrange lower limit to 0, and the upper to autofind with the special code -9999. This makes the function find a rounded maximum based on the range found in the data.
Define which ones of the codes should be plotted as bars instead of lines. These can be all or just some codes (here all are set to be plotted as bar). Use the same colors as defined above

#### Cumulative Lines
![Cumulative rain at different locations](https://raw.githubusercontent.com/spirrobe/dolueg2figures/master/examples/basel_0_b_precipitation_cumulative.svg "Cumulative rain at different locations")

```python

plot(['BKLIPCT2', 'BLEOPCT1', 'BBINPCT1', 'BBINPCT4', 'BKLSPCT2', 'BKLBPCT2'],     
     t0='*-14',
     t1=datetime.datetime.now(),
     outfile='basel_0_b_precipitation_cumulative.svg', 
     figopt={'cumulativecodes': ['BKLIPCT2', 'BLEOPCT1', 'BBINPCT1', 'BBINPCT4', 'BKLSPCT2', 'BKLBPCT2'], 
             'yrange': [0, -9999],
            },
     colors=humcol,
     )  
     
``` 
Select the same precipiation codes as in the example above. Use mixed t0 and t1 format again, for 14 days this time.
Choose cumulativecodes in this example for all codes and set the range to 0 and autofind with [0, -9999].
Take the same colors as before.

#### Specific ticks/axes 
Ticks ofthe right axis changed from numbers to winddirection (also possible for first axis)
![Wind speed, gusts and direction](https://raw.githubusercontent.com/spirrobe/dolueg2figures/master/examples/basel_4_c_wind.svg "Wind speed, gusts and direction")
```python

for windno, windcodes in enumerate([['BKLIWVA6', 'BKLIWVX6', 'BKLIWDA1'],
                                    ['BKLSWVA2', 'BKLSWVX2', 'BKLSWDA2'],
                                    ['BKLBWVA2', 'BKLBWVX2', 'BKLBWDA2'],
                                    ['BAWVA1', 'BAWVX1', 'BAWDA1'],
                                    ['BLEOWVA1', 'BLEOWVX1', 'BLEOWDA1'],
                                    [],  # empty for binningen
                                    ['BLERWVA7', 'BLERWVX7', 'BLERWDA2'],
                                    ]):
    if windcodes:
        pass
    else:
        continue

    windcodes = ['BAWVA1', 'BAWVX1', 'BAWDA1'] 
    plot(windcodes,
         t0='*', t1='*-7', dt='30Min',
         outfile='basel_'+str(windno+1)+'_c_wind.svg',
         colors=['#9900cc', '#9900cc', '#ff0000'],
         figopt={'yrange': [0, -9999],
                 'yticks': 5,
                 'secondaryaxis': windcodes[2],
                 'secondaryaxisyrange': [0, 360],
                 'secondaryaxisticks': 5,
                 'secondaryaxislabels': ['N','E','S','W','N'],
                 },
         lineopt={windcodes[1]: {'ls':':'},
                  windcodes[2]: {'marker': 'o', 'ls': 'None'},
                 },
         )

```
The picture example shows one of the created plots (Aeschenplatz).
Create the same plot for several stations as denoted by the list of lists with codes. Take note that overview plots have a 0 in their filename for our dolueg2 setup and we thus start with station 1, i.e. we add 1 to the windno to account for the overview being 0.
This allows for windcodes to be reused directly (see figopt/lineopt) in the call. We on purpose set t0 and t1 the wrong way around, i.e. t0 is now, t1 is in the past as our getdata function automatically adjusts for this error.
outfile contains the windno as the loopcounter where we add +1 to the windno.
For figoptions set the left axis to autofind with [0, -9999], and to have 5 ticks instead of the default to match up with the right axis. Choose which codes go on the secondary axis with the secondaryaxis entry, set the yrange to 0 to 360° for our wind direction and also set the ticks to be 5 (instead of matplotlib default). Choose aliases/yticklabels for the second axis to make it more user-friendly.

Set the linestyle windcodes[1] (which is the wind gusts in this case) to dotted with an ls of ':' and choose no linestyle for the windcodes[2] (winddirection) and only markers. The latter makes wind direction plots more appealing in our opinion. Change as needed/wanted.

#### More complex cases
Create an overview of temperatures in the area/surroundings to present prominently below a measurement values table
![Temperature Overview](https://raw.githubusercontent.com/spirrobe/dolueg2figures/master/examples/basel_temp_overview.svg "Temperature Overview")

```python
plot(['BKLIDTA1', 'BLERDTA7', 'B2091WT0'],
     t0='*-1', t1=t'*', dt='30Min',
     outfile='basel_temp_overview.svg',
     lineopt={'BKLIDTA1': {'color': '#b30000', 'marker': 'o'},
              'BLERDTA7': {'color': '#008000', 'marker': 'o'},
              'B2091WT0': {'color': '#3399ff', 'marker': 'o'},
              },
     figopt={'secondaryaxis': ['B2091WT0'],
             'marktropicalnights': True,
             'suppressaxiscolor': False,
             },
     )
```
Takes the three codes (BKLIDTA1, BLERDTA7, B2091WT0) for the time from t0 to t1 (* and *-1 are passed on to the getdata function and are today, and today - 1 day respectively) in a temporal resolution of 30 Minutes instead of the native one of 10 Minutes (from the database). 
Lineoptions refer to the specific codes to use markers instead of just lines and specific colors. 
figoptions refer to the whole figure setup, for example which of the codes should be plotted on the right (in this case that is the water temperature), to mark tropical nights (nocturnal temperature doesnt fall below 20°C) and to not suppress the secondary axis color (that is, if the codes on the secondary axis all use the same color, that color is used to draw ticks and the ticklabels, but not the axistitle)

## xy ( scatter-like plot, replace time on x-axis with another variable) 

Create an overview of temperatures in the area/surroundings to present prominently below a measurement values table
![Scatter plot of temperature between rural and urban station with urban station on x axis](https://raw.githubusercontent.com/spirrobe/dolueg2figures/master/examples/basel_0_a_atemp_scatter.svg "Temperature Scatter Rural vs Urban")

```python
plot(['BKLIDTA9', 'BLERDTA1'],
     t0='*-7', t1='*',
     outfile='basel_0_a_atemp_scatter.svg',
     figopt={'ytitle': 'Temperature Difference: Basel Klingelbergstrasse - Basel Lange Erlen'
             },
)
```
Substract the two codes (BKLIDTA9, urban; BLERDTA1, rural) for the time range (t0 is one year ago, now *-365 days, t1 is now *).
Keep the temperature range that is shown fixed from -4 to 4 and choose a specific type for the title that is used in the graph
        
## Profile (several heights versus time) time series example

Create an overview of temperatures in the area/surroundings to present prominently below a measurement values table
![Temperature difference between two stations over the course of a day versus day of year](https://raw.githubusercontent.com/spirrobe/dolueg2figures/master/examples/basel_1_a_atemp_profile.svg "Temperature Difference Urban-Rural")

```python
plot(['BKLIDTA9-BLERDTA1'],
     t0='*-365', t1='*',
     outfile='basel_0_a_atemp_diff_iso.svg',
     figopt={'zrange': [-4, 4],
             'ytitle': 'Temperature Difference: Basel Klingelbergstrasse - Basel Lange Erlen'
             },
     plottype='iso',    
)
```
Substract the two codes (BKLIDTA9, urban; BLERDTA1, rural) for the time range (t0 is one year ago, now *-365 days, t1 is now *).
Keep the temperature range that is shown fixed from -4 to 4 and choose a specific type for the title that is used in the graph
        
## Iso (measurements run over the day versus day of year) time series examples

Create an overview of temperatures in the area/surroundings to present prominently below a measurement values table
![Temperature profile at Basel Klingelbergstrasse](https://raw.githubusercontent.com/spirrobe/dolueg2figures/master/examples/basel_0_a_atemp_diff_iso.svg "Temperature profile at Basel Klingelbergstrasse")

```python
plot(['BKLIDTA'+i for i in ['7', '8', '9']],
     t0=t0, t1=t1, dt='1H',
     outfile='basel_1_a_atemp_profile.svg',
     plottype='profile',
     figopt={'profileconnect': True}, 
     colors=['#3399ff', 'red', '#aa33ff'],  
     title='Basel Klingelbergstrasse Temperature Profile',
     # account for height difference of measurements
     offset=[0.0392, 0.0882, 0.1372],
     minvalue=-999,
     lineopt={c: {'lw': 2, 'marker': 'o'}
              for c in ['BKLIDTA'+i for i in ['7', '8', '9']]}
     )                                                                                                                  
```
Choose a timestep of 1 hour (1H) to get more spacing between profile lines 
Select it to be a profile plot
Figopt denote that the single points of measurements should be connected via "profileconnect"
Colors are can be HTML code for matplotlib or any known matplotlib colors (if no colors are passed, a default colormap is used, see defaultct())
offset for each measurement height as the temperature in the database are not geopotential height
minvalue serves no longer a real purpose as database got cleaned, kept for backward compatibility 
lineopt denote a larger linewidth for the profileconnection, and which marker to use
                                                                                                                                      

## Mesh (measurements at several heights versus time)

Create an overview of temperatures in the area/surroundings to present prominently below a measurement values table
![Backscatter at Basel Klingelbergstrasse](https://raw.githubusercontent.com/spirrobe/dolueg2figures/master/examples/basel_1_g_backscatter_1medium.svg "Ceilometer measurements of the boundary layer/lower atmosphere in Basel")

```python
bsheight = 1000 # how far up as the code corresponds to the measurement height
bsoverlaprange = 50 # the overlap range where the outgoing laser influences measurement
bscodes = ['bklibs' + str(i).zfill(4)                                                                                              for i            in range(bsoverlaprange//5, bsheight//5+1)] 

plot(bscodes,
     t0='*', t1='*-7', dt='15Min',
     plottype='mesh',
     outfile='basel_1_g_backscatter_1_low.svg',
     minvalue=15,
     figopt={'zlog':True,
             'zrange': [1, 3],
             'yrange': [0, bsheight]},
     cmap='jet',
     how={i: 'max' for i in bscodes}
     )                                                                                                                   
```
First create a list of backscatter codes up to a certain height for the last 7 days with a temporal resolution of 15 minutes.
Aggregate according to the maximum value in that time interval instead of mean (default of backscatter codes in our database).
Keep only values above 15 (sensible to remove some noise here)
Make the display logarithmic with zlog as backscatter spans several order of magnitudes
Choose the range, which has a rather low maximum here to highlight the boundary layer height
Despite its issues, use the jet colormap with cmap='jet'
Set the plottype to 'mesh'
      
## windmap (draw windrose at locations of stations on a static webmap of google or openstreetmap)
![Windroses in the Basel area of last week](https://raw.githubusercontent.com/spirrobe/dolueg2figures/master/examples/basel_0i_mapwind.svg "Windroses in the Basel area of last week")
```python
plot(['BKLIWDA1', 'BKLIWVA6', 'BLERWDA2', 'BLERWVA7'], 
     t0='*-7',
     outfile='basel_0i_mapwind.svg',
     minvalue=-999,        
     figopt={'yrange': [0, 360]},   
     plottype='wind',
     mapfullscreen=True,
     #cmap='jet',
)    
```
Choose which windcodes should be used in order of wind direction and wind speed (WDA, then WVA for us). The two stations here are Basel Klingelberg and Basel Lange Erle, that is urban and rural.
Set t0 to '*-7' for data of the last week, t1 defaults to now (when the function is run). Timespan of data is indicated in the map.
Do not use a dt as we want statistics of the whole range instead of aggregated.
Figopt can be set but will not be used anywhere in this kind of plottype='wind'
Remove the coordinates around the map, i.e. mape the map fullscreen=True, which gives a better impression, but may remove possibilites for orientation.
If needed, another than the default colormap for windroses can be used by passing the cmap keyword that is outcommented. Any matplotlib named colormap or a self-generated cmap can be used.


![Urbanfluxes single station windrose data](https://raw.githubusercontent.com/spirrobe/dolueg2figures/master/examples/urbanfluxes_0i_9i_mapwind.svg "Urbanfluxes single station windrose data")
```python
plot(['UFBCWWD', 'UFBCWWV'],
     t0=t0, t1=t1,         
     outfile='urbanfluxes_0i_9i_mapwind.svg', 
     plottype='wind',   
     )                
```

The simplest way to create the windmap with just winddirection code, the timerange and change of the plottype.

## stationmap (draw markers for stations of a network on a static webmap of google or openstreetmap)
![Stationmap of URBANFLUXES](https://raw.githubusercontent.com/spirrobe/dolueg2figures/master/examples/urbanfluxes_0i_stationmap.svg "Stationmap of URBANFLUXES")
```python

plot(['UFB1WWD', 'UFB2BVA', 'UFB3WWD', 'UFB4BVA', 'UFB5WWD',
      'UFB6BVA', 'UFB7WWD', 'UFB8BVA', 'UFBABVA'],
      t0='*-1',
      t1='*',
      outfile=projectprefix+'_0i_stationmap.svg',
      plottype='stationmap',
)
```

Instead of a windmap, a similar type is the stationmap, which creates a map with markers, where nearby markers are combined. Each marker is numbered according to the passed in order of the list. As there are no real data needed, t0 and t1 can be set to a minimal timespan and any code for a station can be used as only the metadata of latitude and longitude are used.

                                                                                    


                                                  
