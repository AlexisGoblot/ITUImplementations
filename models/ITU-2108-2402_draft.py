#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np 
import bqplot
import matplotlib.pyplot as plt 
import astropy.units as u


# In[ ]:


fGHz=6
#tau = 3*u.ns


# In[ ]:


K1 = 93*fGHz**0.175
A1 = 0.05


# In[2]:


import scipy.stats as st 
N = st.norm()


# In[ ]:


p = np.linspace(0,1,100)
theta = 5*np.pi/180


# In[ ]:


arg = A1*(1-theta)+theta
term1  = (-K1*(np.log(1-p))*(np.cos(arg)/np.sin(arg)))**(0.5*(np.pi/2-theta)/(np.pi/2))
term2 = -1 - 0.6*N.isf(p)
Lces  = term1 + term2


# In[ ]:


plt.plot(Lces,p)


# In[ ]:


class ITU(object):
    def __init__(self,**kwargs):
        self.dinput = kwargs
    def __repr__(self):
        st = ''
        for k in self.dinput:
            st = st + str(k) + ' : ' + str(self.dinput[k])+'\n'
        return(st)
    
    def ppf(self,p):
        p = np.array([p])
        model = self.dinput['model']
        return dfunct[model](p,self.dinput)
        
        


# In[ ]:


import pdb


# In[ ]:


def Lces_ITU_2108(p,din):
    """
    Parameters
    ----------
    
    p : probability in [0,1]  axis 0 
    
    din : dict of parameters 
    
        fGHz       axis 1
        thetadeg   axis 2
        
      
    Implementation of formula (6) page 8 of Rec UIT-R P.2108-0
    
    """
    NorLaw = st.norm()
    fGHz = np.r_[din['fGHz']]
    thetadeg = np.r_[din['thetadeg']]
    theta = thetadeg*np.pi/180
    
    K1 = 93*fGHz[None,:,None]**0.175
    A1 = 0.05
    arg = A1*(1-theta[None,None,:]) + theta[None,None,:]
    #pdb.set_trace()
    term1  = (-K1*(np.log(1-p[:,None,None]))*(np.cos(arg)/np.sin(arg)))**(0.5*(np.pi/2-theta[None,None,:])/(np.pi/2))
    term2 = -1 - 0.6*NorLaw.isf(p[:,None,None])
    return(term1 + term2)       


# In[ ]:


dfunct ={}
dfunct[2108]=Lces_ITU_2108


# In[ ]:


M = ITU(fGHz=6,thetadeg=7,model=2108)


# In[ ]:


p = np.linspace(0.01,1-0.01,100)


# In[27]:


plt.plot(M.ppf(p).ravel(),p)


# In[ ]:


N = st.norm()


# In[ ]:


plt.plot(N.ppf(p),p)


# In[ ]:


get_ipython().run_line_magic('timeit', 'u1 = np.random.rand(100)')


# In[ ]:


U = st.uniform()


# In[ ]:


get_ipython().run_line_magic('timeit', 'u2 = U.rvs(100)')


# In[ ]:


u1 = np.random.rand(100000)


# In[ ]:


h =plt.hist(N.ppf(u1),bins=100)


# # ITU 2402

# ## Génération des variables aléatoires

# In[ ]:





# In[108]:


# Nombre de réalisation
N = 1000


# In[98]:


DB1 = st.norm(15,scale=3)
DB12 = st.norm(50,scale=5)
Hb = st.norm(25,scale=5)
Hs = 15 # Transmitter Height


# In[104]:


def roof_heights(Hs,Hb,N):
    X = (Hb.rvs(4*N)-Hs).reshape(N,4)
    return X


# In[105]:


#param = {'Kdr':(0.5,"Upper fraction of distance probability range for re'flection distances")}
#'kdh':(1.5,"Adjusts distance/height ratio of diffraction building height'),
#'Khc':(0.3,"A probability which adjusts the critical diffraction height')}
#       'Krc':𝐾𝑟𝑐3.0Frequency in GHz defining regions of reflection loss
# 15Slope in dB/decade of low-frequency reflection rang
Kdr = 0.5
Kdh = 1.5
Khc = 0.3
Krc = 3.0
Krs = 15
Krm = 8


# In[109]:


db1 = DB1.rvs(N)


# In[106]:


Hbxs = roof_heights(Hs,Hb,N)  # (8)


# In[107]:


Hbxs


# In[60]:


Hc = Hb.ppf(Khc) # (9a)
Hb = roof_heights(Hs,Hb) # (9b)


# In[62]:


Hbxs


# In[63]:


Hb


# In[13]:


x = np.linspace(0,40,100)
p = np.linspace(0,1,100)
plt.plot(x,DB1.cdf(x))


# In[ ]:




