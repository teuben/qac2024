# Imaging script for M100, 7m data (trimmed qac2024 data)
# Tested in CASA version 6.5.6
# wall clock:  ~3min 15 s  (all cores)
#               1min 1s    (1 core)

#--------------------------------------------------------------------------------------#
#                             Imaging                                                  #
#--------------------------------------------------------------------------------------#

finalvis = 'M100_Band3_7m_CalibratedData.ms'          # 11 GB
linevis  = 'M100_aver_7.ms'                           # 25 MB

lineimagename = 'M100_7m_CO' # name of line image

# If you do not wish to use the provided mask, comment out the line: "mask=''"

for ext in ['.image','.mask','.model','.image.pbcor','.psf','.residual','.pb','.sumwt']:
    rmtables(lineimagename + ext)

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
# Export the images to fits

exportfits(imagename='M100_7m_CO.image',            fitsimage='M100_7m_CO.image.fits',            overwrite=True)
exportfits(imagename='M100_7m_CO.pb',               fitsimage='M100_7m_CO.pb.fits',               overwrite=True)
exportfits(imagename='M100_7m_CO.image.pbcor',      fitsimage='M100_7m_CO.image.pbcor.fits',      overwrite=True)
exportfits(imagename='M100_7m_CO.image.mom0',       fitsimage='M100_7m_CO.image.mom0.fits',       overwrite=True)
exportfits(imagename='M100_7m_CO.image.pbcor.mom0', fitsimage='M100_7m_CO.image.mom0.pbcor.fits', overwrite=True)
exportfits(imagename='M100_7m_CO.image.mom1',       fitsimage='M100_7m_CO.image.mom1.fits',       overwrite=True)

# QAC stats
cubename = 'M100_7m_CO.image.fits'
expected = "0.00658316147132589 0.07530835419854627 -0.2958295941352844 2.587661027908325 1079.1434685780266 0.20917498"
expected = "0.006583161471325896 0.07530835419854684 -0.2958295941352844 2.587661027908325 1079.1434685780266 0.20917498 OMT=1"
qac_stats(cubename)
print(f"QAC_STATS: {cubename} {expected} [EXPECTED]")
