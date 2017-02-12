#!/usr/bin/python
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

#==============0. SETUP==============
modnames={}
modules={}

f=open(SCRIPTDIR+'/'+"gen.conf.modules","r")
f.seek(0)
lines=f.read().splitlines()
for line in lines:
    line_list=line.split(':')
    modname=line_list[0]
    modnames[modname]=0
    nckw_list=filter(None,line_list[1].split(';'))
    modules[modname+'_nckw']={}
    for kwnamevalpair in nckw_list:
        kwname=kwnamevalpair.split('=')[0]
        exec ('kwval='+kwnamevalpair.split('=')[1]) #a string, by nature
        if not kwname or not kwval:
            print "kwname ",kwname," or kwval",kwval," empty"
            exit(64)
        modules[modname+'_nckw'][kwname]=kwval
    ckw_list=filter(None,line_list[2].split(';'))
    modules[modname+'_ckw']={}
    for kwname in ckw_list:
        modules[modname+'_ckw'][kwname]='ckw'

#==============1. INPUT==============
#--------------1.1 cmd-line read keywords--------------
keywords={}
sys.argv.pop(0)
while len(sys.argv)>0:
    argname=sys.argv.pop(0)
    shift_flag=0
    ismodule_flag=0
    for modname in modnames.keys():
        if  modname == argname :
            modnames[argname] = 1
            shift_flag = 1
            ismodule_flag = 1
            break
    if ismodule_flag == 1:
        continue
    #assign acclaimed keywords
    #1) check that claims are not self-conflicting
    if keywords.get(argname) is not None:
        print "error in folder",os.getcwd(), "sname {", keywords.get('sname'), '}:', "more than one assignment for keyword ", argname
        exit(64)
    #2) check that claim syntax are right i.e. contain $1 and $2
    if len(sys.argv)==0:
        print "error in folder", os.getcwd(), "sname {", keywords.get('sname'), '}:',argname," is not a module, and neither is argval specied"
        exit(64)
    exec('argval='+sys.argv.pop(0))
    keywords[argname]=argval
#--------------1.2 NC takes its place--------------
for modname in modnames.keys():
    if modnames[modname] == 0 :
        continue
    #keywords in ${modname}_nckw
    for kwname in modules[modname+'_nckw'].keys():
        if keywords.get(kwname) is None :
            keywords[kwname]=modules[modname+'_nckw'][kwname]
        elif keywords[kwname] != keywords.get(kwname)  :
            print "error in folder", os.getcwd(), "sname {", keywords.get('sname'), '}:', 'attempting to overwrite nckw kw ', kwname
            exit(64)

#--------------1.3 CUST--------------
modnames['virtual']=1
modules['virtual_nckw']={} #represents both nckw and ckw, since there is no need for ckw here
modules['virtual_ckw']={} #should remain empty
#--------------othercust----------------------
f.close()
f=open(SCRIPTDIR+'/'+"gen.conf.othercust","r")
f.seek(0)
lines=f.read().splitlines()
for line in lines:
    ifyes_list=filter(None,line.split(':')[0].split(';'))
    ifnot_list=filter(None,line.split(':')[1].split(';'))
    ifyes_kwnameval_list=filter(None,line.split(':')[2].split(';'))
    ifnot_kwnameval_list=filter(None,line.split(':')[3].split(';'))
    othercust_nc_list=filter(None,line.split(':')[4].split(';'))
    batchname_list=filter(None,line.split(':')[5].split(';'))
    force_flag=line.split(':')[6]
    ifyes_flag=1
    for modname in ifyes_list+ifnot_list :
        if modnames.get(modname) is None:
            print "error in folder", os.getcwd(), "sname {", keywords.get('sname'), '}:', 'modname {', modname, '} does not exist'
            exit(64)
    for modname in ifyes_list :
        if modnames[modname]== 0 :
            ifyes_flag=0
            break
    for modname in ifnot_list :
        if modnames[modname]== 1 :
            ifyes_flag=0
            break
    for kwnamevalpair in ifyes_kwnameval_list:
        kwname=kwnamevalpair.split('=')[0]
        exec ('kwval='+kwnamevalpair.split('=')[1])
        if not kwname or not kwval:
            print "cont.othercust error: kwname {",kwname,"} or kwval {",kwval,"} empty"
            exit(64)
        if str(keywords.get(kwname)) != kwval :
            ifyes_flag=0
    for kwnamevalpair in ifnot_kwnameval_list:
        kwname=kwnamevalpair.split('=')[0]
        exec ('kwval='+kwnamevalpair.split('=')[1])
        if not kwname or not kwval:
            print "cont.othercust error: kwname {",kwname,"} or kwval {",kwval,"} empty"
            exit(64)
        if str(keywords.get(kwname)) == kwval :
            ifyes_flag=0
    if ifyes_flag == 1 :
        for batchname in batchname_list :
            source_module_name = imp.load_source(batchname,SCRIPTDIR+'/'+batchname+'.py')
            keywords=source_module_name.source_function_name(modnames,modules,keywords,force_flag)
        for kwname in othercust_nc_list :
            modules['virtual_nckw'][kwname]='othercust_nc'
#--------------confcust----------------------
f.close()
f=open(SCRIPTDIR+'/'+"gen.conf.cust","r")
f.seek(0)
lines=f.read().splitlines()
for line in lines:
    ifyes_list=filter(None,line.split(':')[0].split(';'))
    ifnot_list=filter(None,line.split(':')[1].split(';'))
    ifyes_kwnameval_list=filter(None,line.split(':')[2].split(';'))
    ifnot_kwnameval_list=filter(None,line.split(':')[3].split(';'))
    cust_nc_list=filter(None,line.split(':')[4].split(';'))
    cust_c_list=filter(None,line.split(':')[5].split(';'))
    force_flag=line.split(':')[6]
    ifyes_flag=1
    for modname in ifyes_list+ifnot_list :
        if modnames.get(modname) is None:
            print "conf.cust error in folder", os.getcwd(), "sname {", keywords.get('sname'), '}:', 'modname {', modname, '} does not exist'
            exit(64)
    for modname in ifyes_list :
        if modnames[modname]== 0 :
            ifyes_flag=0
            break
    for modname in ifnot_list :
        if modnames[modname]== 1 :
            ifyes_flag=0
            break
    for kwnamevalpair in ifyes_kwnameval_list:
        kwname=kwnamevalpair.split('=')[0]
        exec ('kwval='+kwnamevalpair.split('=')[1])
        if not kwname or not kwval:
            print "conf.othercust error: kwname {",kwname,"} or kwval {",kwval,"} empty"
            exit(64)
        if keywords.get(kwname) != kwval :
            ifyes_flag=0
    for kwnamevalpair in ifnot_kwnameval_list:
        kwname=kwnamevalpair.split('=')[0]
        exec ('kwval='+kwnamevalpair.split('=')[1])
        if not kwname or not kwval:
            print "conf.othercust error: kwname {",kwname,"} or kwval {",kwval,"} empty"
            exit(64)
        if str(keywords.get(kwname)) == kwval :
            ifyes_flag=0
    if ifyes_flag == 1 :
        for kwname in cust_c_list :
            modules['virtual_nckw'][kwname]='cust_c'
        for kwnamevalpair in cust_nc_list:
            kwname=kwnamevalpair.split('=')[0]
            exec ('kwval='+kwnamevalpair.split('=')[1])
            if kwname is None or kwval is None:
                print "conf.cust error: kwname ",kwname," or kwval",kwval," empty"
                exit(64)
            if keywords.get(kwname) is not None and keywords.get(kwname) != kwval :
                if force_flag == 1 :
                    print "error in folder", os.getcwd(), "sname {", keywords.get('sname'), '}:', "attempting to overwrite nckw keyword",kwname,'value',keywords[kwname],', with value {}',kwval,'}'
                    exit(64)
                else:
                    print "warning in folder", os.getcwd(), "sname {", keywords.get('sname'), '}:', 'conf.cust attempted to overwrite keyword',kwname, 'value',keywords[kwname],'with cust value',kwval, 'but failed: overwrite is not mandatory: ref gen.conf.cust line',line
                    continue
            keywords[kwname]=kwval
            modules['virtual_nckw'][kwname]='cust_nc'

#=============2. CHECK==============
#--------------2.1 check kwc--------------
#all active module keywords, changeable or non-changeable, are non-empty: otherwise quit---------
for modname in modnames.keys() :
    if modnames[modname] == 0 :
        continue
    #keywords in ${modname}_ckw
    for kwname in modules[modname+'_ckw'].keys():
        if keywords.get(kwname) is None :
            print "check ckw/nckw integrity error in folder {", os.getcwd(), "} sname {", keywords.get('sname'), '}:', "changeable keyword {",kwname,'} not set, but is required as ckw by module {',modname
            exit(64)
    #keywords in ${modname}_nckw
    for kwname in modules[modname+'_nckw'].keys():
        if keywords.get(kwname) is None :
            print "check ckw/nckw integrity error in folder", os.getcwd(), "sname {", keywords.get('sname'), '}:', "non-changeable keyword",kwname,'.',kwname,'} not set, but is required as nckw by module {',modname
            exit(64)
#--------------2.2 optional mandatory mod--------------
f.close()
f=open(SCRIPTDIR+'/'+"gen.conf.opt_mand_modules","r")
f.seek(0)
lines=f.read().splitlines()
for line in lines:
    sum_actmod_list=filter(None,line.split(':')[0].split(';'))
    opt_mand_mod_list=filter(None,line.split(':')[1].split(';'))
    sum_opt_mand_mod=0
    for opt_mand_modname in opt_mand_mod_list:
        sum_opt_mand_mod=sum_opt_mand_mod+int(modnames[opt_mand_modname])
    ok_flag=0
    for sum_actmod in sum_actmod_list :
        if str(sum_opt_mand_mod) == str(sum_actmod) :
            ok_flag=1
    if not ok_flag:
        print "error in folder", os.getcwd(), "sname {", keywords.get('sname'), '}:', sum_actmod_list,"of the following modules", opt_mand_mod_list, "should be loaded: actually",sum_opt_mand_mod, "are."
        exit(64)
#---------------2.3 keys are sane------------------------
#ensure that all keywords belong to active modules: otherwise set to ""---------------
for kwname in keywords.keys():
    kw_orphan_flag=1   #keyword is an 'orphan' i.e. does not belong to module
    for modname in modnames.keys() :
        if modnames[modname] == 0 :
            continue
        for mod_kwname in modules[modname+'_nckw'].keys() :
            if mod_kwname == kwname :
                kw_orphan_flag=0
        for mod_kwname in modules[modname+'_ckw'].keys() :
            if mod_kwname == kwname :
                kw_orphan_flag=0
    if kw_orphan_flag == 1 :
        print "warning in folder", os.getcwd(), "sname {", keywords.get('sname'), '}:', kwname, "does not belong to any active module, but you have set it. it is now being set to None"
        keywords[kwname]=None
#-----------2.4 keyword checks: if $ifyes modules present and $ifnot not present, run $batchname: adopted from othercust-------------------
f.close()
f=open(SCRIPTDIR+'/'+"gen.conf.check","r")
f.seek(0)
lines=f.read().splitlines()
for line in lines:
    ifyes_list=filter(None,line.split(':')[0].split(';'))
    ifnot_list=filter(None,line.split(':')[1].split(';'))
    batchname_list=filter(None,line.split(':')[2].split(';'))
    ifyes_flag=1
    for modname in ifyes_list+ifnot_list :
        if modnames.get(modname) is None:
            print "error in folder", os.getcwd(), "sname {", keywords.get('sname'), '}:', 'modname {', modname, '} does not exist'
            exit(64)
    for modname in ifyes_list :
        if modnames[modname]== 0 :
            ifyes_flag=0
            break
    for modname in ifnot_list :
        if modnames[modname]== 1 :
            ifyes_flag=0
            break
    if ifyes_flag == 1 :
        for batchname in batchname_list :
            source_module_name = imp.load_source(batchname,SCRIPTDIR+'/'+batchname+'.py')
            master_data_structure=source_module_name.source_function_name(modnames,modules,keywords,master_data_structure)

#------------2.5 keyword nulliify, write KPOINTS----------------------------------
f.close()
f=open(SCRIPTDIR+'/'+"gen.conf.othercust","r")
f.seek(0)
lines=f.read().splitlines()
for line in lines:
    ifyes_list=filter(None,line.split(':')[0].split(';'))
    ifnot_list=filter(None,line.split(':')[1].split(';'))
    kwnullify_list=filter(None,line.split(':')[2].split(';'))
    ifyes_flag=1
    for modname in ifyes_list+ifnot_list :
        if modnames.get(modname) is None:
            print "kw.nullify error in folder", os.getcwd(), "sname {", keywords.get('sname'), '}:', 'modname {', modname, '} does not exist'
            exit(64)
    for modname in ifyes_list :
        if modnames[modname]== 0 :
            ifyes_flag=0
            break
    for modname in ifnot_list :
        if modnames[modname]== 1 :
            ifyes_flag=0
            break
    if ifyes_flag == 1 :
        for kwname in kwnullify_list:
            if not keywords.get(kwname):
                print "kw.nullify warning in folder", os.getcwd(), "sname {", keywords.get('sname'), '}:', 'keyword {', kwname, '} is supposed to be nullified, but it is already null'
            else:
                keywords[kwname]=None

#------------2.6 keyword bans: kwban_bc(ban content),kwban_bkw (ban keyword)----------------------------
f.close()
f=open(SCRIPTDIR+'/'+"gen.conf.kwban","r")
f.seek(0)
lines=f.read().splitlines()
for line in lines:
    ifyes_list=filter(None,line.split(':')[0].split(';'))
    ifnot_list=filter(None,line.split(':')[1].split(';'))
    kwban_bc_list=filter(None,line.split(':')[2].split(';'))
    kwban_bkw_list=filter(None,line.split(':')[3].split(';'))
    ifyes_flag=1
    for modname in ifyes_list+ifnot_list :
         if modnames.get(modname) is None:
            print "conf.kwban error in folder", os.getcwd(), "sname {", keywords.get('sname'), '}:', 'modname {', modname, '} does not exist'
            exit(64)
    for modname in ifyes_list :
        if modnames[modname]== 0 :
            ifyes_flag=0
            break
    for modname in ifnot_list :
        if modnames[modname]== 1 :
            ifyes_flag=0
            break
    if ifyes_flag == 1 :
        for kwnamevalpair in kwban_bc_list:
            kwname=kwnamevalpair.split('=')[0]
            exec ('kwval='+kwnamevalpair.split('=')[1])
            if keywords[kwname] == kwval :
                print "conf.kwban error in folder", os.getcwd(), "sname {", keywords.get('sname'), '}:', 'the value', kwval, 'of keyword', kwname,  'is banned (i.e. should not be this value). ref: gen.conf.kwban line', line
                exit(64)
        for kwname in kwban_bkw_list:
            if keywords.get(kwname) is not None:
                print "conf.kwban error in folder", os.getcwd(), "sname {", keywords.get('sname'), '}:', 'keyword', kwname,  'is banned (i.e. should be \"\"). ref: gen.conf.kwban line', line
                exit(64)

#=============3. Initialization Completed. Processing. ==============
f.close()
#master data structure
f=open(SCRIPTDIR+'/'+"gen.conf.master_data_structure","r")
f.seek(0)
master_data_structure_namelist=f.read().splitlines()[0].split(';')
master_data_structure={}
for name in master_data_structure_namelist:
    if name in vars() or name in globals():
        exec('master_data_structure[name]='+name)
    else:
        exec('master_data_structure[name]=None')
#postcheck, converted from othercust
f.close()
f=open(SCRIPTDIR+'/'+"gen.conf.postcheck","r")
f.seek(0)
lines=f.read().splitlines()
for line in lines:
    ifyes_list=filter(None,line.split(':')[0].split(';'))
    ifnot_list=filter(None,line.split(':')[1].split(';'))
    batchname_list=filter(None,line.split(':')[2].split(';'))
    ifyes_flag=1
    for modname in ifyes_list+ifnot_list :
        if modnames.get(modname) is None:
            print "error in folder", os.getcwd(), "sname {", keywords.get('sname'), '}:', 'modname {', modname, '} does not exist'
            exit(64)
    for modname in ifyes_list :
        if modnames[modname] != 1 :
            ifyes_flag=0
            break
    for modname in ifnot_list :
        if modnames[modname] == 1 :
            ifyes_flag=0
            break
    if ifyes_flag == 1 :
        for batchname in batchname_list :
            source_module_name = imp.load_source(batchname,SCRIPTDIR+'/'+batchname+'.py')
            master_data_structure=source_module_name.source_function_name(modnames,modules,keywords,master_data_structure)
            for name in master_data_structure.keys():
                exec (name+'=master_data_structure[name]')
