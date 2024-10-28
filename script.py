#commands pulled from https://casaguides.nrao.edu/index.php/M100_Band3_Combine_6.5.4

os.system('rm -rf M100_*m.ms.listobs')
listobs('M100_Band3_12m_CalibratedData.ms',listfile='M100_12m.ms.listobs')
listobs('M100_Band3_7m_CalibratedData.ms',listfile='M100_7m.ms.listobs')


os.system('rm -rf M100_12m_CO.ms')
split(vis='M100_Band3_12m_CalibratedData.ms',
      outputvis='M100_12m_CO.ms',spw='0',field='M100',
      datacolumn='data',keepflags=False)
os.system('rm -rf M100_7m_CO.ms')
split(vis='M100_Band3_7m_CalibratedData.ms',
      outputvis='M100_7m_CO.ms',spw='3,5',field='M100',
      datacolumn='data',keepflags=False)


os.system('rm -rf M100_combine_CO.ms')
concat(vis=['M100_12m_CO.ms','M100_7m_CO.ms'],
       concatvis='M100_combine_CO.ms')

os.system('rm -rf ' + 'M100_combine12+7_CO_cube' + '.*')
tclean(vis='M100_combine_CO.ms',
    imagename='M100_combine12+7_CO_cube',
    gridder='mosaic',
    pbmask=0.2,
    imsize=800,
    cell='0.5arcsec',
    weighting='briggsbwtaper',
    robust=0.5,
    phasecenter='J2000 12h22m54.9 +15d49m15',
    specmode='cube',
    width='5km/s',
    start='1400km/s',
    nchan=70,
    restfreq='115.271201800GHz',
    outframe='LSRK',
    restoringbeam='common',
    mosweight=True,
    niter=10000,
    threshold='0.03mJy',
    usemask='auto-multithresh',
    sidelobethreshold=2.0,
    noisethreshold=4.25,
    minbeamfrac=0.3,
    lownoisethreshold=1.5,
    negativethreshold=0.0,
    growiterations=75,
    interactive=False,
    pbcor=True)

imhead('M100_TP_CO_cube.spw3.image.bl',mode='get',hdkey='restfreq')
imhead('M100_combine12+7_CO_cube.image',mode='get',hdkey='restfreq')

os.system('rm -rf M100_TP_CO_cube.regrid')
imregrid(imagename='M100_TP_CO_cube.spw3.image.bl',
         template='M100_combine12+7_CO_cube.image',
         axes=[0, 1],
         output='M100_TP_CO_cube.regrid')

os.system('rm -rf M100_TP_CO_cube.regrid.subim')
imsubimage(imagename='M100_TP_CO_cube.regrid',
           outfile='M100_TP_CO_cube.regrid.subim',
           box='219,148,612,579')
os.system('rm -rf M100_combine12+7_CO_cube.image.subim')
imsubimage(imagename='M100_combine12+7_CO_cube.image',
           outfile='M100_combine12+7_CO_cube.image.subim',
           box='219,148,612,579')

os.system('rm -rf M100_combine12+7_CO_cube.pb.subim')
imsubimage(imagename='M100_combine12+7_CO_cube.pb',
           outfile='M100_combine12+7_CO_cube.pb.subim',
           box='219,148,612,579')

os.system('rm -rf M100_TP_CO_cube.regrid.subim.depb')
immath(imagename=['M100_TP_CO_cube.regrid.subim',
                  'M100_combine12+7_CO_cube.pb.subim'],
       expr='IM0*IM1',
       outfile='M100_TP_CO_cube.regrid.subim.depb')

os.system('rm -rf M100_Feather_CO.image')
feather(imagename='M100_Feather_CO.image',
        highres='M100_combine12+7_CO_cube.image.subim',
        lowres='M100_TP_CO_cube.regrid.subim.depb')

#make moment maps of feathered images
myimage = 'M100_TP_CO_cube.regrid.subim'
chanstat = imstat(imagename=myimage,chans='4')
rms1 = chanstat['rms'][0]
chanstat = imstat(imagename=myimage,chans='66')
rms2 = chanstat['rms'][0]
rms = 0.5*(rms1+rms2)  
 
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

