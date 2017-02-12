def source_function_name(modnames,modules,keywords,master_data_structure):
    import os
    import numpy as np
    from subprocess import call
    import re
    import sys
    import scipy
    np.set_printoptions(threshold=np.nan,suppress=True)
    SCRIPTDIR=os.path.dirname(os.path.realpath(__file__))
    #----------------------------------User-adjustable parameters. -----------------------------------
    ### ALL SUB-SCRIPTS USING THIS TOOL MUST IMPLEMENT THESE PARAMETERS, or STATE OTHERWISE!. ###
    #exclude_dist
    #exlude_pair
    #truncate_dist_at
    #exclude_ele_pair
    #----------------------------------End adjustable parameters------------------------------------
    #1.get system parameter
    f=open("POSCAR","r")
    master_data_structure['lines']=f.readlines()
    master_data_structure['base']=[master_data_structure['lines'][i].split()[0:3] for i in range(8,len(master_data_structure['lines']))]
    master_data_structure['cell']=[master_data_structure['lines'][i].split() for i in range(2,5)]
    master_data_structure['element']=[]
    for tmp_nelement in range(0,len(master_data_structure['lines'][5].split())):
        for tmp_natom_perelement in range(0,int(master_data_structure['lines'][6].split()[tmp_nelement])):
            master_data_structure['element'].append(master_data_structure['lines'][5].split()[tmp_nelement])
    if len(master_data_structure['base'][-1])==0:
     print 'Warning: last line of POSCAR should not be empty, watch it! Removing the last line...'
     master_data_structure['base'].pop(-1)
    if len(master_data_structure['base'][-1])==0:
     print 'Error: last line of POSCAR still empty! '
     exit(-1)
    master_data_structure['base']=np.float64(master_data_structure['base'])
    master_data_structure['cell']=np.float64(master_data_structure['cell'])
    #2.image to supercell
    master_data_structure['pos_imaged']=[]
    master_data_structure['rpos_imaged']=[]
    for i in [0,1,-1]:
     for j in [0,1,-1]:
      for k in [0,1,-1]:
       tmp_image_shift=np.float64([i,j,k])
       for id_base in range(0,len(master_data_structure['base'])):
        ele_pos_imaged=tmp_image_shift+master_data_structure['base'][id_base]
        master_data_structure['rpos_imaged'].append(ele_pos_imaged)
        ele_pos_imaged=np.dot(ele_pos_imaged,master_data_structure['cell'])
        master_data_structure['pos_imaged'].append(ele_pos_imaged)
    master_data_structure['pos_imaged']=np.float64(master_data_structure['pos_imaged'])
    master_data_structure['rpos_imaged']=np.float64(master_data_structure['rpos_imaged'])
    master_data_structure['pos_original']=np.dot(master_data_structure['base'],master_data_structure['cell'])
    master_data_structure['pos_original']=np.float64(master_data_structure['pos_original'])
    #3.calculate distances
    #calculate dist_qui
    master_data_structure['dist_qui']=[]
    changefromto=[]
    for id1_base in range(0,len(master_data_structure['base'])):
     for id2_base in range(0,len(master_data_structure['base'])):
      for id2_pos_imaged in [id2_base+tmp_image_shift*len(master_data_structure['base']) for tmp_image_shift in range(0,27)]:
       tmp_dist=np.linalg.norm(master_data_structure['pos_original'][id1_base]-master_data_structure['pos_imaged'][id2_pos_imaged])
       if abs(tmp_dist)<0.1:
        continue
       #THE 'IF' JUDGEMENT THAT ADD 0.4 TO disTANCES WHEN NECESSARY. i IS THE INDEX OF FIRST ATOM, STARTING FROM 0. j IS THAT OF THE SECOND. k IS THE INDEX OF IMAGED SECOND ATOM.
       #if i>1 and j>1:
        #dist=dis`t+0.4
       id1_pos_imaged=id1_base
       master_data_structure['dist_qui'].append([id1_pos_imaged,id2_pos_imaged,id1_base,id2_base,tmp_dist])
    master_data_structure['dist_qui']=np.float64(master_data_structure['dist_qui'])
    master_data_structure['dist_qui']=master_data_structure['dist_qui'][np.argsort(master_data_structure['dist_qui'][:,4])]
    #get the excluded distances using exclude_ele_pair
    for ele_exclude_pair in keywords['exclude_pair']:
        ele_exclude_pair=np.float64(ele_exclude_pair)
        exclude_quis=[ele_dist_qui for ele_dist_qui in master_data_structure['dist_qui'] if ele_dist_qui[2]==ele_exclude_pair[0] and ele_dist_qui[3]==ele_exclude_pair[1]]
        if exclude_quis!=[]:
            keywords['exclude_dist'].append(exclude_quis[0][4])
    keywords['exclude_dist']=np.float64(keywords['exclude_dist'])
    #ending
    return master_data_structure
