import matplotlib.pyplot as plt
import math


coord = [[700,400], [400,600], [300,400], [210,300], [200,100], [700,400]]
coord2 = []
coord3 = []
x = 100
xx = 800
counter = 0
for idx in range(len(coord) - 1):
    x1 = coord[idx][0]
    y1 = coord[idx][1]
    x2 = coord[idx + 1][0]
    y2 = coord[idx + 1][1]
    a=y2 - y1
    b=x1-x2
    c1=(x2 - x1)*y1 - (y2 - y1)*x1
    c2_prim = c1 + 10*math.sqrt(a*a + b*b)
    c2_secont = c1 - 10*math.sqrt(a*a + b*b)
    y = (-c2_prim - (y2-y1)*x)/(x1-x2)
    yy = (-c2_prim - (y2-y1)*xx)/(x1-x2)
    coord2.append([x,y])
    coord2.append([xx,yy])
    y11 = (-c2_secont - (y2-y1)*x)/(x1-x2)
    yy11 = (-c2_secont - (y2-y1)*xx)/(x1-x2)
    coord3.append([x,y11])
    coord3.append([xx,yy11])
    break

xs, ys = zip(*coord)
plt.plot(xs,ys)

xs2, ys2 = zip(*coord2)
plt.plot(xs2,ys2)

xs3, ys3 = zip(*coord3)
plt.plot(xs3,ys3)

plt.show()
