#!/usr/bin/python
#Program:
#	This program works in the parent directory of subdirectories containing VASP calculations for magnetic configurations.
#	The subdirectories are named in a 44-- fashion, corresponding to a magnetic configuration of 4,-4,4,-4 in POSCAR_M, which only contains magnetic ions.
#	Files and directories with letters a-z,A-Z in their names are ignored.
#
#	Based on the Heisenberg Hamiltonian, construct array of equations like 3J_1+2J_2+0J_3+E_0=E
#	and outputs its rank.
#	Prints the solved J's, a pair of atoms whose magnetic coupling are of the J's type, and the distances.
#
#	Different magnetic interactions are classified according to interatomic distances. An error of 1E-5 is allowed, so trim your POSCAR_M if necessary!
#	However, for pairs with same distances but different types of couplings, the distances are manually increased by 0.4 in all outputs (and in the program itself).
#	Also, distances are calculated between atoms in a unit cell, and its 27 nearest mirrors (for obvious reasons).
#
#Usage:
#	Execute the python script directly in the parent directory. No parameters are needed.
#
#Tunable parameters:
#	keywords['truncate_dist_at'] = maximum number of distances
#	keywords['exclude_dist'] = interatomic distances corresponding to the J's. (remember to add 0.4 if necessary)
#	keywords['exclude_pair'] = pair effective_magnetic_pair corresponding to the J's
#	The IF statement...
#
#Dependencies:
#	~/src/gadgets/grepen, that, when run in a directory with OUTCAR, outputs the energy, which
#	 should be something like: grep "energy without" OUTCAR | tail -1 | awk '{printf "%12.6f \n", $5 }'
#History:
#	2015/08/13 Xiang First release
#	2015/08/15 Xiang Modified to distplay matrix rank, and use least square method.
#	2015/08/23 Xiang Modified to read POSCAR_M, to include keywords['exclude_pair'] feature, and to include +0.4 mechanism.
#	2015/08/28 Xiang Modified to conform to VBird Shebang standard.
#
#STATEMENT: DID NOT IMPLEMENT exlude_ele_pair
#
#Wrapper
def source_function_name(modnames,modules,keywords,master_data_structure):
    import os
    import numpy as np
    from subprocess import call
    import re
    import sys
    import scipy
    np.set_printoptions(threshold=np.nan,suppress=True)
    SCRIPTDIR=os.path.dirname(os.path.realpath(__file__))
    #4.get non-repetitive distance list and truncate distance with a list-of-array:dist_qui_ex_tr and list dist_noindex_nonrep
    dist_noindex_nonrep=[]
    dist_qui_ex_tr=[]
    for ele_dist_qui in master_data_structure['dist_qui']:
     tmp_dist=ele_dist_qui[4]
     if (abs(keywords['exclude_dist']-tmp_dist)<1e-3).any():   #problem here is ACCURACY
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
    #get effective_magnetic_pair. do this with a list of list of 2-element-lists:effective_magnetic_pair
    effective_magnetic_pair=[]
    for tmp_dist in dist_noindex_nonrep:
     effective_magnetic_pair.append([[x[2],x[3]] for x in dist_qui_ex_tr if abs(x[4]-tmp_dist)<1e-3])

    #II.In root folder with 11111111-------- format, get each folder's magmomlist:mag_list
    print '============================================================================================================================================'
    print '\tEquation'
    print '============================================================================================================================================'
    matrices=[]
    for i in range(0,keywords['truncate_dist_at']):
     tmpmat=np.zeros((len(master_data_structure['base']),len(master_data_structure['base'])))
     for j in effective_magnetic_pair[i]:
      tmpmat[tuple(j)]=tmpmat[tuple(j)]+0.5
     matrices.append(tmpmat)
    #iterate through subdirs
    A=[]
    b=[]
    x=[]
    for subdir in os.popen('ls').read().split():
     if re.search('[a-zA-Z]',subdir):
      continue
     #get magnetic moments list
     mag_list=[]
     mag_list=' '.join(subdir).split()
     if 1==3:
      for i in range(0,len(mag_list)):
       if mag_list[i]=='-' and i>=8:
        mag_list[i]=-0.5
       elif mag_list[i]=='-' and i<8:
        mag_list[i]=-2
       elif mag_list[i]=='1' and i>=8:
        mag_list[i]=0.5
       elif mag_list[i]=='0':
        mag_list[i]=0
       else:
        mag_list[i]=2
     elif 1==2:
      for i in range(0,len(mag_list)):
       if mag_list[i]=='-' and i>=2:
        mag_list[i]=-0.5
       elif mag_list[i]=='-' and i<2:
        mag_list[i]=-2
       elif mag_list[i]=='1' and i>=2:
        mag_list[i]=0.5
       elif mag_list[i]=='0':
        mag_list[i]=0
       else:
        mag_list[i]=2
     else:
      for i in range(0,len(mag_list)):
       if mag_list[i]=='-':
        mag_list[i]=-1
       else:
        mag_list[i]=1
     #A_line=(product1,product2,...), set matrix mat first
     A_line=[]
     for i in range(0,keywords['truncate_dist_at']):
      product_x=np.matrix(mag_list)
      product_xT=product_x.getT()
      product=product_x*matrices[i]*product_xT
      A_line.append(product.item(0))
     A_line.append(1)
     A.append(A_line)
     os.chdir(subdir)
     energy=os.popen('grepen').read()
     os.chdir('..')
     b.append(energy)
    #specific assignments
    #A.append([1,0,0,0])
    #b.append(3.6718/8065.54429)
    #III. Compute energy-coefficient of various J's. THE LAST J IS NON-MAG BASIC ENERGY.
    #solve linear equation by least-squre
    solution,residuals,rank,singular=np.linalg.lstsq(A,b,rcond=-1)
    for i in range(0,len(A)):
     print '\t'+' \t'.join(format(A[i][idx],'5.1f')+'J_'+str(idx+1)+'+' for idx in range(0,len(A[i])))+'\t&=&\t'+str(float(b[i]))+' eV\\\\ '
    print '============================================================================================================================================'
    print '\tSolution'
    print '============================================================================================================================================'
    for i in range(0,len(solution)):
     if i==len(solution)-1:
      pairsname="Non-magnetic energy"
     else:
      pairsname="distance:"+"{:.4f}".format(dist_noindex_nonrep[i])+'\tpairs:'+str(np.int_(np.array(effective_magnetic_pair[i][0])+1))+'\t'+str(len(effective_magnetic_pair[i])/2)+'pairs/unitcell'
     print '\t'+'J'+str(i+1)+'\t=\t'+"{:8.4f}".format(solution[i])+' eV\t# '+pairsname
    print '\tNorm of residual='+str(residuals*8065.54429)+' cm-1\tEquation rank='+str(rank)
    tmpE=abs(solution[0]*6+max(solution[1],solution[2])*12)*11601
    print solution[1],solution[2],solution[0]
    print max(tmpE-1000,50),tmpE+1000,100

    #for i in effective_magnetic_pair:
    # for j in i:
    #  print j

    return master_data_structure
