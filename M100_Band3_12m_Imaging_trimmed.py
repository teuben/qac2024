# Imaging script for M100, 12m data  (trimmed qac2024 data)
# Tested in CASA version 6.5.6
# wall clock:  ~9min 3s   (all cores)
#               6min 32s  (1 core)

#--------------------------------------------------------------------------------------#
#                             Imaging                                                  #
#--------------------------------------------------------------------------------------#

finalvis = 'M100_Band3_12m_CalibratedData.ms'       # 16 GB
linevis  = 'M100_aver_12.ms'                        # 91 MB

lineimagename = 'M100_12m_CO' # name of line image

# If you do not wish to use the provided mask, comment out the line: "mask=''"

for ext in ['.image','.mask','.model','.image.pbcor','.psf','.residual','.pb','.sumwt']:
    rmtables(lineimagename + ext)

tclean(vis=linevis,
      imagename=lineimagename, 
      field='1~47', # science fields
      spw='0',
      phasecenter='J2000 12h22m54.9 +15d49m15',        
      specmode='cube',
      start='1400km/s', # start velocity
      width='5km/s', # velocity width
      nchan= 70,  # number of channels
      outframe='LSRK', # velocity reference frame
      veltype='radio', # velocity type
      restfreq='115.271201800GHz', # rest frequency of primary line of interest
      niter=10000,  
      threshold='0.015Jy', 
      #interactive=True,
      cell='0.5arcsec',
      imsize=800, 
      weighting='briggs', 
      robust=0.5,
      gridder ='mosaic',
      #mask='M100_12m_CO_demo.mask',
      pbcor = True)


# M100_12m_CO.image (and other files) created -- use .mask file to reproduce my masking by hand
# beam: 3.43" by 2.39"
# rms in line free channel (width 5 km/s): 11-12 mJy/beam

##############################################
# Make moment maps of the CO(1-0) emission

cmd='rm -rf  M100_12m_CO.image*mom*'
os.system(cmd)

immoments(imagename = 'M100_12m_CO.image',
          moments = [0],
          axis = 'spectral',chans = '9~60',
          includepix = [0.02,100.],
          outfile = 'M100_12m_CO.image.mom0')

immoments(imagename = 'M100_12m_CO.image',
          moments = [1],
          axis = 'spectral',chans = '9~60',
          includepix = [0.05,100.],
          outfile = 'M100_12m_CO.image.mom1')

immoments(imagename = 'M100_12m_CO.image.pbcor',
          moments = [0],
          axis = 'spectral',chans = '9~60',
          includepix = [0.02,100.],
          outfile = 'M100_12m_CO.image.pbcor.mom0')


##############################################
# Export the images to fits

exportfits(imagename='M100_12m_CO.image',            fitsimage='M100_12m_CO.image.fits',            overwrite=True)
exportfits(imagename='M100_12m_CO.pb',               fitsimage='M100_12m_CO.pb.fits',               overwrite=True)
exportfits(imagename='M100_12m_CO.image.pbcor',      fitsimage='M100_12m_CO.image.pbcor.fits',      overwrite=True)
exportfits(imagename='M100_12m_CO.image.mom0',       fitsimage='M100_12m_CO.image.mom0.fits',       overwrite=True)
exportfits(imagename='M100_12m_CO.image.pbcor.mom0', fitsimage='M100_12m_CO.image.mom0.pbcor.fits', overwrite=True)
exportfits(imagename='M100_12m_CO.image.mom1',       fitsimage='M100_12m_CO.image.mom1.fits',       overwrite=True)

# QAC stats
cubename = 'M100_12m_CO.image.fits'
expected = "0.00046897872756007945 0.015443754289710123 -0.09721964597702026 0.6331420540809631 799.0091597811446 0.045486018"   # all cores
expected = "0.0004689787275600808 0.015443754289709948 -0.09721964597702026 0.6331420540809631 799.0091597811446 0.045486018 OMT=1"  
qac_stats(cubename)
print(f"QAC_STATS: {cubename} {expected} [EXPECTED]")

