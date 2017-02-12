def source_function_name(modnames,modules,keywords,master_data_structure):
    from shutil import copyfile
    import os
    import numpy as np
    from subprocess import call
    import re
    import sys
    import scipy
    import scipy.optimize as optimize
    import imp
    np.set_printoptions(threshold=np.nan,suppress=True)
    SCRIPTDIR=os.path.dirname(os.path.realpath(__file__))
    import os
    copyfile(SCRIPTDIR+'/gen_template_'+keywords['template'],os.getcwd()+'/POSCAR.template')
    with open("POSCAR", "wt") as fout:
        with open("POSCAR.template", "rt") as fin:
            for line in fin:
                for i in range(1,keywords['nions']+1):
                    line=line.replace('ion'+str(i), keywords['ion'+str(i)])
                fout.write(line)
    return master_data_structure
