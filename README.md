# Figures
Make figures like on mcr.unibas.ch/dolueg2 in terms of layout and filenaming so they may automatically be found by the PHP script in the homepage folder

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
 
 # Needed adjustments
 We use a "getdata" function that returns the timeseries of a/several database code/s and the related information about the series, such as (device, measurement height, location ..). As it is likely that your data is in another form than ours, the relevant function is available on requests but keep in mind it is based on a specific organisation of meta and data tables on a SQL-Server we use that requires setup of the server, the dataflow and quality checks.
 
 # Optional adjustments
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
### Simple case

### Specific ticks/axes

### More complex case
Create an overview of temperatures in the area/surroundings to present prominently below a measurement values table
![Temperature Overview](https://mcr.unibas.ch/dolueg2/projects/basel/plots/0day/basel_temp_overview.svg "Temperature Overview")

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
![Scatter plot of temperature between rural and urban station with urban station on x axis](https://mcr.unibas.ch/dolueg2/projects/basel/plots/3year/basel_0_a_atemp_scatter.svg "Temperature Scatter Rural vs Urban")

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
![Temperature difference between two stations over the course of a day versus day of year](https://mcr.unibas.ch/dolueg2/projects/basel/plots/0day/basel_1_a_atemp_profile.svg "Temperature Difference Urban-Rural")

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
![Temperature profile at Basel Klingelbergstrasse](https://mcr.unibas.ch/dolueg2/projects/basel/plots/3year/basel_0_a_atemp_diff_iso.svg "Temperature profile at Basel Klingelbergstrasse")

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
![Backscatter at Basel Klingelbergstrasse](https://mcr.unibas.ch/dolueg2/projects/basel/plots/0day/basel_1_g_backscatter_1medium.svg "Ceilometer measurements of the boundary layer/lower atmosphere in Basel")

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

## stationmap (draw markers for stations of a network on a static webmap of google or openstreetmap)

                                                  
