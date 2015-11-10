# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 08:36:11 2015

@author: michaelwransky
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi


def voronoi_finite_polygons_2d(vor, radius=None):
    """
    Reconstruct infinite voronoi regions in a 2D diagram to finite
    regions.

    Parameters
    ----------
    vor : Voronoi
        Input diagram
    radius : float, optional
        Distance to 'points at infinity'.

    Returns
    -------
    regions : list of tuples
        Indices of vertices in each revised Voronoi regions.
    vertices : list of tuples
        Coordinates for revised Voronoi vertices. Same as coordinates
        of input vertices, with 'points at infinity' appended to the
        end.

    """

    if vor.points.shape[1] != 2:
        raise ValueError("Requires 2D input")

    new_regions = []
    new_vertices = vor.vertices.tolist()

    center = vor.points.mean(axis=0)
    if radius is None:
        radius = vor.points.ptp().max()

    # Construct a map containing all ridges for a given point
    all_ridges = {}
    for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
        all_ridges.setdefault(p1, []).append((p2, v1, v2))
        all_ridges.setdefault(p2, []).append((p1, v1, v2))

    # Reconstruct infinite regions
    for p1, region in enumerate(vor.point_region):
        vertices = vor.regions[region]

        if all(v >= 0 for v in vertices):
            # finite region
            new_regions.append(vertices)
            continue

        # reconstruct a non-finite region
        ridges = all_ridges[p1]
        new_region = [v for v in vertices if v >= 0]

        for p2, v1, v2 in ridges:
            if v2 < 0:
                v1, v2 = v2, v1
            if v1 >= 0:
                # finite ridge: already in the region
                continue

            # Compute the missing endpoint of an infinite ridge

            t = vor.points[p2] - vor.points[p1] # tangent
            t /= np.linalg.norm(t)
            n = np.array([-t[1], t[0]])  # normal

            midpoint = vor.points[[p1, p2]].mean(axis=0)
            direction = np.sign(np.dot(midpoint - center, n)) * n
            far_point = vor.vertices[v2] + direction * radius

            new_region.append(len(new_vertices))
            new_vertices.append(far_point.tolist())

        # sort region counterclockwise
        vs = np.asarray([new_vertices[v] for v in new_region])
        c = vs.mean(axis=0)
        angles = np.arctan2(vs[:,1] - c[1], vs[:,0] - c[0])
        new_region = np.array(new_region)[np.argsort(angles)]

        # finish
        new_regions.append(new_region.tolist())

    return new_regions, np.asarray(new_vertices)

#function to determine if point is within polygon
def point_in_poly(x,y,poly):

    n = len(poly)
    inside = False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside

#dust drift function
#NOTE INPUT IS IN METERS
def dust_drift(meter):
    #coefficients a,b,c,d are from experimental data
    a=15.59
    b=-11.46
    c=1.734
    d=-0.006923

    concentration = a*np.exp(b*meter/10)+c*np.exp(d*meter/10)
    return concentration

#function for the distance to the hive
def dist_hive(x,y):
    distance_to_hive = np.sqrt(pow((x-2000),2)+pow((y-2000),2))
    return distance_to_hive

#function to pick the 10 foraging locations
#function takes a random sample of potential foraging locations
#returns 10 most likely foraging sites based on distance to hive
def foraging_sites(forage_points):
    visit_prob=[]; number_list=[]
    numb_points=len(forage_points)
    pick20 = np.random.randint(numb_points,size=(15,1))
    def getKey(item):
        return item[0]
    for i in range(0,15):
        
        prob=0.1227*np.exp(-0.002151*dist_hive(forage_points[pick20[i]][0],forage_points[pick20[i]][1]))
        visit_prob.append([prob,forage_points[pick20[i]][0],forage_points[pick20[i]][1]])

    sorted_20=sorted(visit_prob,key=getKey)
    
    top10=sorted_20[5:15]
    top10_points=np.zeros((10,2))
    top10_prob=np.zeros((10,1))
    for i in range(0,10):
        top10_points[i,0]=top10[i][1]
        top10_points[i,1]=top10[i][2]
        top10_prob[i]=top10[i][0]
    
    return top10_prob, top10_points
def print_concentrations(top10,area):
    for i in range(0,10):
        print area[top10[i,0]][top10[i,1]]
        
def hit_or_miss(top10,radius,area):
    
    bee_exposure=np.zeros((10000,1))
    for i in range(0,10):
        
        centerx=top10[i,0]; centery=top10[i,1]
        for j in range(0,1000):
            np.random.seed()
            minus=np.random.randint(2,size=(1,1))
            concent=0
            while concent==0:
                if minus == 1:
                    numberx=np.random.randint(radius,size=(1,1))
                    numbery=np.random.randint(radius,size=(1,1))
                else:
                    numberx = -1*np.random.randint(radius,size=(1,1))
                    numbery = -1*np.random.randint(radius,size=(1,1))
                
                placex=centerx+numberx; placey=centery+numbery
                if placex>=4000 or placex<0:
                    placex=centerx
                if placey>=4000 or placey<0:
                    placey=centery
                
                concent=area[int(placex),int(placey)]
                
                #print concent
                
            bee_exposure[int((i*1000)+j)]=area[int(placex),int(placey)]
           
    return bee_exposure




def create_voronoi_points():
    np.random.seed(1234)
    points=np.random.randint(4000,size=(6,2))
    return points


points=create_voronoi_points()

# make up data points

area=np.zeros((4000,4000))
# compute Voronoi tesselation
vor = Voronoi(points)

# plot
regions, vertices = voronoi_finite_polygons_2d(vor)
#print "--"
#print regions
#print "--"
#print vertices

# create landscape
forage_landscape=[]
np.random.seed()
corn_fields=np.random.randint(2,size=(6,1))
count=0
count2=0
for region in regions:
    
    iscorn=False
    if corn_fields[count2]==1:
        iscorn=True
    count2+=1


    polygon = vertices[region]
    centroid = points[count]
    #print polygon
    count += 1
    
    numbp= len(polygon[:,0])

    if iscorn:
        plt.fill(*zip(*polygon), facecolor='y')
    else:
        plt.fill(*zip(*polygon), facecolor='g')

    #plt.fill(*zip(*polygon), alpha=0.4)
    #plt.plot(polygon[:,0], polygon[:,1], 'ko')
    
    for b in range(-150,150):
        for l in range(0,numbp-1):
            x1 = polygon[l,0]+b; y1 = polygon[l,1]
            x2 = polygon[l+1,0]+b; y2 = polygon[l+1,1]
            deltax = x2-x1; deltay = y2-y1

            if deltax ==0:
                if y1<=y2:
                    ystart=int(y1)
                    yend=int(y2+1)
                else:
                    ystart=int(y2)
                    yend=int(y1+1)
                for y in range(ystart,yend):
                    if not point_in_poly(int(x1),y,polygon):
                        #plt.plot(int(x1),y)
                        if 0<int(x1)<4000:
                            if 0<int(y)<4000:
                                if iscorn:
                                    forage_landscape.append((int(x1),y))
                                    area[int(x1),y]=dust_drift(abs(b))
                                #else:
                                    #forage_landscape.append((int(x1),y))
                        
                
            elif deltay ==0:
                if x1<=x2:
                    xstart=int(x1)
                    xend=int(x2+1)
                else:
                    xstart = int(x2)
                    xend = int(x1+1)
                for x in range(xstart,xend):
                    if not point_in_poly(x,int(y1),polygon):
                        #plt.plot(x,int(y1))
                        if 0<x<4000:
                            if 0<int(y1)<4000:
                                if iscorn:
                                    area[x,int(y1)]=dust_drift(abs(b))
                                    forage_landscape.append((x,int(y1)))
                                #else:
                                    #forage_landscape.append((x,int(y1)))
                                #area[x,int(y1)]=dust_drift(abs(b))
                   
            else:
                m=deltay/deltax
               
                if x1<=x2:
                    xstart=int(x1)
                    xend=int(x2+1)
                else:
                    xstart=int(x2)
                    xend=int(x1+1)
                for x in range(xstart,xend):
                    y = (m*x) + (y1-(m*x1))
                    if not point_in_poly(x,y,polygon):
                        #plt.plot(x,int(y),'ko')
                        if 0<x<4000:
                            if 0<y<4000:
                                if iscorn:
                                    forage_landscape.append((x,int(y)))
                                    area[x,int(y)]=dust_drift(abs(b))
                                #else:
                                    #forage_landscape.append((x,int(y)))
            

prob,pts = foraging_sites(forage_landscape)  
#print pts
bee_levels = hit_or_miss(pts,500,area)
#
num_bins = 500
## the histogram of the data
n, bins, patches = plt.hist(bee_levels, num_bins, facecolor='green', alpha=0.5)
plt.bar(bins[0:500],n[0:500],width=0.1)
plt.show()
    #area.fill(*zip(*polygon), alpha=0.4)

#plt.plot(points[:,0], points[:,1], 'ko')
#plt.xlim(0 - 0.1, 4000 + 0.1)
#plt.ylim(0 - 0.1, 4000 + 0.1)

#plt.show()

# plt.imshow(area)
# plt.show()
