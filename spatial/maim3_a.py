from mpl_toolkits.basemap import Basemap, cm, shiftgrid,interp,maskoceans
from netCDF4 import Dataset as NetCDFFile
import numpy as N
import matplotlib.pyplot as plt
import glob
import numpy.ma as ma
from scipy.interpolate import griddata
import matplotlib.colors as colors


iizumi=NetCDFFile('/scratch2/scratchdirs/tslin2/plot/globalcrop/data/iizumi/iizumi.2013JAN29.maize.1982-2006.30min.nc4','r')
#print iizumi
iyield = iizumi.variables['yield50'][18,:,:]
iarea =iizumi.variables['area'][18,:,:]
la=iizumi.variables['lat'][:]
lo=iizumi.variables['lon'][:]
iyield=N.flipud(iyield)
iarea=N.flipud(iarea)

region1=NetCDFFile('/scratch2/scratchdirs/tslin2/plot/globalcrop/data/clm/HistoricalGLM_crop_150901.nc','r')
maitrop = region1.variables['maize_trop'][99,:,:]
maitemp = region1.variables['maize_temp'][99,:,:]
maizeto = maitrop+maitemp

clm=NetCDFFile('/scratch2/scratchdirs/tslin2/plot/globalcrop/data/clm/clm45historical/maizetrop_historical_co2_rf_nofert_0.5x0.5.nc','r')
clmtrop = clm.variables['yield'][96:103,:,:]
clmtropf=N.average(clmtrop,axis=0)

clm1=NetCDFFile('/scratch2/scratchdirs/tslin2/plot/globalcrop/data/clm/clm45historical/maizetemp_historical_co2_rf_nofert_0.5x0.5.nc','r')
clmtemp = clm1.variables['yield'][96:103,:,:]
clmtempf=N.average(clmtemp,axis=0)


#print clmtropf.shape
clmtropf=N.flipud(clmtropf)
clmtempf=N.flipud(clmtempf)


clmtropf= ma.masked_where(maitrop<=0,clmtropf)
clmtempf= ma.masked_where(maitemp<=0,clmtempf)
clmtropf=ma.filled(clmtropf, fill_value=0.)
clmtempf=ma.filled(clmtempf, fill_value=0.)

area=NetCDFFile('/scratch2/scratchdirs/tslin2/plot/globalcrop/data/maizegridarea.nc','r')
gridarea = area.variables['cell_area'][:,:]

nclu=NetCDFFile('/scratch2/scratchdirs/tslin2/plot/globalcrop/data/maize_AreaYieldProduction.nc','r')
ncvar_maize = nclu.variables['maizeData'][:]
latnc = nclu.variables['latitude'][:]
znc = nclu.variables['level'][:]
lonnc = nclu.variables['longitude'][:]
timenc = nclu.variables['time'][:]
#lon,lat = N.meshgrid(lonnc,latnc)
lon,lat = N.meshgrid(lonnc,latnc)

ncvar_maizef= N.zeros((2160, 4320))
ncvar_maizef=ncvar_maize[0,1,:,:]
ncvar_maize1=ncvar_maize[0,4,:,:]
ncvar_mask= N.zeros((2160, 4320))
ncvar_mask=ncvar_maize[0,0,:,:]


ncvar_maizef[N.isnan(ncvar_maizef)] = -9999
ncvar_mask[N.isnan(ncvar_mask)] = -9999
ncvar_maize1[N.isnan(ncvar_maize1)] = -9999

ncvar_maizef = ma.masked_where(ncvar_maizef<=0,ncvar_maizef)
#ncvar_maizef= ma.masked_where(ncvar_mask<0.01,ncvar_maizef)
ncvar_maizef = ma.masked_where(ncvar_maize1<=0,ncvar_maizef)
#ncvar_maizef = ma.masked_where(mask_clm<=0,ncvar_maizef)


yieldf= N.zeros((7, 360, 720))
yieldf2= N.zeros((7, 360, 720))
years = range(1997, 2004)
for i, year in enumerate(years):
    base = NetCDFFile ("/scratch2/scratchdirs/tslin2/isam/model/global/isam_his/cruhis/output/cruhis.bgp-yearly_crop_{0}.nc".format(year), mode='r')
    lona1 = base.variables["lon"][:]
    lata1 = base.variables["lat"][:]
   
    yield1 = base.variables["yield"][0,:,:]
    yieldf[i, :, :] = yield1
    #yield2 = base2.variables["totalyield"][:]
    #yieldf2[i, :, :] = yield2

yielda=N.average(yieldf,axis=0)
#yielda2=N.average(yieldf2,axis=0)

yield_new,lona11 = shiftgrid(180.5,yielda,lona1,start=False)
#yield_new2,lona11 = shiftgrid(180.,yielda2,lona1,start=False)

lon2,lat2 = N.meshgrid(lona11,lata1)
#print lon2.shape
#ncvar_maize2 = interp(ncvar_maizea,lonnc,lat_new,lon,lat,order=1)

#yield_smooth = interp(maize_new, lonnc,lat_new, lons_sub,lats_sub , order=1)
yield_fine = interp(yield_new, lona11,lata1,lon,lat  , order=1)
#yield_fine2 = interp(yield_new2, lona11,lata1,lon,lat  , order=1)

yield_clmtro = interp(clmtropf, lona11,lata1,lon,lat  , order=1)
yield_clmtep = interp(clmtempf, lona11,lata1,lon,lat  , order=1)

mask_clm = interp(maizeto, lona11,lata1,lon,lat  , order=1)

#print maskus_new



fig, ax = plt.subplots(figsize=(8,6))


ax.set_title("M3 Maize Yield gridecll (g/$\mathregular{m^2}$)",fontsize=20)
map = Basemap(projection ='cyl', llcrnrlat=-65, urcrnrlat=90,llcrnrlon=-180, urcrnrlon=180, resolution='c')
map.drawcoastlines()
map.drawcountries()
map.drawmapboundary()



lone,late = N.meshgrid(lonnc,latnc) #Returns coordinate matrices from coordinate vectors
x,y = map(lone,late)
ncvar_maizef=maskoceans(x,y,ncvar_maizef)
ncvar_maizef=ma.filled(ncvar_maizef, fill_value=0.)
ncvar_maizef = ma.masked_where(ncvar_maizef<=0,ncvar_maizef)

#print maskus_new
cs = map.pcolormesh(x,y,ncvar_maizef*ncvar_maize1*1000/gridarea*1000,cmap=plt.cm.YlGn,norm=colors.PowerNorm(gamma=1./2.),vmin=0,vmax=100)
cbar = map.colorbar(cs,location='bottom',size="5%",pad="2%")
cbar.ax.tick_params(labelsize=15) 
plt.axis('off')
plt.savefig('maim3.jpg',dpi=300,bbox_inches='tight')


fig = plt.figure(figsize=(20,15))

ax2 = fig.add_subplot(321)
ax2.set_title("ISAM-NCEP Maize Yield gridcell (g/$\mathregular{m^2}$)",fontsize=20)
map = Basemap(projection ='cyl', llcrnrlat=-65, urcrnrlat=90,llcrnrlon=-180, urcrnrlon=180, resolution='c')
#map = Basemap(projection='robin',lon_0=0,resolution='c')
map.drawcoastlines()
map.drawcountries()
map.drawmapboundary()
yield_fine=maskoceans(x,y,yield_fine)
yield_fine=ma.filled(yield_fine, fill_value=0.)

#yield_fine[N.isnan(yield_fine)] = -9999
yield_fine = ma.masked_where(yield_fine<=0,yield_fine)
yield_fine = ma.masked_where(ncvar_maizef<=0,yield_fine)

cs1 = map.pcolormesh(x,y,yield_fine*ncvar_maize1*1000/gridarea*1000,cmap=plt.cm.YlGn,norm=colors.PowerNorm(gamma=1./2.),vmin=0,vmax=100)
#cs1 = map.pcolormesh(x,y,yield_fine,cmap=plt.cm.jet,vmin=0.0,vmax=15)

cbar = map.colorbar(cs1,location='bottom',size="5%",pad="2%")
cbar.ax.tick_params(labelsize=15) 
plt.axis('off')
#print N.max(yield_fine*ncvar_maize1*1000/gridarea)


ax2 = fig.add_subplot(322)
ax2.set_title("CLM Maize Yield gridcell (g/$\mathregular{m^2}$)",fontsize=20)
map = Basemap(projection ='cyl', llcrnrlat=-65, urcrnrlat=90,llcrnrlon=-180, urcrnrlon=180, resolution='c')
#map = Basemap(projection='robin',lon_0=0,resolution='c')
map.drawcoastlines()
map.drawcountries()
map.drawmapboundary()

yield_clmtf=yield_clmtep+yield_clmtro
yield_clmtf = ma.masked_where(yield_clmtf<=0,yield_clmtf)
yield_clmtf = ma.masked_where(ncvar_maizef<=0,yield_clmtf)

cs1 = map.pcolormesh(x,y,yield_clmtf*ncvar_maize1*1000/gridarea*1000,cmap=plt.cm.YlGn,norm=colors.PowerNorm(gamma=1./2.),vmin=0,vmax=100)
#cs1 = map.pcolormesh(x,y,yield_clm*ncvar_maize1*1000/gridarea,cmap=plt.cm.YlGn,vmin=0.0,vmax=0.35)
#cs1 = map.pcolormesh(x,y,yield_fine,cmap=plt.cm.jet,vmin=0.0,vmax=15)

cbar = map.colorbar(cs1,location='bottom',size="5%",pad="2%")
cbar.ax.tick_params(labelsize=15) 
plt.axis('off')
#print N.max(yield_fine*ncvar_maize1*1000/gridarea)



ax2 = fig.add_subplot(323)
ax2.set_title("ISAM-M3 Maize Yield gridcell (g/$\mathregular{m^2}$)",fontsize=20)
map = Basemap(projection ='cyl', llcrnrlat=-65, urcrnrlat=90,llcrnrlon=-180, urcrnrlon=180, resolution='c')
#map = Basemap(projection='robin',lon_0=0,resolution='c')
map.drawcoastlines()
map.drawcountries()
map.drawmapboundary()
cs1 = map.pcolormesh(x,y,(yield_fine*ncvar_maize1*1000/gridarea*1000)-(ncvar_maizef*ncvar_maize1*1000/gridarea*1000),cmap=plt.cm.bwr,vmin=-100,vmax=100)
#cs1 = map.pcolormesh(x,y,(yield_fine)-(ncvar_maizef),cmap=plt.cm.bwr,vmin=-0.5,vmax=0.5)

cbar = map.colorbar(cs1,location='bottom',size="5%",pad="2%")
cbar.ax.tick_params(labelsize=15) 
plt.axis('off')


ax2 = fig.add_subplot(324)
ax2.set_title("CLM-M3 Maize Yield gridcell (g/$\mathregular{m^2}$)",fontsize=20)
map = Basemap(projection ='cyl', llcrnrlat=-65, urcrnrlat=90,llcrnrlon=-180, urcrnrlon=180, resolution='c')
#map = Basemap(projection='robin',lon_0=0,resolution='c')
map.drawcoastlines()
map.drawcountries()
map.drawmapboundary()
cs1 = map.pcolormesh(x,y,(yield_clmtf*ncvar_maize1*1000/gridarea*1000)-(ncvar_maizef*ncvar_maize1*1000/gridarea*1000),cmap=plt.cm.bwr,vmin=-100,vmax=100)
#cs1 = map.pcolormesh(x,y,(yield_fine)-(ncvar_maizef),cmap=plt.cm.bwr,vmin=-0.5,vmax=0.5)

cbar = map.colorbar(cs1,location='bottom',size="5%",pad="2%")
cbar.ax.tick_params(labelsize=15) 
plt.axis('off')


ax2 = fig.add_subplot(325)
ax2.set_title("ISAM-M3 Maize Yield gridcell (%)",fontsize=20)
map = Basemap(projection ='cyl', llcrnrlat=-65, urcrnrlat=90,llcrnrlon=-180, urcrnrlon=180, resolution='c')
#map = Basemap(projection='robin',lon_0=0,resolution='c')
map.drawcoastlines()
map.drawcountries()
map.drawmapboundary()
cs1 = map.pcolormesh(x,y,((yield_fine*ncvar_maize1*1000/gridarea*1000)-(ncvar_maizef*ncvar_maize1*1000/gridarea*1000))/(ncvar_maizef*ncvar_maize1*1000/gridarea*1000)*100,cmap=plt.cm.bwr,vmin=-100,vmax=100)
#cs1 = map.pcolormesh(x,y,(yield_fine)-(ncvar_maizef),cmap=plt.cm.bwr,vmin=-0.5,vmax=0.5)

cbar = map.colorbar(cs1,location='bottom',size="5%",pad="2%")
cbar.ax.tick_params(labelsize=15)
plt.axis('off')


ax2 = fig.add_subplot(326)
ax2.set_title("CLM-M3 Maize Yield gridcell (%)",fontsize=20)
map = Basemap(projection ='cyl', llcrnrlat=-65, urcrnrlat=90,llcrnrlon=-180, urcrnrlon=180, resolution='c')
#map = Basemap(projection='robin',lon_0=0,resolution='c')
map.drawcoastlines()
map.drawcountries()
map.drawmapboundary()
cs1 = map.pcolormesh(x,y,((yield_clmtf*ncvar_maize1*1000/gridarea*1000)-(ncvar_maizef*ncvar_maize1*1000/gridarea*1000))/(ncvar_maizef*ncvar_maize1*1000/gridarea*1000)*100,cmap=plt.cm.bwr,vmin=-100,vmax=100)
#cs1 = map.pcolormesh(x,y,(yield_fine)-(ncvar_maizef),cmap=plt.cm.bwr,vmin=-0.5,vmax=0.5)

cbar = map.colorbar(cs1,location='bottom',size="5%",pad="2%")
cbar.ax.tick_params(labelsize=15)
plt.axis('off')



plt.savefig('maim3_ncep.jpg',dpi=300,bbox_inches='tight')
#plt.show()


fig, ax = plt.subplots(figsize=(6,6))
colors = (0,0,1)
colorsr = (1,0,0)

ax.plot([0,1200],[0,1200], 'k--',label='1:1')

ax.scatter(ncvar_maizef*ncvar_maize1*1000/gridarea*1000, yield_fine*ncvar_maize1*1000/gridarea*1000, c=colors,alpha=1,label='ISAM')
ax.scatter(ncvar_maizef*ncvar_maize1*1000/gridarea*1000, yield_clmtf*ncvar_maize1*1000/gridarea*1000, c=colorsr,alpha=0.2,label='CLM')

plt.xlim(0, 1200)
plt.ylim(0, 1200)
ax.set_title('Maize yield over gridcell',fontsize=18)
ax.legend()
plt.tick_params(axis='both',labelsize=15)

plt.xlabel('M3-Crops (g/$\mathregular{m^2}$)',fontsize=18)
plt.ylabel('Model (g/$\mathregular{m^2}$)',fontsize=18)
plt.savefig('scatter_maim3_ncep.png',bbox_inches='tight')
#plt.show()



