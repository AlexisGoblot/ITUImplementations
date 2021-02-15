## This is an analysis of the Munich Data

```python
>>> import numpy as np 
>>> import shapely as sha
>>> import matplotlib.pyplot as plt
>>> import matplotlib.cm as cm
>>> from shapely.geometry.polygon import LinearRing
>>> %pylab inline
>>> #
... # See http://www.lx.it.pt/cost231/final_report.htm
... #
... 
>>> D = np.fromfile('Munich_buildings.res',dtype=int,sep=' ')
>>> D = D.reshape(17445,8)
>>> 
>>> #Tx      = np.round(np.r_([1281.36,1381.27,0,0,1,515]))
... bdgold = 1
>>> lring = []
>>> lcoords = []
>>> for k in range(17445):
...     x1 = D[k,0]
...     y1 = D[k,1]
...     x2 = D[k,2]
...     y2 = D[k,3]
...     z  = D[k,4]
...     bdg = D[k,5]
...     bdc = D[k,6]
...     ght = D[k,7]
>>> 
...     if (bdgold-bdg)!=0:
...         ring = LinearRing(lcoords)
...         lring.append(ring)
...         lcoords = []
>>> 
...     bdgold=bdg
...     lcoords.append((x1,y1))
...     lcoords.append((x2,y2))
>>> 
>>> # Route 0 
... 
>>> R0 = np.fromfile('route0.rx',dtype=int,sep=' ')
>>> R0 = R0.reshape(len(R0)/3,3)
>>> R1 = np.fromfile('route1.rx',dtype=int,sep=' ')
>>> R1 = R1.reshape(len(R1)/3,3)
>>> R2 = np.fromfile('route2.rx',dtype=int,sep=' ')
>>> R2 = R2.reshape(len(R2)/3,3)
>>> 
>>> # PathLoss
... PL = np.fromfile('pathloss.res',sep=' ')
>>> 
>>> p1 = PL[0:1420]
>>> p2 = PL[1420:1420+1845]
>>> p3 = PL[1420+1845:]
>>> 
>>> pl1 = p1.reshape(len(p1)/4,4)
>>> pl2 = p2.reshape(len(p2)/3,3)
>>> pl3 = p3.reshape(len(p3)/2,2)
>>> 
>>> Metro200 = np.hstack((pl1[:,1],pl2[:,1]))
>>> Metro201 = pl1[:,2]
>>> Metro202 = np.hstack((pl1[:,3],pl2[:,2],pl3[:,1]))
>>> 
>>> 
>>> def plotcity(lring,ax,title=''):
...     for k in range(len(lring)):
...         x,y = lring[k].xy
...         ax.plot(x,y,'k',linewidth=0.5)
...         #ax.axis('scaled')
...         #ax.set_title(title)
...     return ax     
>>> 
>>> # figure 
... nfig = 3
>>> if nfig==1:
...     fig = plt.figure(figsize=(20,20))
...     ax = fig.add_subplot(111)
...     ax = plotcity(lring,ax)
...     plt.axis('scaled')
>>> if nfig==3:
...     fig = plt.figure(figsize=(30,20))
...     ax1 = fig.add_subplot(321)
...     ax1 = plotcity(lring,ax1,title='Metro 200')    
>>> 
...     ax1.scatter(1281.36,1381.27,s=100,c='r')
...     ax1.scatter(R0[:,1],R0[:,2],s=10,c=Metro200,cmap=cm.hot,linewidth=0)
>>> 
...     ax2 = fig.add_subplot(322)
...     ax2.plot(-Metro200)
...     ax2.set_title('Metro 200')
...     ax3 = fig.add_subplot(323)
...     ax3 = plotcity(lring,ax3,title='Metro 201')    
>>> 
>>> 
...     ax3.scatter(1281.36,1381.27,s=100,c='r')
...     ax3.scatter(R1[:,1],R1[:,2],s=10,c=Metro201,cmap=cm.hot,linewidth=0)
>>> 
...     ax4 = fig.add_subplot(324)
...     ax4.plot(-Metro201)
...     ax4.set_title('Metro 201')
>>> 
...     ax5 = fig.add_subplot(325)
...     ax5 = plotcity(lring,ax5,title='Metro 202')    
>>> 
>>> 
...     ax5.scatter(1281.36,1381.27,s=100,c='r')
...     ax5.scatter(R2[:,1],R2[:,2],s=10,c=Metro202,cmap=cm.hot,linewidth=0)
>>> 
...     ax6 = fig.add_subplot(326)
...     ax6.plot(-Metro202)
...     ax6.set_title('Metro 202')
>>> 
...     d0 = np.sqrt((R0[:,1]-1231.36)**2+(R0[:,2]-1381.27)**2)
...     d1 = np.sqrt((R1[:,1]-1231.36)**2+(R1[:,2]-1381.27)**2)
...     d2 = np.sqrt((R2[:,1]-1231.36)**2+(R2[:,2]-1381.27)**2)
...     #plt.scatter(R1[:,1],R1[:,2],s=10,c='g')
...     #plt.scatter(R2[:,1],R2[:,2],s=10,c='c')
>>> 
...     plt.show()
Populating the interactive namespace from numpy and matplotlib
```

```python
>>> from pylayers.gis.ezone import *
```

Munich 48.8 11.35

```python
>>> E=Ezone('N48E011')
```

```python
>>> E.getdem()
Download srtm file
SRTMDownloader - server= dds.cr.usgs.gov, directory=srtm/version2_1/SRTM3.
No cached file list. Creating new one!
createFileListHTTP
```

```python
>>> E=Ezone
```

```python

```
