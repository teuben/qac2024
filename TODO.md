# TODO's

As a result of the demos, we identified a few things to work on:

## bugs

- There are two sets of scripts:   the individual imaging scripts from the data-download links.Those are old and arguably should be removed or updated for casa6:

     - original **M100_Band3_12m_Imaging.py** was still in python2, and had a bad call to uvcontsub, where uvcontsub_old() would work  (API changed)
     - original **M100_Band3_7m_Imaging.py** was still in python2 - same

-  My dataset **M100_TP_CO_cube.spw3.image.bl** got corrupted with beams-per-plane, which threw off feather() on a second run
   of the combination casaguide.
   This apparently was done in preparating for sdintimaging !!!.  This caused a particularly difficult to parse error

              chan >=0 && chan < Int(nchan()) && stokes >= 0 && stokes < Int(nstokes()

   this only happens if you run the script a second time,as the TP data got "corrupted" with beams-per-plane.

   SHould add here that the slides did not add the per-plane-beams, but the casaguide did.


- .weight file also needs to be removed before tclean() - a repeat with a different nchan for example will cause failure - better is to remove
  all .* files before tclean() instead of the individual rmtables() used in the scripts




## some nuisances

- symlinks to calibrated data preferred over moving them
- immmoment doesn't have an overwrite=True and does not remove output
  files (all programs should have an overwrite=True option)
- 6.6.5 and qac.py might need astropy:   %pip install astropy
- WARN    task_tclean::SIImageStore::getPSFGaussian (file /source/casa6/casatools/src/code/synthesis/ImagerObjects/SIImageStore.cc, line 2075)    PSF is blank for[C69:P0]
    -  this is related to the trimmed data, which have issues related to a bug im imtrans()

