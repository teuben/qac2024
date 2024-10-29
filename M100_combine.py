

# joint 7m+12m on trimmed data


# trimmed versions
vis12 = 'M100_aver_12.ms'
vis7  = 'M100_aver_7.ms'


# Concat and scale weights
os.system('rm -rf M100_combine_CO.ms')
concat(vis=[vis12, vis7],
       concatvis='M100_combine_CO.ms')



### Define clean parameters
vis='M100_combine_CO.ms'
prename='M100_combine_CO_cube'
imsize=800
cell='0.5arcsec'
minpb=0.2
restfreq='115.271201800GHz'
outframe='LSRK'
spw='0~2'
spw='0'
width='5km/s'
start='1400km/s'
nchan=70
robust=0.5
phasecenter='J2000 12h22m54.9 +15d49m15'

### Setup stopping criteria with multiplier for rms.
stop=3.


# Make Initial Dirty Image and Determine Synthesized Beam area



### Make initial dirty image
os.system('rm -rf '+prename+'_dirty.*')
tclean(vis=vis,
       imagename=prename + '_dirty',
       gridder='mosaic',
       deconvolver='hogbom',
       pbmask=minpb,
       imsize=imsize,
       cell=cell,
       spw=spw,
       weighting='briggsbwtaper',
       robust=robust,
       phasecenter=phasecenter,
       specmode='cube',
       width=width,
       start=start,
       nchan=nchan,
       restfreq=restfreq,
       outframe=outframe,
       veltype='radio',
       restoringbeam='common',
       mask='',
       niter=0,
       interactive=False)


# Find properties of the dirty image

### Find the peak in the dirty cube.
myimage=prename+'_dirty.image'
bigstat=imstat(imagename=myimage)
peak= bigstat['max'][0]
print('peak (Jy/beam) in cube = '+str(peak))   # 0.8418998718261719

# find the RMS of a line free channel (should be around 0.011
chanstat=imstat(imagename=myimage,chans='4')
rms1= chanstat['rms'][0]
chanstat=imstat(imagename=myimage,chans='66')
rms2= chanstat['rms'][0]
rms=0.5*(rms1+rms2)        

print('rms (Jy/beam) in a channel = '+str(rms))   # 0.01072584467430408





# Clean the Data


sidelobethresh = 2.0
noisethresh = 4.25
minbeamfrac = 0.3
lownoisethresh= 1.5
negativethresh = 0.0

os.system('rm -rf ' + prename + '.*')
tclean(vis=vis,
       imagename=prename,
       gridder='mosaic',
       deconvolver='hogbom',
       pbmask=minpb,
       imsize=imsize,
       cell=cell,
       spw=spw,
       weighting='briggsbwtaper',
       robust=robust,
       phasecenter=phasecenter,
       specmode='cube',
       width=width,
       start=start,
       nchan=nchan,
       restfreq=restfreq,
       outframe=outframe,
       veltype='radio',
       restoringbeam='common',
       mosweight=True,
       niter=10000,
       usemask='auto-multithresh',
       threshold=str(stop*rms)+'Jy/beam',
       sidelobethreshold=sidelobethresh,
       noisethreshold=noisethresh,
       lownoisethreshold=lownoisethresh, 
       minbeamfrac=minbeamfrac,
       growiterations=75,
       negativethreshold=negativethresh,
       interactive=False,
       pbcor=True)


# Moment Maps for 7m+12m CO (1-0) Cube


myimage='M100_combine_CO_cube.image'
chanstat=imstat(imagename=myimage,chans='4')
rms1= chanstat['rms'][0]
chanstat=imstat(imagename=myimage,chans='66')
rms2= chanstat['rms'][0]
rms=0.5*(rms1+rms2)
print('rms in a channel = '+str(rms))   # 0.01072584467430408



os.system('rm -rf M100_combine_CO_cube.image.mom0')
immoments(imagename = 'M100_combine_CO_cube.image',
         moments = [0],
         axis = 'spectral',chans = '9~61',
         mask='M100_combine_CO_cube.pb>0.3',
         includepix = [rms*2,100.],
         outfile = 'M100_combine_CO_cube.image.mom0')

os.system('rm -rf M100_combine_CO_cube.image.mom1')
immoments(imagename = 'M100_combine_CO_cube.image',
         moments = [1],
         axis = 'spectral',chans = '9~61',
         mask='M100_combine_CO_cube.pb>0.3',
         includepix = [rms*5.5,100.],
         outfile = 'M100_combine_CO_cube.image.mom1')





os.system('rm -rf M100_combine_CO_cube.pb.1ch')
imsubimage(imagename='M100_combine_CO_cube.pb',
           outfile='M100_combine_CO_cube.pb.1ch',
           chans='35')


os.system('rm -rf M100_combine_CO_cube.image.mom0.pbcor')
impbcor(imagename='M100_combine_CO_cube.image.mom0',
    pbimage='M100_combine_CO_cube.pb.1ch',
    outfile='M100_combine_CO_cube.image.mom0.pbcor')


exportfits(imagename='M100_combine_CO_cube.image',            fitsimage='M100_combine_CO_cube.image.fits',            overwrite=True)
exportfits(imagename='M100_combine_CO_cube.pb',               fitsimage='M100_combine_CO_cube.pb.fits',               overwrite=True)
exportfits(imagename='M100_combine_CO_cube.image.mom0',       fitsimage='M100_combine_CO_cube.image.mom0.fits',       overwrite=True)
exportfits(imagename='M100_combine_CO_cube.image.mom0.pbcor', fitsimage='M100_combine_CO_cube.image.mom0.pbcor.fits', overwrite=True)
exportfits(imagename='M100_combine_CO_cube.image.mom1',       fitsimage='M100_combine_CO_cube.image.mom1.fits',       overwrite=True)



## Feathering the Total Power and 7m+12m Interferometric Images

imhead('M100_TP_CO_cube.spw3.image.bl',mode='get',hdkey='restfreq')
imhead('M100_combine_CO_cube.image',mode='get',hdkey='restfreq')


os.system('rm -rf M100_TP_CO_cube.regrid')
imregrid(imagename='M100_TP_CO_cube.spw3.image.bl',
         template='M100_combine_CO_cube.image',
         axes=[0, 1],
         output='M100_TP_CO_cube.regrid')





os.system('rm -rf M100_TP_CO_cube.regrid.subim')
imsubimage(imagename='M100_TP_CO_cube.regrid',
           outfile='M100_TP_CO_cube.regrid.subim',
           box='219,148,612,579')
os.system('rm -rf M100_combine_CO_cube.image.subim')
imsubimage(imagename='M100_combine_CO_cube.image',
           outfile='M100_combine_CO_cube.image.subim',
           box='219,148,612,579')



os.system('rm -rf M100_combine_CO_cube.pb.subim')
imsubimage(imagename='M100_combine_CO_cube.pb',
           outfile='M100_combine_CO_cube.pb.subim',
           box='219,148,612,579')


os.system('rm -rf M100_TP_CO_cube.regrid.subim.depb')
immath(imagename=['M100_TP_CO_cube.regrid.subim',
                  'M100_combine_CO_cube.pb.subim'],
       expr='IM0*IM1',
       outfile='M100_TP_CO_cube.regrid.subim.depb')
#> WARN    ImageExprCalculator::compute






# Feather TP Cube with 7m+12m Cube


os.system('rm -rf M100_Feather_CO.image')
feather(imagename='M100_Feather_CO.image',
        highres='M100_combine_CO_cube.image.subim',
        lowres='M100_TP_CO_cube.regrid.subim.depb')



myimage = 'M100_TP_CO_cube.regrid.subim'
chanstat = imstat(imagename=myimage,chans='4')
rms1 = chanstat['rms'][0]
chanstat = imstat(imagename=myimage,chans='66')
rms2 = chanstat['rms'][0]
rms = 0.5*(rms1+rms2)     #  0.11425382981723972
 
os.system('rm -rf M100_TP_CO_cube.regrid.subim.mom0')
immoments(imagename='M100_TP_CO_cube.regrid.subim',
         moments=[0],
         axis='spectral',
         chans='10~61',
         includepix=[rms*2., 50],
         outfile='M100_TP_CO_cube.regrid.subim.mom0')
 
os.system('rm -rf M100_TP_CO_cube.regrid.subim.mom1')
immoments(imagename='M100_TP_CO_cube.regrid.subim',
         moments=[1],
         axis='spectral',
         chans='10~61',
         includepix=[rms*5.5, 50],
         outfile='M100_TP_CO_cube.regrid.subim.mom1')





myimage = 'M100_Feather_CO.image'
chanstat = imstat(imagename=myimage,chans='4')
rms1 = chanstat['rms'][0]
chanstat = imstat(imagename=myimage,chans='66')
rms2 = chanstat['rms'][0]
rms = 0.5*(rms1+rms2)  
 
os.system('rm -rf M100_Feather_CO.image.mom0')
immoments(imagename='M100_Feather_CO.image',
         moments=[0],
         axis='spectral',
         chans='10~61',
         includepix=[rms*2., 50],
         outfile='M100_Feather_CO.image.mom0')
 
os.system('rm -rf M100_Feather_CO.image.mom1')
immoments(imagename='M100_Feather_CO.image',
         moments=[1],
         axis='spectral',
         chans='10~61',
         includepix=[rms*5.5, 50],
         outfile='M100_Feather_CO.image.mom1')


 # Correct the Primary Beam Response

os.system('rm -rf M100_Feather_CO.image.pbcor')
immath(imagename=['M100_Feather_CO.image',
                  'M100_combine_CO_cube.pb.subim'],
       expr='IM0/IM1',
       outfile='M100_Feather_CO.image.pbcor')



os.system('rm -rf M100_combine_CO_cube.pb.1ch.subim')
imsubimage(imagename='M100_combine_CO_cube.pb.subim',
           outfile='M100_combine_CO_cube.pb.1ch.subim',
           chans='35')

os.system('rm -rf M100_Feather_CO.image.mom0.pbcor')
immath(imagename=['M100_Feather_CO.image.mom0',
                  'M100_combine_CO_cube.pb.1ch.subim'],
        expr='IM0/IM1',
        outfile='M100_Feather_CO.image.mom0.pbcor')



imstat('M100_combine_CO_cube.image.subim')

imstat('M100_TP_CO_cube.regrid.subim.depb')['flux']    # 2803.67209906
imstat('M100_Feather_CO.image')['flux']                # 2803.67074178]
imstat('M100_Feather_CO.image.pbcor')['flux']          # 3026.5187356







ia.open("M100_TP_CO_cube.spw3.image.bl") 

ib = iatool()
ib.open("M100_TP_CO_cube.spw3.image.bl")

# ensure target has no beam(s) at start, not always necessary
# but it doesn't hurt to do it.
ib.setrestoringbeam(remove=True)

# Now copy the beams. This only will work correctly if both images
# have the same number of channels. nchan is set to
# the number of channels 
for c in range(nchan):
   beam = ia.restoringbeam(channel=c)
   ib.setrestoringbeam(beam=beam, channel=c)

ia.done()
ib.done()

sdintimaging(usedata="sdint", sdimage="M100_TP_CO_cube.spw3.image.bl", 
            sdpsf="",sdgain=3.0, dishdia=12.0, vis="M100_combine_CO.ms", 
            imagename="try_sdint_niter5k", imsize=imsize, cell=cell, 
            phasecenter=phasecenter, stokes="I", 
            specmode="cube", reffreq="", nchan=nchan, 
            start=start, width=width, #"114732899312.0Hz", width="-1922516.74324Hz", 
            outframe=outframe, veltype="radio", restfreq=restfreq, 
            interpolation="linear", perchanweightdensity=True,  
            gridder="mosaic", mosweight=True, 
            pblimit=0.2, deconvolver="hogbom", scales=[0, 5, 10, 15, 20], 
            smallscalebias=0.0, pbcor=False, weighting="briggs", 
            robust=robust, niter=5000, gain=0.1, threshold=0.0, nsigma=3.0, 
            interactive=False, usemask="user", mask="", pbmask=0.3)
