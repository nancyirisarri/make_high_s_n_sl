import subprocess
import glob

# Get the OBJECT of the SourceLists, which we have stored in a 
# txt file.
with open('dr1_sls_object.txt', 'r') as fp:
    objs = fp.read()
    
objs = objs.split('\n')
objs = [i for i in list(objs) if len(i) > 0]

# Remove the OBJECTs that have been processed.
objs_done = glob.glob('logs/*make_sourcelist_high_s_n.log')
objs_done = [
  i[i.find('KIDS'):i.find('-make_s')] for i in list(objs_done)
]

for i in objs_done:
    try:
        indx = objs.index(i)
        objs.pop(indx)
        
    except:
        pass

# Run the script for 5 OBJECTs.
objs = objs[:5]

objs = sorted(objs)

print objs

for i in objs:
    subprocess.call(
      "awe make_sourcelist_high_s_n.py %s '*src_KCv1.6_Iv5*'" % i,
      shell=True
    )
    
    filename_log = glob.glob(
      '*%s-make_sourcelist_high_s_n.log' % i
    )[0]

    subprocess.call(
      'mv %s logs/' % filename_log, shell=True
    )
