# Figures
Make figures like on mcr.unibas.ch/dolueg2 in terms of layout and filenaming so they may automatically be found by the PHP script employed by the webserver.
See [live dolueg for examples](https://mcr.unibas.ch/dolueg2/index.php?project=basel) or check the [slimmed down testversion of the webserver without many figures](https://mcr.unibas.ch/doluegtest/index.php?project=template&var=0).

Webserver repository [can be found here](https://github.com/spirrobe/dolueg2page)

**The section of examples here is rather extensive and meant to illustrate the available options you can also see in the code**

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

![Temperatures of a street canyon with tropicalnights marked](https://raw.githubusercontent.com/spirrobe/dolueg2figures/master/examples/basel_2_a_atemp.svg "Temperatures of a street canyon with tropicalnights marked")

```python
tempcol = ['#ffaa00', '#ff5a00', '#ff0000',
           '#cc0000', '#990000', '#660000',
           '#330000', '#000000', '#ff4d4d',
           '#ff8080']
           
plot(['BKLSDTA1', 'BKLSDTA2'],   
     t0='*-7', 
     t1='*', 
     dt='30Min',  
     outfile='basel_2_a_atemp.svg',
     colors=tempcol,  
     minvalue=-999,                          
     figopt={'marktropicalnight': True, }
     )                                                                                                                    
```

Select the codes (street level temperature in this case) and use data a week back ('*-7').
Too many colors can be passed in and not-needed colors are ignored.
Set the figopt 'marktropicalnight' to true, resulting in a small rectrangle drawn at 20°C during nighttime only.
Related figopt entries are: 
- 'tropicalnightscolor': '#111111'
- 'tropicalnightsedgecolor': '#000000'
- 'tropicalnightsedgewidth': 1
where these define in order
- the color of the fill of the rectangle
- the color of the edge of the rectangle
- the height in percent of the rectangle relative to the total range
            
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

#### Adjusting the values gotten from the database for scaling, e.g. different units
![Temperature Turbulent fluxes](https://raw.githubusercontent.com/spirrobe/dolueg2figures/master/examples/basel_1_e_energyflux_turbulent.svg "Temperature Turbulent fluxes")

```python
    plot(['BKLINRA1', 'BKLIWHCA', 'BKLIWTCA'], 
    t0='*-30',
    t1='*',
    dt='1H',
    outfile='basel_1_e_energyflux_turbulent.svg',
    colors=['#000000', '#00CFFC', '#FF0000'],
    multiplier=[1, 44.1, 1200],
    figopt={'yrange': [-300, 600], 
            'ylabel': 'W m$^{-2}$'
            },  
    )   
```
Choose codes and time as in other examples with specific colors for net radiation, latent and sensible heat flux which are both as covariances in the database.
Multiply these in order by 1, 44.1, 1200 to scale them to Watt per square meter and set the label accordingly. 

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
     indexcode='BKLIDTA9',
     figopt={'ytitle': 'Temperature Difference: Basel Klingelbergstrasse - Basel Lange Erlen'
             },
)
```
Substract the two codes (BKLIDTA9, urban; BLERDTA1, rural) for the time range (t0 is one year ago, now *-365 days, t1 is now *).
Keep the temperature range that is shown fixed from -4 to 4 and choose a specific type for the title that is used in the graph
The indexcode denotes which code should be used for the xaxis; if not explicitly set, defaults to the first one
        
## Profile (several heights versus time) time series example
![Temperature difference between two stations over the course of a day versus day of year](https://raw.githubusercontent.com/spirrobe/dolueg2figures/master/examples/basel_1_a_atemp_profile.svg "Temperature Difference Urban-Rural")

```python
plot(['BKLIDTA'+i for i in ['7', '8', '9']],
     t0=t0, t1=t1, dt='1H',
     outfile=projectprefix+ '_1_a_atemp_profile.svg',  
     plottype='profile',   
     figopt={'profileconnect': True},   
     colors=tempcol,        
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


## Iso (measurements run over the day versus day of year) time series examples

Create an overview of temperatures in the area/surroundings to present prominently below a measurement values table
![Temperature profile at Basel Klingelbergstrasse](https://raw.githubusercontent.com/spirrobe/dolueg2figures/master/examples/basel_0_a_atemp_diff_iso.svg "Temperature profile at Basel Klingelbergstrasse")

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
[Windroses in the Basel area of last week](https://mcr.unibas.ch/dolueg2/projects/basel/plots/0day/basel_0i_mapwind.svg "Windroses in the Basel area of last week")
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
The above cannot be shown inline as the created SVG is too large for Github.
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


## other keywords
- for xy-plots the indexcode can be explicitly set or defaults to the first one of the codelist otherwise
- which values to remove after the db output can be done via
  - removing values below a threshold, e.g. minvalue=-9999
  - removing values above  a threshold, e.g. maxvalue=1000
- set the zlog directly instead of as figure options via zlog=True
- choose values to multiply (or divide) the database output with via mutliplier=[values]
- choose values to offset (+ or -) the database output with via offset=[values]
- **kwargs can be used to be passed onto the called plotroutine, refer to their documentation for more information 
  

## default lineopt options
These lineoptions are passed in via either a dict with an entry directly for each code
or a dict containing just the entries in which case the entry is extended to all codes
- use the following color code for this series 'color': defaultcolors[0] (defaultcolormap can be read by defaultct())
- the linestyle to use 'ls': '-'
- the linewidth to use 'lw': 1.5
- the marker (defaults to no markers) to use: 'marker': None 
- the size of the marker defaults to if used: 'markersize': 5
- the fill color of the marker: 'markerfacecolor': defaultcolors[0]
- the border of the marker: 'markeredgecolor': '#000000'
- the alpha level of the line/marker to use: 'alpha': 0.85,   
- what to enter into the legend if not the autoselection is used: 'label': ''

## default figure options
figopt is a dict containing the following keys

##### general figure options
- how large should the figure (in inches as matplotlib uses inches for it): 'figsize': [24/2, 9.6/2]
- the resolution in dots per inch, i.e. how large the endresult will be, mainly relevant for rasterparts, higher number means larger filesize as well: 'figdpi': 300 

##### y-axis options
- the range for the y-axis, with -9999 denoting autosearch: 'yrange': [-9999, -9999]
- how many ticks should there be for the secondary axis, None lets matplotlib choose by itself: 'yticks': None
- overwrite the label of the axis if needed, defaults to potentially matching meta data (name of series, unit) of the series (linear), height [m] (profile/mesh) or time of day (iso): 'ylabel': ''

##### second (right) y-axis options
- choose which codes to draw on the right: 'secondaryaxis': []
- how to label the second axis: 'secondaryylabel': ''
- which range to use for the axis, -9999 defaults to auto: 'secondaryaxisyrange': [-9999, -9999]
- how many ticks to use for the second axis: 'secondaryaxisticks': None
- how to label the ticks for this secondary axis: 'secondaryaxislabels': None
- take the same axis scaling as on the left axis (only for linear plots) which seems weird but is an option: 'secondaryyaxissamescale': False

##### x-axis options
- the range for the y-axis, with -9999 denoting autosearch: 'xrange': [-9999, -9999]
- how many ticks should there be for the secondary axis, None lets matplotlib choose by itself: 'xticks': None
- overwrite the label of the axis if needed, defaults to the time, including timezone in some manner: 'xlabel': ''

##### z-axis options, i.e. third dimension of data for iso/mesh plots
- if a mesh/iso plot, use this to set the datarange, -9999 means autodetection:  'zrange': [-9999, -9999]
- how many ticks should there be for the secondary axis, None lets matplotlib choose by itself: 'zticks': None
- overwrite the label of the corresponding colorbar (mesh/iso) if needed, defaults to the the name and unit of the dataseries: 'zlabel': ''
##### accessories
- choose to draw a slightly thicker line at zero, defaults to yes: 'zeroline': True
- set the color of the line: 'zerolinecolor': '#000000'
- set the width of the line: 'zerolinewidth': 1

- draw a grid, defaults to yes: 'grid': True
- the linestyle of the grids vertical lines: 'gridxlinestyle': '-'
- the linestyle of the grids horizontal lines: 'gridylinestyle': ':'
- the linewidth of the grid: 'gridlinewidth': 0.25
- the color of the grid: 'gridlinecolor': 'k'

- draw a shaded for the night: 'sunlines': True
- the color to draw the shade in: 'sunlinescolor': '#bcbcbc'
- the color to use for the sunline in the isoplots: 'sunlinesisocolor': '#000000'
- the width of the line in the isoplots: 'sunlineswidth': 1.5
- which textcolor for the isoplot sunline: 'sunlinestextcolor': '#333333'

- whether to draw a rectangle for tropicalnights: 'marktropicalnight': False                                                           
- the height in relative units to the yrange, defaults to 1%: 'tropicalnightsedgewidth': 1
- which color to use for filling the tropical nights, is not visibile if 'tropicalnightsedgewidth' is too small: 'tropicalnightscolor': '#111111'
- which color for the edge of the rectangle to use: 'tropicalnightsedgecolor': '#000000'

#### changes to drawing style of codes
- which codes to draw as bar instead of as lines: 'barcodes': [ ]
- the width in dt-relative units, e.g. if dt = 30 minutes a 5/6 here would be 25 minutes: 'bartotalwidth': 0.85

- which codes to cumulatively sum: 'cumulativecodes': [ ]

- draw the axis in the same color as used by the first code drawn on it, e.g. blue:  'suppressaxiscolor': True
- draw a legend with the information in the graph: 'suppresslegend': False

- overwrite the legendtitle, defaults to information about aggregation: 'legtitle': None
- set the legendlabels by yourself to overwrite the default behaviour to get meta information: 'leglabel': [ ]
- set the fontsize: 'legfontsize': 10
- create a box for the legend: 'legendbox': True
- alpha for the legend: 'legalpha': 0.5
- use an overarching figure title: 'figtitle': None
- general fontsize to use for text: 'fontsize': 10

##### the following are only applied to mesh/iso plots
- whether to scale the data logarithmically, values below or equal 0 are masked: 'zlog': False,                                                                                                                          
##### only applied to linear plots
- whether to scale the y-axis logarithmically: 'ylog': False
- whether to scale the second axis logarithmically: 'secondaryylog': False

##### only applied to linear bar plots
- draw the edge of the bar as well: 'baredge': False,                                                                                   

##### only relevant for plots with a map background
- how transparent the background, a high value makes the plot disappear somewhat: 'mapalpha': 0.85

##### only relevant for stationmap data
- the alpha value for the stationmarkers when creating a stationmap: 'stationalpha': 0.5
                                                                                                                                                                                                                                        
