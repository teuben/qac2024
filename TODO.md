# todo's


- original M100_Band3_12m_Imaging.py was still in python2
- original M100_Band3_7m_Imaging.py was still in python2
- symlinks to calibrated data preferred over moving them
- immmoment doesn't have an overwrite=True and does not remove output files (all programs should have an overwrite=True option)
- WARN    task_tclean::SIImageStore::getPSFGaussian (file /source/casa6/casatools/src/code/synthesis/ImagerObjects/SIImageStore.cc, line 2075)    PSF is blank for[C69:P0] 
- feather assertion fails:   chan >=0 && chan < Int(nchan()) && stokes >= 0 && stokes < Int(nstokes()
- 6.6.5 and qac.py might need astropy:   %pip install astropy

- .weight file needs to be removed before tclean() - a repeat with a different nchan for example will cause failure

-  Somehow my  'M100_TP_CO_cube.spw3.image.bl' got corrupted with beams-per-plane, which threw off feather()
   this was done by script.py in preparating for sdintimaging !!!
