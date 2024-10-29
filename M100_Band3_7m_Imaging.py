# Imaging script for M100, 7m data
# Tested in CASA version 6.5.6


# From this point on you can proceed from M100_Band3_7m_CalibratedData.ms

#--------------------------------------------------------------------------------------#
#                             Imaging                                                  #
#--------------------------------------------------------------------------------------#

##################################################
# Check CASA version
version = casalith.version_string()
print("You are using " + version)
if (version < '6.5.0'):
    print("YOUR VERSION OF CASA IS TOO OLD FOR THIS GUIDE.")
    print("PLEASE UPDATE IT BEFORE PROCEEDING.")
else:
    print("Your version of CASA is appropriate for this guide.")

##################################################
# Identify Line-free SPWs and channels

finalvis='M100_Band3_7m_CalibratedData.ms' 

# Use plotms to identify line and continuum spectral windows
if False:
    plotms(vis=finalvis, xaxis='channel', yaxis='amplitude',
           ydatacolumn='data',
           avgtime='1e8', avgscan=True, avgchannel='1', 
           iteraxis='spw' )

##################################################
# Create an Averaged Continuum MS

# In this case, you just need to average dedicated continuum spws.

# Average channels within spws
contspws='0,1,2,4' # from plotms output
contvis='M100_7m_cont.ms'
os.system('rm -rf ' + contvis)
split(vis=finalvis,
      spw=contspws,
      outputvis=contvis,
      width=[4080,4080,4080,4080], # number of channels to average together. change to appropriate value for each spectral window.
      datacolumn='data')
#PJT: was running in parallel ?

# these observations contain continuum-only SPWs: 0,1,2,4 (line is in SPW 3,5)


#############################################
# Imaging the Continuuum

contimagename = 'M100_7m_cont'

for ext in ['.image','.mask','.model','.image.pbcor','.psf','.residual','.pb','.sumwt']:
    rmtables(contimagename+ext)

tclean(vis=contvis,
      imagename=contimagename,
      field='1~23', # science fields
      phasecenter='J2000 12h22m54.9 +15d49m15',     
      specmode='mfs',
      deconvolver='clark',
      imsize = [200,200], # size of image in pixels
      cell= '2.0arcsec', # cell size for imaging
      weighting = 'briggs', 
      robust = 0.5,
      niter = 1000, 
      threshold = '0.0mJy', 
      #interactive = True,
      gridder = 'mosaic',
      pbcor=True)

# some continuum emission detected at the center
# 15 iterations
# RMS ~ 0.3 mJy in a 14.03"x10.78" beam (7m)

########################################
# Continuum Subtraction for Line Imaging

fitspw = '0,1,2,3:300~1500;2500~3700,4,5:300~1500;2500~3700' # line-free channel for fitting continuum
linespw = '3,5' # line spectral windows.

uvcontsub_old(vis=finalvis,
          spw=linespw, # spw to do continuum subtraction on
          fitspw=fitspw, 
          combine='', 
          solint='int',
          fitorder=1,
          want_cont=False) # This value should not be changed.


##############################################
# Image line emission


linevis = finalvis+'.contsub'
linevis = finalvis
lineimagename = 'M100_7m_CO' # name of line image

# If you do not wish to use the provided mask, comment out the line: "mask=''"

for ext in ['.image','.mask','.model','.image.pbcor','.psf','.residual','.pb','.sumwt']:
    rmtables(lineimagename + ext)
# M100_12m_CO.weight

tclean(vis=linevis,
      imagename=lineimagename, 
      field='1~23', # science fields
      spw='0~1',
      phasecenter='J2000 12h22m54.9 +15d49m15',
      specmode='cube',
      start='1400km/s', # start velocity
      width='5km/s', # velocity width
      nchan=70, 
      outframe='LSRK', # velocity reference frame 
      veltype='radio', # velocity type
      restfreq='115.271201800GHz', # rest frequency of primary line 
      niter=10000,  
      threshold='0.05Jy', 
      #interactive=True,
      cell='2.0arcsec', # cell size for imaging
      imsize= [200,200], 
      weighting='briggs', 
      robust=0.5,
      gridder='mosaic',
      #mask='M100_7m_CO_demo.mask',
      pbcor=True)

# M100_7m_CO.image (and other files) created -- use .mask file to reproduce my masking by hand
# beam: 13.08" by 10.16"
# rms in line free channel (width 5 km/s): 28 mJy/beam

##############################################
# Make moment maps of the CO(1-0) emission 

cmd='rm -rf  M100_7m_CO.image*mom*'
os.system(cmd)

immoments(imagename = 'M100_7m_CO.image',
         moments = [0],
         axis = 'spectral',chans = '9~60',
         includepix = [0.056,100.], # rms*2
         outfile = 'M100_7m_CO.image.mom0')

immoments(imagename = 'M100_7m_CO.image',
         moments = [1],
         axis = 'spectral',chans = '9~60',
         includepix = [0.14,100.], # rms*5
         outfile = 'M100_7m_CO.image.mom1')

immoments(imagename = 'M100_7m_CO.image.pbcor', 
         moments = [0], 
         axis = 'spectral',chans = '9~60', 
         includepix = [0.056,100.], 
         outfile = 'M100_7m_CO.image.pbcor.mom0')


##############################################
# Export the images

exportfits(imagename='M100_7m_CO.image',            fitsimage='M100_7m_CO.image.fits',                overwrite=True)
exportfits(imagename='M100_7m_CO.pb',               fitsimage='M100_7m_CO.pb.fits',                   overwrite=True)
exportfits(imagename='M100_7m_CO.image.pbcor',      fitsimage='M100_7m_CO.image.pbcor.fits',          overwrite=True)
exportfits(imagename='M100_7m_CO.image.mom0',       fitsimage='M100_7m_CO.image.mom0.fits',           overwrite=True)
exportfits(imagename='M100_7m_CO.image.pbcor.mom0', fitsimage='M100_7m_CO.image.mom0.pbcor.fits',     overwrite=True)
exportfits(imagename='M100_7m_CO.image.mom1',       fitsimage='M100_7m_CO.image.mom1.fits',           overwrite=True)
