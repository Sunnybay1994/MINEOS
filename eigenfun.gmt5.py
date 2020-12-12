#!/usr/bin/env python3
import argparse,os,logging,re

#logger
logger = logging.getLogger('eigenfun.gmt5.py')
logger.setLevel(logging.DEBUG) #CRITICAL>ERROR>WARNING>INFO>DEBUG》NOTSET
fh = logging.FileHandler('eigenfun.gmt5.py.log')
fh.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s(%(process)d-%(processName)s): (%(levelname)s) %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

def read_mode_and_draw(ffn,n,l,mode_Char,outdir='fig'):
    if not os.path.isdir(outdir):
        os.mkdir(outdir)

    fn_asc = '%d%s%d'%(n,mode_Char,l)
    # logger.info('Begin: %s-%s'%(ffn,fn_asc))
    fn_asc = os.path.join(outdir,fn_asc)

    logger.info('Reading %s from %s'%(fn_asc,ffn))
    read_cmdin = '%s\n%s.asc\n%d,%d\n'%(ffn,fn_asc,n,l)
    out = list(os.popen('echo "%s" | ./read_mineos'%read_cmdin))
    logger.debug(''.join(out))

    logger.info('Drawing %s'%fn_asc)
    out = list(os.popen('./eigenfun.gmt5 %s'%fn_asc))
    logger.info(''.join(out))
    logger.info('DONE.')



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Call "eigenfun.gmt5"')
    parser.add_argument('-n',type=int,default=1,help='Parameter n.')
    parser.add_argument('-l',type=int,default=1,help='Angular degree - l.')
    parser.add_argument('--mode',choices=['tor','sph'],default='sph',help='Toroidal or spheroidal mode.')
    parser.add_argument('--tor',action='store_const',const='tor',dest='mode',help='Toroidal mode.')
    parser.add_argument('--sph',action='store_const',const='sph',dest='mode',help='spheroidal mode.')
    parser.add_argument('--fn',default='PREMQL6ic_21808e.card',help='File name of input model.')
    parser.add_argument('--fdir',default='tmp',help='Directory MINEOS output files.')
    parser.add_argument('--pre',action='store_true',dest='pre',help='Draw some pre-defined modes.')
    args = parser.parse_args()

    fn = os.path.basename(args.fn)
    fdir = args.fdir
    if args.pre:
        modes_txt = '0T3, 0T25, 0T40, 0T120, 0T250, 4T2, 20T24, 12T30, ' + \
            '0S3, 0S25, 0S40, 0S120, 0S250, 4S2, 20S24, 12S30, 3S0, 25S0, 40S0'
        modes_list = modes_txt.split(', ')
        for s in modes_list:
            [n,l] = map(int,re.split('[TS]',s))
            mode = 'rad' if l==0 else 'tor' if 'T' in s else 'sph'
            logger.debug('mode=%d%s%d'%(n,mode,l))
            ffn_fun = '%s_%s_00%05d.fun'%(os.path.join(fdir,fn),mode,l)
            read_mode_and_draw(ffn_fun,n,l,mode[0].upper())
        
    else:
        l = args.l
        n = args.n
        mode = args.mode
        if l==0:
            mode = 'rad'
        ffn_fun = '%s_%s_00%05d.fun'%(os.path.join(fdir,fn),mode,l)
        read_mode_and_draw(ffn_fun,n,l,mode[0].upper())
    
