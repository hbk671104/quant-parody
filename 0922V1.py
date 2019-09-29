import urllib
import numpy as np
import csv
import matplotlib.pyplot as plt
from scipy import linalg as LA
import random

tickers = ["BTC","ETH","EOS","USDT"]  

num_year = int(input("Number of days in which the data is extracted:"))
print ""

prices   = []
Pricebox = np.zeros((len(tickers)+1,num_year))
return1  = np.zeros((len(tickers),num_year-1))
z=0

with open('BTC_historical.csv', 'rb') as csvfile:                                       #  Estract the price data from excel sheet
    spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for row in spamreader:

        prices=row[0].split(",")

        for i in range(0,num_year):
            Pricebox[z][i]=float(prices[(i+1)])

        z=z+1

for t in range(1,len(tickers)):
   for i in range(0,num_year-1):
      return1[t-1][i] = (Pricebox[t][i]-Pricebox[t][i+1])/(Pricebox[t][i+1])              #   compute the daily return for given number of years

return1[len(tickers)-1]=0

np.set_printoptions(linewidth=200)


mean1   = np.zeros(len(tickers))
cov1    = np.zeros((len(tickers),len(tickers)))
var1    = np.zeros((len(tickers),1))

cov1      = np.cov(return1)                                                             #   compute cov for the returns

for i in range (0,len(tickers)):
  var1[i] = cov1[i][i]                                                                  #    compute var for the returns

for i in range(0,len(tickers)):
  mean1[i] = np.mean(return1[i])                                                        #    compute mean for the returns

cov1[:][3]=10**-10
cov1[3][:]=10**-10

Lag1    = np.zeros(num_year-1)                                                      #    Create Parameters to solve linear equation
Lag2    = np.zeros(num_year-1)                                                      #    Lag1,Lag2 are sets of 2 lagrange multipliers
Lagones = np.ones(len(tickers))                                                         #    Create 1*N matrix
Laga    = np.dot(np.dot((np.transpose(Lagones)),(np.linalg.inv(cov1))),Lagones)
Lagb    = np.dot(np.dot((np.transpose(Lagones)),(np.linalg.inv(cov1))),mean1)           #    Laga,b,c are 3 parameters which is created to make solve the equations
Lagc    = np.dot(np.dot((np.transpose(mean1)),(np.linalg.inv(cov1))),mean1)

frontier_mean, frontier_var, frontier_weights = [], [], []

Lagcount=0                                                                              #    Create a counter start from 0

minvar=1/Laga                                                      #Directly find min variance
#print "Min Var", 1/Laga

minweight=np.dot(np.linalg.inv(cov1),Lagones)/Laga

#print minweight                                                  #Find corresponding weights for min var

minvarreturn=np.dot(minweight,mean1)                            #Compute




for r in np.linspace(minvarreturn, max(mean1), num=20):                                  #    Solve the linear equation to find w for the given return between min(mean1)and max(mean1)                    
    Lag1[Lagcount] = (Lagc-Lagb*r)/(Lagc*Laga-(Lagb)**2)                                #    Calculate the two lagrange multipliers for each set of data
    Lag2[Lagcount] = (Laga*r-Lagb)/(Lagc*Laga-(Lagb)**2)                                #    Plug back to solve for weight w
    frontier_weights.append(np.dot(np.linalg.inv(cov1),(Lag1[Lagcount]*Lagones+Lag2[Lagcount]*mean1)))
    frontier_mean.append(r)                      #    Use w to calculate the mean and var
    frontier_var.append(np.dot(np.dot(frontier_weights[Lagcount], cov1), frontier_weights[Lagcount]))
    Lagcount       = Lagcount+1

aa = np.array(frontier_mean)                                                            #    Transform list to array
bb = np.array(frontier_var)
cc = frontier_weights

indexmin=frontier_var.index(min(frontier_var))
aa[indexmin]=minvarreturn
bb[indexmin]=minvar
cc[indexmin]=minweight

plt.plot(bb,aa,'r',linewidth=3)                                                      #     draw the graph of curve beyond the max mean1
#plt.plot(var1,mean1,'ro')
plt.plot(minvar,minvarreturn,'ro')
plt.text(minvar+0.000005,minvarreturn,"MVP")
plt.ylabel('Portfolio Daily Return')
plt.xlabel('Portfolio Variance')
"""
for i in range(0,len(tickers)):
    plt.text(var1[i], mean1[i],tickers[i],fontsize=8)
"""    
#plt.text(0.00005, 0.014,'Min Variance Portfolio',fontsize=12.5)
#plt.text(0.00005, 0.012,'Investment Opportunity Frontier for 50 Risky Asset',fontsize=12.5)
plt.xlim(0,0.0050)
plt.ylim(-0.02,0.04)
plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
plt.show()
