## The following are CASA commands instead of a python script

# Start by creating your comparison image.  This is just a normally cleaned image using the data that is not self calibrated.
tclean(vis='twhya_calibrated.ms',
    imagename='before_selfcal',
    field='5',
    spw='',
    specmode='mfs',
    deconvolver='hogbom',
    nterms=1,
    gridder='standard',
    imsize=[250,250],
    cell=['0.1arcsec'],
    weighting='natural',
    threshold='0mJy',
    niter=5000,
    interactive=True)

# Next, use tclean to create your model for your source. 
tclean(vis='twhya_calibrated.ms',
    imagename='first_image',
    field='5',
    spw='',
    specmode='mfs',
    deconvolver='hogbom',
    nterms=1,
    gridder='standard',
    imsize=[250,250],
    cell=['0.1arcsec'],
    weighting='natural',
    threshold='0mJy',
    niter=5000,
    interactive=True,    
    savemodel='modelcolumn')

# Determine gain solutions based off of your model.  Make sure to set your solint appropriatly
gaincal(vis="twhya_calibrated.ms",
    caltable="phase.cal",
    field="5",
    solint="inf",
    calmode="p",
    refant="DV22",
    gaintype="G")

# Apply your solutions
applycal(vis="twhya_calibrated.ms",
    field="5",
    gaintable=["phase.cal"],
    interp="linear")

# Create another image to compare to your original to evaluate the self-calibration.
tclean(vis='twhya_calibrated.ms',
    imagename='after_self_cal',
    datacolumn='corrected',
    field='5',
    spw='',
    specmode='mfs',
    deconvolver='hogbom',
    nterms=1,
    gridder='standard',
    imsize=[250,250],
    cell=['0.1arcsec'],
    weighting='natural',
    threshold='0mJy',
    interactive=True,
    niter=5000)
