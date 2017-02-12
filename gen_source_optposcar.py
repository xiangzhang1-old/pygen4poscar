#Comment
#   This script uses atomic radii to "guess" a POSCAR based on a template
#   The cell is optimized so that the distance of a few AB pairs are close to rA+rB
#   The nearest 5 distances (not pairs) with no C inside the smallest sphere enclosing A&B are considered.
#   \sum\abs(rA+rB-dist) are optimized.
#Algorithm
#   1) filter for selected_pairs
#   2) construct target function
#   3) optimize

#construct target function stack_closeness
#wrapper header

import os
import numpy as np
from subprocess import call
import re
import sys
import scipy
import scipy.optimize as optimize
np.set_printoptions(threshold=np.nan,suppress=True)
SCRIPTDIR=os.path.dirname(os.path.realpath(__file__))

def source_function_name(modnames,modules,keywords,master_data_structure):
    np.set_printoptions(threshold=np.nan,suppress=True)
    SCRIPTDIR=os.path.dirname(os.path.realpath(__file__))
    #get non-repetitive distance list and truncate/exclude distance
    dist_noindex_nonrep=[]
    dist_qui_ex_tr=[]
    for ele_dist_qui in master_data_structure['dist_qui']:
     tmp_dist=ele_dist_qui[4]
     if (abs(keywords['exclude_dist']-tmp_dist)<1e-3).any():   #problem here is ACCURACY
      continue
     #if bond comes into the sphere, dismiss it
     eleA=master_data_structure['element'][int(ele_dist_qui[2])] #eleA='La'
     radiusA=float(os.popen(SCRIPTDIR+'/radius '+eleA).read()) #raiuds La = 1.5A
     posA=master_data_structure['pos_imaged'][int(ele_dist_qui[0])] #posA=(1.355,2.353.6.756)
     eleB=master_data_structure['element'][int(ele_dist_qui[3])]
     radiusB=float(os.popen(SCRIPTDIR+'/radius '+eleB).read())
     posB=master_data_structure['pos_imaged'][int(ele_dist_qui[1])]
     posMidAB=(posA+posB)/2
     if ((np.linalg.norm(master_data_structure['pos_imaged']-posMidAB)-radiusA/2-radiusB/2)<1e-3).any():
         continue
     continue_flag=0
     for ele_exclude_ele_pair in keywords['exclude_ele_pair']:
         if eleA==ele_exclude_ele_pair[0] and eleB==ele_exclude_ele_pair[1]:
             continue_flag=1
         if eleA==ele_exclude_ele_pair[1] and eleB==ele_exclude_ele_pair[0]:
             continue_flag=1
         if continue_flag:
             continue
     if len(dist_noindex_nonrep)<=keywords['truncate_dist_at']:
       dist_qui_ex_tr.append(ele_dist_qui)
     else:
      break
     if len(dist_noindex_nonrep)==0 or (abs(dist_noindex_nonrep-tmp_dist)>1e-3).all():
      dist_noindex_nonrep.append(tmp_dist)
    dist_qui_ex_tr.pop(-1)
    dist_noindex_nonrep.pop(-1)
    dist_qui_ex_tr=np.float64(dist_qui_ex_tr)
    #get target_qui
    target_qui=[]
    for tmp_dist in dist_noindex_nonrep:
     target_qui.append([x for x in dist_qui_ex_tr if abs(x[4]-tmp_dist)<1e-3][0])
    #constraints: don't go too far
    def stack_closeness(cell_1d):
       sum=0
       #get ele_target_qui
       for ele_target_qui in target_qui:
           var_cell=[cell_1d[0:3],cell_1d[3:6],cell_1d[6:9]]
           var_cell=np.float64(var_cell)
           eleA=master_data_structure['element'][int(ele_target_qui[2])] #eleA='La'
           radiusA=float(os.popen(SCRIPTDIR+'/radius '+eleA).read()) #raiuds La = 1.5A
           eleB=master_data_structure['element'][int(ele_target_qui[3])]
           radiusB=float(os.popen(SCRIPTDIR+'/radius '+eleB).read())
           #the core quantity
           idA=int(ele_target_qui[0])
           idB=int(ele_target_qui[1])
           posA=np.dot(var_cell,master_data_structure['rpos_imaged'][idA])
           posB=np.dot(var_cell,master_data_structure['rpos_imaged'][idB])
           distAB=np.linalg.norm(posA-posB)
           sum=sum+np.exp(-keywords['bond_len_error']*keywords['bond_len_error']/(distAB-radiusA-radiusB)/(distAB-radiusA-radiusB))
       return sum
    cell_1d_0=master_data_structure['cell'].reshape(9)
    bnds=[[min(x*0.66,x*1.5),max(x*0.66,x*1.5)] for x in cell_1d_0]
    cell_optimized=optimize.minimize(stack_closeness,cell_1d_0,method='L-BFGS-B',bounds=bnds,tol=0.03)
    #result
    cell_optimized=cell_optimized.x.reshape(3,3)
    #write to poscar (overwrite)
    ##header
    lines_new=[]
    for id_line in [0,1]:
        lines_new.append(master_data_structure['lines'][id_line])
    for id_line in [0,1,2]:
        lines_new.append('\t'+'\t'.join("{0:.16f}".format(x) for x in cell_optimized[id_line])+'\n')
    for id_line in [5,6,7]:
        lines_new.append(master_data_structure['lines'][id_line])
    #base part (rpos)
    for i in range(8,len(master_data_structure['lines'])):
        lines_new.append(master_data_structure['lines'][i])
    ##write to poscar
    g=open("POSCAR.opt","w")
    g.seek(0,0)
    g.writelines(lines_new)
    #ending
    return master_data_structure
