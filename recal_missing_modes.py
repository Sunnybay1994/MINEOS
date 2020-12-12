#!/usr/bin/env python
import sys,os,re,logging
# import multiprocessing as mp
from multiprocessing import Pool

# chkm_indir = 'CHECKMODE_INPUT_FILES'
# chkm_outdir = 'CHECKMODE_OUTPUT_FILES'
# mineos_indir = 'MINEOS_INPUT_FILES'

#logger
logger = logging.getLogger('recal_missing_modes')
logger.setLevel(logging.DEBUG) #CRITICAL>ERROR>WARNING>INFO>DEBUG》NOTSET
fh = logging.FileHandler('recal_missing_modes.log')
fh.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s(%(process)d-%(processName)s): (%(levelname)s) %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

def get_fn_from_dir(fn, order=1):
    logging.info('loading files with name "' + os.path.basename(fn) + '" from "' + os.path.dirname(fn) + '"')
    if 'win' in sys.platform:
        list1 = os.popen('dir/b/on ' + fn).readlines()
        dirname = os.path.dirname(fn)
        list1 = list(map(lambda x: os.path.join(dirname, x), list1))
    elif 'linux' in sys.platform:
        list1 = os.popen('ls ' + fn).readlines()
    else:
        logger.error('unknown platform: %s'%sys.platform)
        return 0
    if order == -1:
        list1.reverse()
    return list(map(lambda x: x.strip('\n'), list1))


def recal_missing_modes(fn,chkm_indir='CHECKMODE_INPUT_FILES',chkm_outdir=\
    'CHECKMODE_OUTPUT_FILES',mineos_indir='MINEOS_INPUT_FILES',\
        fre_inc=0.1,lnum=2,max_attempt=100):
    fn = os.path.basename(fn)
    logger.info('Start finding missing mode: ' + fn)

    [_,ts,l] = re.split('[._]',fn)
    ts = ts[:3] # tor or sph
    l = int(l[-5:]) # parameter l for normal mode

    # initialize checkmode input file
    fn_chk_in0 = os.path.join(chkm_indir,'checkmode.' + ts + 'inp_00' + str(l).zfill(5))
    fn_chk_in1 = os.path.join(chkm_indir,'checkmode.' + ts + 'inp_01' + str(l).zfill(5))
    with open(fn_chk_in0,'r') as fin:
        with open(fn_chk_in1,'w') as fout:
            fout.write(fin.readline())
            line = list(fin.readline())
            line[-11] = '1'
            fout.write(''.join(line))
            line = list(fin.readline())
            line[-7] = '1'
            fout.write(''.join(line))
            line = list(fin.readline())
            line[-7] = '1'
            fout.write(''.join(line))
            fout.write(fin.readline())
            fout.write(fin.readline())

    # read data from mineos input file
    fn_m_in0 = os.path.join(mineos_indir,'mineos.inp' + ts + '_00' + str(l).zfill(5))
    with open(fn_m_in0,'r') as fin:
        fn_model = fin.readline()
        fn_mout_fre0 = fin.readline()
        line = list(fn_mout_fre0)
        line[-11] = '1'
        fn_mout_fre1 = ''.join(line)
        fn_mout_fun0 = fin.readline()
        line = list(fn_mout_fun0)
        line[-11] = '1'
        fn_mout_fun1 = ''.join(line)
        para1 = fin.readline()
        para2 = fin.readline().strip().split()
        para2[4] = str(lnum)
        start_feq0 = float(para2[2])
    
    # built an empty checkmode output file to trigger recalculate procedure 
    flag = os.path.join(chkm_outdir,'checkmode.' + ts + 'out_01' + str(l).zfill(5))
    with open(flag,'w') as fo:
        logger.debug(flag)
        fo.write('Initialize...')
    count = 0

    # change start frequency and recalculate untill 
    fn_m_in1 = os.path.join(mineos_indir,'mineos.inp' + ts + '_01' + str(l).zfill(5))
    while count <= max_attempt:
        count += 1
        for start_feq in [start_feq0 + fre_inc * count, start_feq0 - fre_inc * count]:
            start_feq = round(start_feq,3)
            logger.debug(count)
            if os.path.isfile(flag) and start_feq >= 0.05:
                os.remove(flag)
                # write minos input file
                with open(fn_m_in1,'w') as fout:
                    fout.write(fn_model)
                    fout.write(fn_mout_fre1)
                    fout.write(fn_mout_fun1)
                    fout.write(para1)
                    para2[2] = str(start_feq)
                    fout.write(' '.join(para2))
                # recalculate and recheck
                logger.info('Recalculating with start frequency ' + str(start_feq) + ' Hz (attempt count:' + str(count) + ')')
                status = list(os.popen('./mineos < ' + fn_m_in1))
                logger.debug(''.join(status))
                status = list(os.popen('./checkmode < ' + fn_chk_in1))
                logger.debug(''.join(status))
        if not os.path.isfile(flag):
            logger.info('Missing fundamental mode found.')
            break
    
    # merge file
    logger.info('Merging...')
    cmdin_txt = '2\n' + fn_mout_fun0.strip() + '\n' + fn_mout_fun1.strip() + '\n' + fn_mout_fun0.strip() + '\n'
    # fn_merge_in = 'merge_cmdin_' + ts + '_' + str(l).zfill(5) + '.txt'
    # with open(fn_merge_in,'w') as fo:
    #     fo.write(cmdin_txt)
    # status = list(os.popen('./mineos_merge < ' + fn_merge_in))
    status = list(os.popen('echo "' + cmdin_txt + '" | ./mineos_merge'))
    logger.debug(''.join(status))
    # os.remove(fn_merge_in)
    logger.info('Done merging.')
    logger.info('ALL DONE: ' + fn)


if __name__ == "__main__":
    chkpath = 'CHECKMODE_OUTPUT_FILES/checkmode.*out_00*'
    flist = get_fn_from_dir(chkpath)
    # recal_missing_modes('checkmode.torout_0000002')
    with Pool() as p:
        p.map(recal_missing_modes,flist)

# To run the script on freeosc (change 'cu2' to idle nodes):
# sbatch --nodelist=cu2 --ntasks-per-node=24 recal_missing_modes.py 