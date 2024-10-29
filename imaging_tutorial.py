# DO NOT RUN THIS AS A SCRIPT ITSELF. The following are commands for CASA, not for Python.


listobs(vis='twhya_calibrated.ms')


listobs(vis='twhya_calibrated.ms',listfile='twhya_listobs.txt')


plotms(vis='twhya_calibrated.ms', xaxis='u', yaxis='v', avgchannel='10000', avgspw=False, avgtime='1e9', avgscan=False, coloraxis='field', showgui=True)


plotms(vis='twhya_calibrated.ms', xaxis='UVwave', yaxis='Amp', avgchannel='10000', avgspw=False, avgtime='1e9', avgscan=False,field='2', coloraxis='antenna1', showgui=True)


# do this only if you have existing old files to delete
#os.system('rm -rf phase_cal.*')  


tclean(vis='twhya_calibrated.ms', imagename='phase_cal', 
field='3', 
spw='', 
specmode='mfs', 
deconvolver='hogbom', 
gridder='standard', 
imsize=[250,250],
cell=['0.1arcsec'], 
weighting='briggs', 
threshold='0.0mJy', 
interactive=True)


# Remove the generated files since we did not do any cleaning using the previous tclean command
os.system('rm -rf phase_cal.*')


tclean(vis='twhya_calibrated.ms', imagename='phase_cal', 
field='3',
spw='',
specmode='mfs',
deconvolver='hogbom', 
gridder='standard', 
imsize=[250,250],
cell=['0.1arcsec'], 
weighting='briggs', 
threshold='0.0mJy', 
niter=5000,
interactive=True)


# do this only if you have existing old files to delete
#os.system('rm -rf twhya_smoothed.ms')


split(vis='twhya_calibrated.ms', field='5', width='8', outputvis='twhya_smoothed.ms', datacolumn='data')


# do this only if you have existing old files to delete
#os.system('rm -rf twhya_cont.*')


tclean(vis='twhya_smoothed.ms',
imagename='twhya_cont',
field='0', spw='', specmode='mfs',
gridder='standard',
deconvolver='hogbom',
imsize=[250,250],
cell=['0.1arcsec'],
weighting='briggs',
robust=0.5, threshold='0mJy',
niter=5000,
interactive=True)


# do this only if you have existing old files to delete
#os.system('rm -rf twhya_cont.pbcor.image')

impbcor(imagename='twhya_cont.image',
pbimage='twhya_cont.pb',
outfile='twhya_cont.pbcor.image')


# Spectral line imaging (not covered in this workshop)

plotms(vis='twhya_selfcal.ms',
       xaxis='channel',
       yaxis='amp',
       field='5',
       avgspw=False,
       avgtime='1e9',
       avgscan=True,
       avgbaseline=True, 
       showgui = True)

# do this only if you have existing old files to delete
#os.system('rm -rf twhya_selfcal.ms.contsub')

uvcontsub(vis = 'twhya_selfcal.ms',
          field = '5',
          fitspec = '0:0~239;281~383',
          fitorder = 0,
          outputvis='twhya_selfcal.ms.contsub')


plotms(vis='twhya_selfcal.ms.contsub',
       xaxis='channel',
       yaxis='amp',
       field='5',
       avgspw=False,
       avgtime='1e9',
       avgscan=True,
       avgbaseline=True, 
       showgui = True)


restfreq = '372.67249GHz'

# do this only if you have existing old files to delete
#os.system('rm -rf twhya_n2hp.*')

tclean(vis = 'twhya_selfcal.ms.contsub',
       imagename = 'twhya_n2hp',
       field = '5',
       spw = '0',
       specmode = 'cube',
       perchanweightdensity=True,
       nchan = 15,
       start = '0.0km/s',
       width = '0.5km/s',
       outframe = 'LSRK',
       restfreq = restfreq,
       deconvolver= 'hogbom',
       gridder = 'standard',
       imsize = [250, 250],
       cell = '0.1arcsec',
       weighting = 'briggsbwtaper',
       robust = 0.5,
       restoringbeam='common',
       interactive = True,
       niter=5000)


# do this only if you have existing old files to delete
#os.system('rm -rf twhya_n2hp.pbcor.image')

impbcor(imagename='twhya_n2hp.image',
pbimage='twhya_n2hp.pb',
outfile='twhya_n2hp.pbcor.image')



