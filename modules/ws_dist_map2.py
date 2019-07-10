import numpy as np


from time import time

class map_1R():
   def __init__(self,lines,irvec):
       lines_split=[np.array(l.split(),dtype=int) for l in lines]
       self.dict={(l[0]-1,l[1]-1):l[2:].reshape(-1,3) for l in lines_split}
       self.irvec=np.array([irvec])
       
   def __call__(self,i,j):
       try :
           return self.dict[(i,j)]
       except KeyError:
           return self.irvec
          

class ws_dist_map():
    def __init__(self,iRvec,num_wann,lines):
        nRvec=iRvec.shape[0]
        self.num_wann=num_wann
        self._iRvec_new=dict()
        n_nonzero=np.array([l.split()[-1] for l in lines[:nRvec]],dtype=int)
        lines=lines[nRvec:]
        nonzero=[]
        t0=time()
        for ir,nnz in enumerate(n_nonzero):
            map1r=map_1R(lines[:nnz],iRvec[ir])
            for iw in range(num_wann):
                for jw in range(num_wann):
                    self._add_star(ir,map1r(iw,jw),iw,jw)
            lines=lines[nnz:]
        t1=time()
        self._iRvec_ordered=sorted(self._iRvec_new)
        for ir  in range(nRvec):
            chsum=0
            for irnew in self._iRvec_new:
                if ir in self._iRvec_new[irnew]:
                    chsum+=self._iRvec_new[irnew][ir]
            chsum=np.abs(chsum-np.ones( (num_wann,num_wann) )).sum() 
            if chsum>1e-12: print "WARNING: Check sum for ",ir," : ",chsum
        t2=time()
        print ("time for reading wsvec: {0}, for chsum: {1}".format(t1-t0,t2-t1))


    def _add_star(self,ir,irvec_new,iw,jw):
        weight=1./irvec_new.shape[0]
        for irv in irvec_new:
            self._add(ir,irv,iw,jw,weight)


    def _add(self,ir,irvec_new,iw,jw,weight):
        irvec_new=tuple(irvec_new)
        if not (irvec_new in self._iRvec_new):
             self._iRvec_new[irvec_new]=dict()
        if not ir in self._iRvec_new[irvec_new]:
             self._iRvec_new[irvec_new][ir]=np.zeros((self.num_wann,self.num_wann),dtype=float)
        self._iRvec_new[irvec_new][ir][iw,jw]+=weight
        
    def __call__(self,matrix):
        ndim=len(matrix.shape)-3
        num_wann=matrix.shape[0]
        reshaper=(num_wann,num_wann)+(-1,)*ndim
        matrix_new=np.array([ sum(matrix[:,:,ir]*self._iRvec_new[irvecnew][ir].reshape(reshaper)
                                  for ir in self._iRvec_new[irvecnew] ) 
                                       for irvecnew in self._iRvec_ordered]).transpose( (1,2,0)+tuple(range(3,3+ndim)) )
        assert ( np.abs(matrix_new.sum(axis=2)-matrix.sum(axis=2)).max()<1e-12)
        return matrix_new
             

#    def mapmat0d(self,matrix):
#        return self.mapmat(matrix)
#        matrix_new= np.array([ sum(matrix[:,:,ir]*self._iRvec_new[irvecnew][ir]
#                                  for ir in self._iRvec_new[irvecnew] ) 
#                                       for irvecnew in self._iRvec_ordered]).transpose( (1,2,0)  )        
#        assert ( np.abs(matrix_new.sum(axis=2)-matrix.sum(axis=2)).max()<1e-12)
#        return matrix_new
