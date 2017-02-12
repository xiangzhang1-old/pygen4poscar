# Usage
This set of tools uses python to deal with POSCAR5 Direct.

# Data structure

## General
SCRIPTDIR : '/home/zkdsnbzx/src/pypos'
list element[:] : ['La','Mn','O','O','O']
np.float64 cell[0:2][0:3] : [a1,a2,a3],[b1,b2,b3],[c1,c2,c3]] (POSCAR)
np.float64 base[0:2][0:3] : [[rx1,ry1,rz1],[rx2,ry2,rz2],...,[rx10,ry10,rz10]] (0<rx,ry,rz<1, Direct)
np.float64 rpos_imaged[:][0:3] : [[rx1-1,ry1-1,rz1-1],...,[rx10+1,ry10+1,rz10+1]] (Direct)
np.float64 pos_original[:][0:3] : [[rx1,ry1,rz1],[rx2,ry2,rz2],...,[rx10,ry10,rz10]] * [a\\,b\\,c] (Cartesian)
np.float64 pos_imaged[:][0:3] : [[rx1-1,ry1-1,rz1-1],...,[rx10+1,ry10+1,rz10+1]] * [a\\,b\\,c] (Cartesian)
np.float64 dist_qui[:][0:5] : [id_imaged1,id_imaged2,atomid1,atomid2,|r1-r2|]
ele_* : element of homogeneous list *
id_* : id of homogeneous list * (starting from 0)
tmp_??? : tmp physical quantity with meaning ???
* : really physical (core) quantity with meaning *
master_data_structure:{'quantity':quantity}, used for passing&using in functions in modules

## Parameters (keywords)
truncate_dist_at        integer
exclude_pair[:][0:1]    list
exclude_ele_pair[:][0:1]    list
exclude_dist[:][0]      np.float64

##calculate_mag_j
np.float64 dist_noindex_nonrep[0:?][0]     np.float64    all dis_truncated[:][2] 1E-3    ? row * [dis]
np.float64 dist_qui_ex_tr[:][0:5] : dis_qui exclude-ed and truncated
np.float64 effective_magnetic_pair[:][0:2] : effective magnetic pairs a.k.a. pairs in dist_qui_tr_ex

##genposcar_using_radius
np.float64 dist_noindex_nonrep[0:?][0]     np.float64    all dis_truncated[:][2] 1E-3    ? row * [dis]
np.float64 dist_qui_ex_tr[:][0:5] : dis_qui exclude-ed and truncated
np.float64 target_pair[:][0:2] : effective magnetic pairs a.k.a. pairs[id0_imaged:id1_imaged] in dist_qui_tr_ex
