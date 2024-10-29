#  QAC:  "Quick Array Combinations" - lightweight version for qac2024
#
#        Helper functions for various Array Combination techniques
#        Some are wrappers around CASA, others are also convenient for regression and performance testing.
#

import os, sys, shutil, math, tempfile, glob
import os.path
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as pl
#    pyfits is still in 6.5, but not in 6.6
try:
    from astropy.io import fits
except:
    import pyfits as fits


_version  = "28-oct-2024 for qac2024"

#                  only support casa6 here
import casatools
is_casa6 = True    

print("Loading QAC %s" % _version)

# creating some convenient numbers in _local namespace
# one should definitely avoid using 2 letter variables, as CASA uses these a lot
# @todo:   wrap them inside the QAC class and/or pre_underscore them
_cqa  = qa.constants('c')                  # (turns out to be in m/s)
_cms  = qa.convert(_cqa,"m/s")['value']    # speed of light, forced in m/s (299792458.0)
_apr  = 180.0 * 3600.0 / np.pi             # arcsec per radian (206264.8)
_bof  = np.pi / (4*math.log(2.0))          # beam oversampling factor (1.1331) : NPPB = bof * (Beam/Pixel)**2  [cbm in tp2vis.py]
_stof = 2.0*np.sqrt(2.0*np.log(2.0))       # FWHM=stof*sigma  (2.3548)


def qac_version():
    """ qac version reporter """
    global qac_root
    print("qac: version %s" % _version)
    print("qac_root: %s = %s" % (qac_root, os.path.realpath(qac_root)))
    if False:
        # casa[] only exists in CASA5
        print("casa:" + casa['version'])        # there is also:   cu.version_string()
        print("data:" + casa['dirs']['data'])
    else:
        # this works in both CASA5 and CASA6 but depends on "au" having been loaded
        print("casa:" + au.casaVersion)
        print("data:" + os.getenv('CASAPATH').split()[0]+'/data')
        
    #-end of qac_version()    

def qac_log(message, verbose=True):
    """ qac banner message; can be turned off
    """
    if verbose:
        print("")
        print("========= QAC: %s " % message)
        print("")
        
    #-end of qac_log()

def qac_par(par):
    """ qac parameter logging, for eazier log parsing
        can do a list of parameters, but this is discouraged
    """
    if type(par) == type([]):
        fmt = "QAC_PAR:"
        for p in par:
            fmt = fmt + " " + p
        for p in par:
            fmt = fmt + " " + str(eval(p))
        print(fmt)
    else:
        print("QAC_PAR: %s %s" % (par,eval(par)))
        
    #-end of qac_par()
    

def qac_project(projectdir, chdir=False):
    """
        start a new project in given project directory name

        projectdir    directory name. it will be created (and removed if present)
        chdir         also change directory into this project directory
        exist ?       should we allow it to exist
        
    """
    print("QAC_PROJECT %s" % projectdir)
    os.system('rm -rf %s ; mkdir -p %s' % (projectdir,projectdir))
    if chdir:
        os.chdir(projectdir)
    
    #-end of qac_project()
    
    
def qac_tmp(prefix, tmpdir='.'):
    """ Create a temporary file in a tmpdir

        Parameters
        ----------
        prefix : str
           starting name of the filename in <tmpdir>/<pattern>

        tmpdir

        Returns
        -------
        Unique filename
    """
    fd = tempfile.NamedTemporaryFile(prefix=prefix,dir=tmpdir,delete='false')
    name = fd.name
    fd.close()
    return name

    #-end of qac_tmp()

def qac_image_desc(image, phasecenter=None, imsize=None, pixel=None):
    """
    Return image descriptors for QAC.
    image          : input image (casa or fits)
    phasecenter    : if given, passed through 
    imsize         : if given, passed through 
    pixel          : if given, passed through
    
    e.g.   (phasecenter, imsize, pixel) = qac_image_desc('skymodel.fits')
    """
    h0 = imhead(image,mode='list')
    ia.open(image)
    h1=ia.summary()
    ia.close()

    imsize1 = h0['shape'][0]
    imsize2 = h0['shape'][1]
    if imsize == None:
        if imsize1 == imsize2:
            imsize = imsize1
        else:
            imsize = [imsize1,imsize2]
    if phasecenter == None:
        _dpr = _apr / 3600.0
        phasecenter = 'J2000 %gdeg %gdeg' % (h0['crval1'] * _dpr, h0['crval2'] * _dpr)
    if pixel == None:
        pixel = abs(h0['cdelt1'] * _apr)
    print("qac_image_desc(%s) -> " % image, phasecenter, imsize, pixel)
    return (phasecenter, imsize, pixel)

    #-end of qac_image_desc()

 
def qac_im_ptg(phasecenter, imsize, pixel, grid, im=[], rect=True, factor=1.0, outfile=None):
    """
    Generate hex-grid of pointing centers that covers a specified area. 
    Can optionally output in file or as list. Can check for overlap with input image areas

    One can also use simobserve() to generate a pointing file. Note that this has two
    conventions:  maptype = "HEX" or "ALMA". For "HEX" the base of the triangle is horizontal,
    for "ALMA" the base of the triangle is vertical. This is also the shortest distance between
    two pointings, which is supposed to to be FWHM/2 (nyquist)
    Our qac_im_ptg() only has one convention: the "HEX" maptype (at least for now).
    
    Required Parameters
    -------------------
        phasecenter : str 
            phasecenter of the image/pointings *only in J2000 decimal degrees format* 
            Example: phasecenter = 'J2000 52.26483deg 31.28025deg'
            @todo:   phasecenter = 'J2000 12h22m54.900s +15d49m15.000s'

        imsize : int or list of 2 ints
            Number of pixels 
            Example: imsize = [1400,1800]
                     imsize = 500 is equivalent to [500,500] 
        pixel : float
            Pixel size in arcsecs
            Example: pixel = 0.5
        grid : float
            Separation of pointings in arcsecs (determined from beam size and sampling)
            For grid<=0 just the phasecenter is returned.
            Example: grid=15.9
                
    Optional Parameters
    -------------------
        im : list of strings @TODO
            Input image file name(s) as a string or list of strings. This determines the area covered by the pointings.
            Example: im=["GBT.im", "VLA.im"]
            Default: empty
        rect : boolean
            Indicates if only pointings within specified rectangular area will be reported
            Example: rect=False
            Default: True
        outfile : str
            If present, used as name of output file 
            Example: outfile="FinalGBT.ptg"
            Default: None (not used, only list returned)
    
    Returns
    -------
        finalPtglist : list of str
            Pointings in CASA J2000 degrees format
    
    
    -- Arnab Dhabal - Feb 14, 2018

    @todo  there are two ways to make a hex grid , point up or point at the side.
           this routine cannot switch and puts the point at th side.
    
    """
    def hex(nring,grid):
        coordlist = []
        for row in range(-nring+1,nring,1):
            y = 0.866025403 * grid * row
            lo = 2-2*nring+abs(row)
            hi = 2*nring-abs(row)-1
            for k in range(lo,hi,2):
                x = 0.5*grid*k
                coords = [x,y]
                coordlist.append((coords))
        return coordlist

    #check the trivial case with no grid
    if grid <= 0.0:
        if outfile != None:
            f= open(outfile,"w+")
            f.write("%s\n" % phasecenter)
            f.close()
        return [phasecenter]
        
    #check if images is list or single file or none
    if type(im) == type([]):
            im_list = im
    elif im == None:
        im_list = []
    else:
        im_list = [im]

    # convert phasecenter into ra,dec in degree
    phaseCenCoords = phasecenter.split(" ")
    if (phaseCenCoords[1][-3:] == "deg") and (phaseCenCoords[2][-3:] == "deg"):
        raDeg = float(phaseCenCoords[1][:-3])
        decDeg = float(phaseCenCoords[2][:-3])
    #print("RA:",raDeg, "Dec:",decDeg)
    cosdec = math.cos(decDeg*math.pi/180.0)
    
    imsize = QAC.imsize2(imsize)
    xim = imsize[0] * factor
    yim = imsize[1] * factor
        
    if yim/xim > np.sqrt(3):
        maxim = yim/2.0
        nring = int(np.ceil((pixel*maxim+0.5*grid)/(grid)))+1
    else:
        diag = np.sqrt(xim**2+yim**2)/2.0
        maxim = diag*np.cos(np.pi/6.0 - np.arctan(yim/xim))
        nring = int(np.ceil(pixel*maxim/(grid*np.cos(np.pi/6.0))))+1
        
    # print("rings:",nring)

    xylist = hex(nring,grid)
    ptgbool = [True]*len(xylist)
    #pointings only inside rect
    if(rect == True):
        for xyi in np.arange(0,len(xylist),1):
            if (xylist[xyi][0] > xim*pixel/2.0) or (xylist[xyi][0] < -xim*pixel/2.0) or (xylist[xyi][1] > yim*pixel/2.0) or (xylist[xyi][1] < -yim*pixel/2.0):
                ptgbool[xyi] = False
    

    #add phasecenter and generate J2000 deg pointings
    ralist = [0.0]*len(xylist)
    declist = [0.0]*len(xylist)
    for xyi in np.arange(0,len(xylist),1):
        ralist[xyi] = raDeg + xylist[xyi][0]/3600.0/cosdec
        declist[xyi] = decDeg + xylist[xyi][1]/3600.0
    
    #TODO: compare against each input file non-Nans
#    for imi in im_list
#        h0 = imhead(imi,mode='list')
#        ia.open(imi)
#        h1=ia.summary()
#        ia.close()
#        ??? = h0['...']
#        for xyi in np.arange(0,len(xylist),1):
#            if(... == np.nan):
#                ptgbool[xyi]=False
#        
#        
    #generate final J2000 deg pointings
    finalPtglist = []
    if outfile == None:
        for xyi in np.arange(0,len(xylist),1):
            if ptgbool[xyi] == True:
                strTemp = "J2000 " + str(round(ralist[xyi],6)) + "deg " + str(round(declist[xyi],6)) + "deg"
                finalPtglist.append(strTemp)
    else:
        n=0
        f= open(outfile,"w+")
        for xyi in np.arange(0,len(xylist),1):
            if ptgbool[xyi] == True:
                n=n+1
                strTemp = "J2000 " + str(round(ralist[xyi],6)) + "deg " + str(round(declist[xyi],6)) + "deg"
                f.write("%s\n" % strTemp)
                finalPtglist.append(strTemp)
        f.close()
        print("%d fields used in %s" % (n,outfile))
        
    return finalPtglist

    #-end of qac_im_ptg()

def qac_line(im):
    """
    return the line parameters for an image in terms of a dictionary for tclean()
    """
    h0 = imhead(im,mode='list')
    ia.open(im)
    h1=ia.summary()
    ia.close()
    #  we assume RA-DEC-POL-FREQ cubes as are needed for simobserve
    crp = h0['crpix4']
    crv = h0['crval4']
    cde = h0['cdelt4']
    ref = h0['restfreq'][0]
    nchan = h0['shape'][3]
    restfreq = str(ref/1e9) + 'GHz'
    width = -cde/ref*_cms/1000.0
    width = str(width) + 'km/s'
    start = (1-(crv - crp*cde)/ref)*_cms/1000.0
    start = str(start) + 'km/s'
    return {'start' : start, 'width' : width, 'nchan' : nchan, 'restfreq' : restfreq}

    #-end of qac_line()

def qac_fits(image, outfile=None, box=None, chans=None, smooth=None, stats=False, channel=0):
    """ exportfits shortcut, appends the extension ".fits" to a casa image
        also handles a list of images

        image     casa image, or list of images, to be converted to fits
        outfile   if given, output fits file name, else add ".fits" (not in list)
        box       if set, use a 'xmin,ymin,xmax,ymax' in 0 based pixels
        chans     if set, use a 'chmin~chmax' in 0 based pixels
        smooth    if set, it is the number of arcsec (circular beam) it should be smoothed to
        stats     if set, also make a qac_plot and qac_stats

        Returns the (last) fits file  (@todo: should do a list if input is a list)
    
    """
    def add_qac_history(image, idict):
        """ add the QAC keywords to the (FITS) history
        """
        def addkey(kv):
            """ add a key=val to the history of the fits file
            """
            print(kv)
        if idict == None:
            return
        ia.open(image)
        history = []
        for k in idict.keys():
            v = str(idict[k])
            history.append("QAC %s=%s" % (k,v))
        ia.sethistory(origin='QAC',history=history)
        ia.close()
        print(idict)
    #
    if type(image) == type([]):
        ii = image
    else:
        ii = [image]
    if box != None or chans != None:
        Qsubim = True
    else:
        Qsubim = False
    fi = None
    for i in ii:
        if not QAC.exists(i):
            print("warning: %s does not exist" % i)
            continue
        idict = qac_image(i,QAC.keys)
        fi = i + '.fits'
        if len(ii)==1 and outfile!=None:
            fi = outfile
        if smooth != None:
            tmpim1 = i + ".tmp1"
            #print("smooth=%g" % smooth)
            imsmooth(imagename=i,
                     outfile=tmpim1,
                     kernel='gauss',
                     major='%garcsec' % smooth,
                     minor='%garcsec' % smooth,                     
                     pa='0deg',
                     targetres=True,
                     overwrite=True)
        else:
            tmpim1 = i
        if Qsubim:
            tmpim2 = i + ".tmp2"
            imsubimage(tmpim1,tmpim2,box=box,chans=chans,overwrite=True)
            add_qac_history(tmpim2,idict)
            exportfits(tmpim2,fi,overwrite=True)
            #print("rm tmpim2")            
            QAC.rmcasa(tmpim2)
        else:
            add_qac_history(tmpim1,idict)            
            exportfits(tmpim1,fi,overwrite=True)
        if i != tmpim1:
            #print("rm tmpim1")
            QAC.rmcasa(tmpim1)
        print("Wrote " + fi)
        if stats:
            qac_stats(fi)
            qac_plot(fi,mode=1,channel=channel)
    return fi

    #-end of qac_fits()

def qac_import(fits, cim, phasecenter=None, dec=None, order=None):
    """ import a fits, and optionally place it somewhere else on the sky
        ? why is indirection not working in simobserve ?

        order:  by defalt not used, but ensure it's a Ra-Dec-Stokes-Freq (RDSF) cube,
                since this is what CASA wants.   e.g. order='0132'
                SHM: Why is this not an option in importfits()
    """
    if order != None:
        infile = cim + '.tmp'
        imtrans(fits,cim+'.tmp',order=order)
    else:
        infile = fits
        
    importfits(infile, cim, overwrite=True)
    if phasecenter != None:
        print("phasecenter=%s to be applied" % phasecenter)
    if dec != None:
        h0 = imhead(cim,mode='put',hdkey='crval2',hdvalue=dec)      
    h0 = imhead(cim,mode='list')
    print("crval2 = %g" % h0['crval2'])

def qac_ds9(image, cleanup=False):
    """
    poor man's ds9. assumes you have ds9 and xpatools installed in your $PATH
    ds9 must also be running already, or you must have the "tods9" script
    """
    # check if it's a directory, if so, we'll need a fits file
    if os.path.isdir(image):
        fi = qac_fits(image)
        # fi = qac_fits(image, image+'/'+image+'.fits'    # ???
    else:
        fi = image
    print("Sending %s to ds9" % fi)
    os.system("tods9 %s" % fi)
    if cleanup:
        os.system("rm %s" % fi)

    #-end of qac_ds9()
    

def qac_ingest(tp, tpout = None, casaworkaround=[1,3], ms=None, ptg=None):
    """
    Check (and optionally correct) that a TP image is a valid input for TP2VIS.
    This is also meant as a workaround certain CASA features (see bugs.txt)

    Currently you will need CASA 5.0 or above. 

    Inputs:
    tp                Input TP image to check (required)
    tpout             Output TP image (optional)
    casaworkaround    List of issues to work around CASA problems
                       1   ensure we have RA-DEC-POL-FREQ
                       2   ensure we have Jy/pixel, else scale down from
                           Jy/beam (deprecated, now in tp2vis on the fly)
                       3   ensure it is a casa image, not a fits file
                      11   reverse the FREQ axis (needs to be same as MS)
    ms                Input MS to check sign of TP channels
                      This will automatically enable workaround #11 if
                      the signs different.
    ptg               not implemented

    NOTE: some of these options cannot yet be combined in one run of
    tp2vischeck(), you will need to run it multiple times.

    This function was formerly known as tp2vischeck()
    
    If no tpout given, the routine returns True/False if the TP image
    was correct

    TODO:  add gridding options like:  nchan=43,start='214km/s',width='1.0km/s'
           but we also need to understand the rounding issues we have before
           with this in terms of loosing a first or last channel

    """
    def casa_version_check(version='5.5.0'):
        # @todo   fix this casa5 dependency
        # cur = casa['build']['version'].split('.')
        cur = au.casaVersion.split('.')
        req = version.split('.')
        print("casa_version_check: %s %s" % (cur,req))
        if cur[0] >= req[0]: return
        if cur[1] >= req[1]: return
        if cur[2] >= req[2]: return
        print("WARNING: your CASA is outdated %s %s" % (cur,req))
        
    def ms_sign(ms):
        if ms == None:
            return 0
        # if not iscasa(ms): return 0
        tb.open(ms + '/SPECTRAL_WINDOW')
        cw = tb.getcol('CHAN_WIDTH')
        print('CHAN_WIDTH=' + str(cw[0][0]))
        tb.close()
        if cw[0][0] > 0:
            return 1
        elif cw[0][0] < 0:
            return -1
        print("WARNING: unexpected chan_width")
        return 0      # should never happen

    def im_sign(im):
        if not QAC.iscasa(im): return 0
        ia.open(im)
        h0 = ia.summary()
        aname = h0['axisnames']
        incr =  h0['incr']
        print("AXIS NAMES:" + str(aname))
        print("incr      :" + str(incr))
        ia.close()
        #
        df = None
        for i in range(len(aname)):
            if aname[i] == 'Frequency':
                # print "Frequency found along axis ",i
                df = incr[i]
                break
        if df == None:
            print("Warning: no freq axis found")
            return 0
        if df > 0:
            return 1
        elif df < 0:
            return -1
        print("WARNING: unexpected freq incr %f" % df)
        return 0
        
    # create a local copy of the list, so no multiple call side-effects !!!
    if type(casaworkaround) == list:
        cwa = list(casaworkaround)
    else:
        cwa = [casaworkaround]
    print("tp2vischeck: casaworkaround: " + str(cwa))

    casa_version_check('5.6.0')

    # check sign of freq axis
    sign1 = ms_sign(ms)     # 0, 1 or -1
    sign2 = im_sign(tp)     # 0, 1 or -1
    if sign1*sign2 != 0 and sign1 != sign2:
        print("Adding workaround 11 for flip FREQ axis")
        cwa.append(11)

    # check if we have a fits file
    if not QAC.iscasa(tp) and not 3 in cwa:
        print("Converting fits file to casa image")
        cwa.append(3)
    elif 3 in cwa and QAC.iscasa(tp):
        print("Already have casa image")
        cwa.remove(3)

    if 3 in cwa:
        if tpout != None:
            importfits(tp,tpout,overwrite=True)
            print("Converted fits to casa image %s" % tpout)
            tp = tpout
            #print("Rerun tp2vischeck() to ensure no more fixed needed")
            #return
        else:
            print("No output file given, expect things to fail now")
    #print("PJT cwa",cwa)

    if 1 in cwa or 11 in cwa:
        #  1: ensure we have a RA-DEC-POL-FREQ cube
        # 11: reverse the FREQ axis to align with TP image
        ia.open(tp)
        h0 = ia.summary()
        aname = h0['axisnames']
        print("AXIS NAMES:" + str(aname))
        if len(aname) == 3:
            # ia.adddegaxes(stokes='I')
            print("Cannot deal with 3D cubes yet - fix this code")
            ia.done()
            return
        order = None
        if aname[2] == 'Frequency':
            if 11 in cwa:
                order = '01-32'
            else:
                order = '0132'
        elif 11 in cwa:
            order = '012-3'
        if order != None:
            print("FIX: ia.transpose order=" + order)
                
        if tpout != None:
            if order != None:
                # on older CASA before 5.0 you will loose beam and object name (bugs.txt #017)
                os.system('rm -rf %s' % tpout)
                ia2 = ia.transpose(outfile=tpout,order=order)
                ia.done()
                ia2.done()
                print("Written transposed " + tpout)
                print("Rerun tp2vischeck() to ensure no more fixed needed")
                return
            else:
                ia.done()                
                print("WARNING: No transposed needed")
        else:
            if order != None:
                print("WARNING: axis ordering not correct, please provide output name")
                return

    if 2 in cwa:
        # ensure we have Jy/pixel
        s0 = imstat(tp)
        h0 = imhead(tp)
        if 'unit' in h0:
            print("UNIT: " + h0['unit'])
        if 'flux' in s0:
            nppb = s0['sum'][0] / s0['flux'][0]
            print("NPPB = %g" % nppb)   # not BOF
            if tpout != None:
                os.system('rm -rf %s' % tpout)                
                expr = 'IM0/%g' % nppb
                immath(tp,'evalexpr',tpout,expr)
                imhead(tpout,'del','beammajor')
                imhead(tpout,'put','bunit','Jy/pixel')
                print("Written rescaled " + tpout)
                print("Rerun tp2vischeck() to ensure no more fixed needed")
                return
            else:
                print("Warning: %s is not in the correct units for tp2vis. Provide output file name" % tp)
        else:
            print("WARNING: No rescale fix needed")
        return

    # BUG 15
    # if sign of channel width in TP is not the same as that in MS, the TP needs to be
    # ran via imtrans(order='012-3')
    # could this be combined with the transpose() ?

    #-end of qac_ingest()

def qac_stats_grid(images, **kwargs):
    for image in images:
        qac_stats(image, **kwargs)
    
    
def qac_stats(image, test = None, eps=None, box=None, region=None, pb=None, pbcut=0.8, edge=False, sratio=True):
    """ summary of some stats in an image or measurement set
        in the latter case the flux is always reported as 0

        This routine can also be used for regression testing (see test=)

        image     image file name (CASA, FITS, MIRIAD)
                  measurement set also allowed, but limited stats will be given
        test      expected regression string
        eps       if given, it should parse the test string into numbers, each number
                  needs to be within relative error "eps", i.e. abs(v1-v2)/abs(v) < eps
        box       if used, this is the box for imstat()   box='xmin,ymin,xmax,ymax'
        region    alternative way to specify a region (file)
        pb        optional pb file, if the .image -> .pb would not work
        pbcut     only used for images, and a .pb should be parallel to the .image file
                  or else it will be skipped
        edge      take off an edge channel from either end (not implemented)
        sratio    also produce the Signal Ratio, defined as s=(FluxP-FluxN)/(FluxP+FluxN)
                  Flux = FluxP-FluxN  and FluxP/FluxN = (1-s)/(1+s)
                  FluxP = Flux * (1+s)/(2s)    FluxN = Flux * (1-s)/(2s)    

        Output should contain:   mean,rms,min,max,flux,[sratio]

        @todo   what when the .pb file is missing
    """
    def text2array(text):
        a = text.split()
        b = np.zeros(len(a))
        for i,ai in zip(range(len(a)),a):
            b[i] = float(ai)
        return b
    def arraydiff(a1,a2):
        delta = abs(a1-a2)
        idx = np.where(delta>0)
        return delta[idx]/a1[idx]
    def lel(name):
        """ convert filename to a safe filename for LEL expressions, e.g. in mask=
        """
        return '\'' + name + '\''
    
    qac_tag("plot")    
        
    if not QAC.exists(image):
        print("QAC_STATS: missing %s " % image)
        return
    
    if QAC.iscasa(image + '/ANTENNA'):                      # assume it's a MS
        Qms = True
        tb.open(image)
        data  = np.abs(tb.getcol('DATA')[0,:,:])  # first pol ->  data[nchan,nvis]
        mean = data.mean()
        rms  = data.std()
        min  = data.min()
        max  = data.max()
        flux = 0.0
        tb.close()
        del data
    else:                                                   # assume it's an IM
        Qms = False
        maskarea = None
        if pbcut != None:
            # this requires a .pb file to be parallel to the .image file
            if pb == None:
                pb = image[:image.rindex('.')] + '.pb'
                if QAC.iscasa(pb):
                    maskarea = lel(pb) + '>' + str(pbcut)      # create a LEL for the mask
            else:
                maskarea = lel(pb) + '>' + str(pbcut)
        if edge:
            nchan = imhead(image)['shape'][3]
            s0 = imstat(image,mask=maskarea,chans='1~%d' % (nchan-2),box=box,region=region)
        else:
            s0 = imstat(image,box=box,region=region,mask=maskarea)
        # mean, rms, min, max, flux
        # @TODO   this often fails
        mean = s0['mean'][0]
        rms  = s0['sigma'][0]
        min  = s0['min'][0]
        max  = s0['max'][0]
        if 'flux' in s0:
            flux = s0['flux'][0]
        else:
            flux = s0['sum'][0]
    test_new = "%s %s %s %s %s" % (repr(mean),repr(rms),repr(min),repr(max),repr(flux))
    if test == None:
        test_out = ""
        report = False
    else:
        if eps == None:
            if test_new == test:
                test_out = "OK"
                report = False
            else:
                test_out = "FAILED regression"
                report = True
        else:
            v1 = text2array(test_new)
            v2 = text2array(test)
            delta = arraydiff(v1,v2)
            print(delta)
            if delta.max() < eps:
                test_out = "OK"
                report = False
            else:
                test_out = "FAILED regression delta=%g > %g" % (delta.max(),eps)
                report = True
    if sratio and not Qms:
        if QAC.iscasa(image,'Image'):
            data = QAC.casa2np(image)
        else:
            data = QAC.fits2np(image)
        sump = data[data > 0.0].sum()
        sumn = data[data < 0.0].sum()
        sratio = (sump + sumn) / (sump - sumn)
        # print("SignalRatio: %g" % sratio)
        srat = str(sratio)
    else:
        srat = ""
            
    msg1 = "QAC_STATS: %s" % (image)
    print("%s %s %s %s" % (msg1,test_new,srat,test_out))
    if report:
        fmt1 = '%%-%ds' % (len(msg1))
        msg2 = fmt1 % ' '
        print("%s %s EXPECTED" % (msg2,test))
    
    #-end of qac_stats()
    




def qac_noise(noise, *args, **kwargs):
    """
    Calculate the simplenoise scaling factor given an expected thermal noise.
    See Carilli et al. (2017) for a writeup of the procedure.

    parameters
    ----------
    noise:           expected thermal noise for the final naturally weighted image (see http://ngvla.nrao.edu/page/refdesign)
                     Units should be Jy/beam
    *args:           args[0] = project, args[1] = ms --> ms should be noisy zero flux ms
    **kwargs:        keywords for calling qac_clean1()

    returns:
    --------
    sn_scale_factor: simplenoise scale factor to give expected thermal noise for a certain observation.
                     See e.g. qac_vla() how this is used and applied.
    
    """
    # copy kwargs dictionary
    clean_params = kwargs
    # force niter to zero
    clean_params['niter'] = [0]
    # force weighting to natural
    clean_params['weighting'] = 'natural'

    # run tclean on the noisy zero ms
    qac_clean1(*args,**clean_params)
    # rename the output from qac_clean1 so that the image is saved if the user saves it for other iterations
    os.system('mv %s/dirtymap.image %s/zero_dirtymap.image'%(args[0], args[0]))
    # remove the other output since it is not needed
    os.system('rm -fr %s/dirtymap.*'%(args[0]))
    # calculate scale factor  @todo   rms or sigma???
    sn_scale_factor = noise / imstat('%s/zero_dirtymap.image'%(args[0]))['rms'][0]     

    return sn_scale_factor

    #-end of qac_noise()

        
def qac_argv(sysargv):
    """
    Safe argument parser from CASA, removing the CASA dependant ones, including the script name
    
    If you call casa using "casa --nogui -c myscript.py arg1 arg2..."   this function will prepare
    a new sys.argv[] style list for you
    
    CASA5 and CASA6 differ in the way they re-populate sys.argv
       casa5:  ['casa', '-c', 'myscript.py', ...]
       casa6:  ['myscript.py', ...]
    
    Typical usage:

         import sys

         for arg in qac_argv(sys.argv):
             exec(arg)

    Alternative method in CASA6 might be to "import casashell"
    

    """
    #print("PJT: ",sysargv)
    if _is_casa6:
        if False:
            import casashell
            print("CASASHELL",casashell.argv)
        return sysargv[1:]
    else:
        return sysargv[3:]

def qac_initkeys(keys=None, argv=[]):
    QAC.keys = {"version" : _version}    
    if keys==None:
        return
    for k in keys.keys():
        QAC.keys[k] = keys[k]
    for kv in argv[3:]:
        i = kv.find('=')
        if i > 0:
            # @todo isn't there a better pythonic way to do this?
            cmd='QAC.keys["%s"]=%s' % (kv[:i], kv[i+1:])
            exec(cmd)
        
def qac_getkey(key=None):
    if key==None:
        return QAC.keys
    return QAC.keys[key]

    

def qac_begin(label="QAC", log=True, plot=False, local=False):
    """
    Every script should start with qac_begin() if you want to use the logger
    and/or Dtime output for performance checking.
    You can safely leave this call out, or set log=False

    label      prefix for Dtime labeling
    log        Use logger ?
    plot       if True, force plots to show up interactively.
    local      if a local tp2vis.py exists, execfile it  (does not work)

    See also qac_tag() and qac_end()
    """
    if local:
        if os.path.exists('tp2vis.py'):
            print("Reading a local tp2vis, which doesn't seem to work")
            execfile('tp2vis.py', globals())
            tp2vis_version()

    qac_initkeys()      # QAC.keys = {}
    
    if log:
        from utils import Dtime
        import logging
        # @todo until the logging + print problem solved, this is disabled
        logging.basicConfig(level = logging.INFO)
        root_logger = logging.getLogger()
        print('root_logger =', root_logger)
        print('handlers:', root_logger.handlers)
        handler = root_logger.handlers[0]
        print('handler stream:', handler.stream)
        print('sys.stderr:', sys.stderr)
        QAC.dt = Dtime.Dtime(label)

    print("CASA_logfile: %s" % casalog.logfile())

def qac_end():
    """
    Ending your QAC script.
    
    Stops logging and calls Dtime.end()
    
    See also qac_begin()
    """
    print("CASA_logfile: %s" % casalog.logfile())
    cmd = "pwd; cp %s ." % casalog.logfile()
    os.system(cmd)
    
    if QAC.hasdt():
        QAC.dt.tag("done")
        QAC.dt.end()
        
def qac_tag(label):
    """
    Create a time/memory tag for the logger using  Dtime.tag()
    Usually called by QAC routines, not by user scripts.
    
    See also qac_begin()
    """
    if QAC.hasdt(): 
        QAC.dt.tag(label)

# Now a convenience class to contain some static methods    

class QAC(object):
    """ Static class to hide some local helper functions

        rmcasa
        iscasa
        casa2np
        imsize2
        assertf
        maxofiles
        ...
    
    """
    @staticmethod
    def version():
        """ return version
        """
        return _version
    
    @staticmethod
    def plot(mode=None):
        """  set plot mode to interactive or not
        """
        return True
    
    @staticmethod
    def figsize(x=8,y=8):
        """  set plot figsize (in inches)
        """
        return (x,y)
    
    @staticmethod
    def hasdt():
        if dir(QAC).count('dt') == 0: return False
        return True

    @staticmethod
    def kwargs(**kwargs):
        """
        return the arguments of the caller as a dictionary for futher processing.
        The locals() function could also be used.
        
        Example of use:

        kw = my_kwargs(a=1, b='2', c='c')
        tclean(vis,**kw)
    """
        return kwargs
       
    @staticmethod
    def exists(filename = None):
        if filename == None:
            return False
        return os.path.exists(filename)
    
    @staticmethod
    def rmcasa(filename):
        if QAC.iscasa(filename):
            os.system('rm -rf %s' % filename)
        else:
            print("Warning: %s is not a CASA dataset" % filename)

    @staticmethod
    def iscasa(filename, casatype=None):
        """is a file a casa image
        
        casatype not implemented yet
        (why) isn't there a CASA function for this?
        
        Returns
        -------
        boolean
        """
        isdir = os.path.isdir(filename)
        if casatype == None:
            return isdir
        if not isdir:
            return False
        
        # ms + '/table.info' is an ascii file , first line should be
        # Type = Image
        # Type = Measurement Set
        ftype = open(filename + '/table.info','r').readlines()[0].strip().split()[-1]
        # print("casatype(%s)=%s" % (filename,ftype))

        return ftype == casatype

    @staticmethod    
    def casa2np(image, box=None, z=None):
        """
        convert a casa[x][y] to a numpy[y][x] such that fits writers
        will produce a fits file that looks like an RA-DEC image
        and also native matplotlib routines, such that imshow(origin='lower')
        will give the correct orientation.

        if image is a string, it's assumed to be the casa image name

        box    pixel list of [xmin,ymin, xmax, ymax]
        z      which plane to pick in case it's a cube (not implemented)
        """
        if type(image)==type(""):
            tb.open(image)
            d1 = tb.getcol("map").squeeze()            
            tb.close()
            return np.flipud(np.rot90(d1))
        return np.flipud(np.rot90(image))

    @staticmethod    
    def fits2np(image, box=None, z=None):
        """
        convert a casa[x][y] to a numpy[y][x] such that fits writers
        will produce a fits file that looks like an RA-DEC image
        and also native matplotlib routines, such that imshow(origin='lower')
        will give the correct orientation.

        if image is a string, it's assumed to be the casa image name

        box    pixel list of [xmin,ymin, xmax, ymax]
        z      which plane to pick in case it's a cube (not implemented)
        """
        if type(image)==type(""):
            hdu = fits.open(image)
            return hdu[0].data
        return np.flipud(np.rot90(image))

    @staticmethod    
    def imsize2(imsize):
        """ if scalar, convert to list, else just return the list
        """
        if type(imsize) == type([]):
            return imsize
        return [imsize,imsize]

    @staticmethod
    def iarray(array):
        """
        """
        return list(map(int,array.split(',')))

    @staticmethod
    def farray(array):
        """
        """
        return list(map(float,array.split(',')))
    
    @staticmethod
    def assertf(filename = None, debug=False):
        """ ensure a file or directory exists, else report and and fail
        """
        if filename == None: return
        if type(filename) == type([]):
            for f in filename:
                assert os.path.exists(f),  "QAC.assertf: %s does not exist" % f
                #print("Checking %s" % f)
        else:
            assert os.path.exists(filename),  "QAC.assertf: %s does not exist" % filename
            #print("Checking %s" % filename)
        return
    
    @staticmethod
    def label(idx,basename="%s"):
        """ helper function to create indexed filenames that tclean() produces, e.g.
            dirtymap.image, dirtyname_2.image, dirtymap_3.image
            are:
              "dirtymap%s.image" % QAC.label(idx)    where idx=[0,1,2]
            or
              QAC.label(idx,"dirtymap%s.image")      where idx=[0,1,2]
        
        """
        if idx==0:
            lab = ""
        else:
            lab = "_%d" % (idx+1)
        return basename % lab
    

    @staticmethod    
    def maxofiles(nofiles = None):
        """ Change the max number of open files, and return this.
            Some large mosaics may need this in some casa versions.
            If no argument is given, it will report the current max.
            See also casa.init.py
        """
        import resource
        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        if nofiles == None:
            print("Max open files set %d [hard=%d]" % (soft,hard))            
            return soft
        resource.setrlimit(resource.RLIMIT_NOFILE, (nofiles, hard))
        print("Changing max open files from %d to %d [hard=%d]" % (soft,nofiles,hard))
        return nofiles
     
    @staticmethod
    def select(thisone,sellist=[0],label=None):
        """
        Convenience method to ease selecting if an option (an integer) is selected
        Typical usage:
        
        if QAC.select(5,select,'Produce fig5.png with flux check'):
            qac_flux(....)
        
        thisone     the current one that needs to be checked
        sellist     list that user entered via command line, or 0 if always true
        label       If present, label is shows with a True/False on the selection
        
        """
        retval = False
        if type(sellist) != type([]): sellist = [sellist]
        if sellist[0]==0:
            retval = True
        elif thisone in sellist:
            retval = True
        else:
            retval = False
        if label != None:
            print("QAC.select %d %s %s" % (thisone,str(retval),label))
        return retval
        
    
#- end of qac.py
