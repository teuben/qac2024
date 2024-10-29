# Quick Array Combinations 2024 (qac2024)

Additional notes and script for the ALMA array combinations for the Data Reduction Workshop (29-oct-2024). This link will
be available on  https://github.com/teuben/qac2024 - please reload/pull this regularly for timely updates.



##  Program overview:

Original link: https://science.nrao.edu/facilities/alma/facilities/alma/naasc-workshops/nrao-dr-umd24

Zoom link: https://umd.zoom.us/j/99368489955?pwd=XLKs8w2i87PAAkb0QKOQ6b6gTcfZL3.1

*    10:30 - 10:40  Welcome coffee & event logistics
*    10:40 - 11:40  ALMA Overview and Interferometry Basics (Eltha Teng)
*    11:40 - 12:00  Science Talk (Keaton Donaghue): "Enshrouded in Dust: Using ALMA to Probe the Embedded Super Star Clusters in NGC 253"
*    12:00 - 13:00  Lunch (provided for in-person attendees)
*    13:00 - 13:30  Verifying data, scripts, and using CASA and CARTA
*    13:30 - 14:30  Tutorial: continuum imaging and self-calibration with CASA (Eltha Teng)
*    14:30 - 14:50  Short break
*    14:50 - 16:20  Tutorial: imaging array combination with feathering and advanced methods (Peter Teuben)
*    16:20 - 16:45  Tutorial: data visualization with CARTA (Eltha & Peter)
*    16:45 - 17:00  Wrap-up & survey: https://naasc.typeform.com/to/r6wNKWpk#workshop=umd



## 1. Installing

### 1.1 CASA

See  https://casa.nrao.edu/casa_obtaining.shtml how to obtain **casa**

Some example links:


2. https://casa.nrao.edu/download/distro/casa/release/rhel/casa-6.6.5-31-py3.10.el8.tar.xz
3. https://alma-dl.mtk.nao.ac.jp/ftp/casa/distro/casa/release/rhel/casa-6.5.6-22-py3.8.el8.tar.xz


Although 6.6.5 is available, current examples have only been verified for 6.5.6 (Peter)

Download, extract, and run. Here's an example for linux:

      tar xf casa-6.5.6-22-py3.8.el8.tar.xz
      casa-6.6.5-31-py3.10.el8/bin/casa

if you an error about missing data, create this directory, and start casa again. This is likely to happen
if you're never run CASA.

      mkdir $HOME/.casa/data

### 1.2 CARTA

For ubuntu, **carta** is now available as a standard package

      sudo apt install carta

otherwise head over to https://cartavis.org to download your favorite version of CARTA.

      wget https://github.com/CARTAvis/carta/releases/latest/download/carta.AppImage.x86_64.tgz


### 1.3 Analysis Scripts

Some of the demos need you to install a plugin for CASA, called analysis script. I normally
put them in the **~/.casa** directory, e.g.

      cd ~/.casa
      wget ftp://ftp.cv.nrao.edu/pub/casaguides/analysis_scripts.tar
      tar xf analysis_scripts.tar

and add the plugin to your **~/.casa/startup.py** file:

      import sys
      sys.path.append("/home/teuben/.casa/analysis_scripts")
      import analysisUtils as au

for a more portable version, one can use

      import sys, os
      sys.path.append("%s/.casa/analysis_scripts" % os.environ["HOME"])
      import analysisUtils as au

###  1.4 Converting CASA format to FITS

      casa-6.6.5-31-py3.10.el8/bin/casa
      CASA <1> exportfits('demo/M100_combine12+7_CO_cube.image','M100-demo.fits')
      CASA <2> exit

      $ ds9 M100-demo.fits
      $ carta M100-demo.fits

      #      for very large cubes, conversion can be useful to speed up CARTA
      $ fits2idia [-o M100-demo.hdf5] M100-demo.fits
      $ carta M100-demo.fits

### 1.5 Running CARTA on remote machines

For large computations your laptop may not efficiently be able to display the data. Of course you can copy
them to your laptop, but with CARTA , much like jupyter notebooks, there's now a way to remotely compute and
locally display using your browser.  You will need to use an ssh port forwarding technique for this.

      remote% carta M100_demo.fits --no_browser
      # copy and paste the URL with the token on your local machine
      xdg-open http://129.2.14.56:3002/?token=4fff9b36-1925-4fbb-928f-a609a114a35f


if this doesn't work, perhaps the port is being blocked, and you might be able to use ssh port forwarding, e.g.

      xxx% PORT=3333 && ssh -L ${PORT}:localhost:${PORT} <user>@<server> carta --host=localhost --port=${PORT} --no_browser

Compare this to a similar way how remote jupyter notebooks can be run:


       # login on the remote
       local% ssh user@remote

       # set up your python environment on the remote, YMMV
       remote% source anaconda3/python_start.sh

       # start up a notebook without local browser, but pick a free port number
       # watch the URL to be loaded later
       remote% jupyter notebook --no-browser --port=8086

       # set up port forwarding between laptop and remote, this will leave an open shell on remote
       local% ssh -L 8086:localhost:8086 user@remote
       local%

       # 
       local%  xdg-open http://localhost:8086/tree?token=blablablabla


### 1.6 Speeding up CASA?

Python's Global Interpreter Lock (GIL) can pay havoc on casa's runtime.  The 7m imaging script took 3 mins on my laptop,
where if using 1 processorm it ran in 1 min.  The 12m imaging not as fast a speedup:   9.5 mins to 6 mins.`

Here is how you can force casa to run with 1 processor

      OMP_NUM_THREADS=1 casa-6.6.5-31-py3.10.el8/bin/casa


### 1.7 Sample CASA guides

0. https://almascience.nrao.edu/alma-data/science-verification   (TW Hyd is #1 on the list, M100 is #4 on the list)
1. https://casaguides.nrao.edu/index.php?title=TWHydraBand7
1. https://casaguides.nrao.edu/index.php/M100_Band3
2. https://casaguides.nrao.edu/index.php/M100_Band3_Combine
3. https://casaguides.nrao.edu/index.php/M100_Band3_SingleDish


Note currently the Combine and SingleDish casaguides point to casa version 6.5.4 (Fall 2024), even though the latest version is 6.6.5

## 2. Data


### 2.1 TW Hyd

For TW-Hya, we need the calibrated measurement set (twhya_calibrated.ms).

    1. https://bulk.cv.nrao.edu/almadata/sciver/TWHya/TWHYA_BAND7_CalibratedData.tgz    5.7 GB
    2. https://bulk.cv.nrao.edu/almadata/sciver/TWHya/TWHYA_BAND7_ReferenceImages.tgz   8.5 MB

0. TW-Hya data:  https://bulk.cv.nrao.edu/almadata/public/ALMA_firstlooks/twhya_firstlook.tgz

1. Extract the needed files:   
```
   tar -xvzf twhya_firstlook.tgz
   tar -xvf twhya_calibrated.ms.tar
```

2. Download the text files:
```   
   1. https://github.com/teuben/qac2024/blob/main/imaging_tutorial.py
   2. https://github.com/teuben/qac2024/blob/main/selfcal_tutorial.py
```


### 2.2 M100

For M100 We will need 12m, 7m, and TP data. 


1. M100 12m data: http://almascience.org/almadata/sciver/M100Band3_12m

   1. https://bulk.cv.nrao.edu/almadata/sciver/M100Band3_12m/M100_Band3_12m_CalibratedData.tgz    15GB  ***
   2. https://bulk.cv.nrao.edu/almadata/sciver/M100Band3_12m/M100_Band3_12m_Imaging.py
   
            M100_Band3_12m_CalibratedData.ms
            M100_12m_CO_demo.mask
            M100_Band3_12m_Imaging.py   (should produce M100_Band3_12m_ReferenceImages.tgz = 297M)
	 
2. M100 7m & TP data: http://almascience.org/almadata/sciver/M100Band3ACA

       https://bulk.cv.nrao.edu/almadata/sciver/M100Band3ACA/M100_Band3_7m_CalibratedData.tgz            - 9.1G ***
       https://bulk.cv.nrao.edu/almadata/sciver/M100Band3ACA/M100_Band3_7m_Imaging.py                    - still python2
       https://bulk.cv.nrao.edu/almadata/sciver/M100Band3ACA/M100_Band3_TP_CalibratedData_5.1.tgz        - 13G   --no--
       https://bulk.cv.nrao.edu/almadata/sciver/M100Band3ACA/M100_Band3_DataComb_ReferenceImages_5.1.tgz - 393M
       https://bulk.cv.nrao.edu/almadata/sciver/M100Band3ACA/M100_Band3_ACA_ReferenceImages_5.1.tgz      - 24M


3. M100 Combo Tutorial:  https://bulk.cv.nrao.edu/almadata/public/combo_tutorial

       M100_combine12+7_CO_cube.image.tgz
       script.py


### 2.2 Data Symlinks:

As mentioned, the tgz files dump their (calibrated) data in subdirectories. To avoid confusion I decided to use
symlinks to these places, instead of moving them. So we would have:


      ln -s M100_Band3_12m_CalibratedData/M100_Band3_12m_CalibratedData.ms/
      ln -s M100_Band3_7m_CalibratedData/M100_Band3_7m_CalibratedData.ms
      ln -s M100_Band3_ACA_ReferenceImages_5.1/M100_TP_CO_cube.spw3.image.bl

### 2.3 Quick Data

The data for M100 are huge!  We have compiled a dataset with trimmed down data
for the 12m and 7m with just 70 x 5km/s channels to combine the data much
quicker.

To be confirmed if these still work, but this will be the link:

      wget https://www.astro.umd.edu/~teuben/QAC/qac_bench5.tar.gz
      tar zxf qac_bench5.tar.gz
      
      OMP_NUM_THREADS=1 casa-6.6.5-31-py3.10.el8/bin/casa
      execfile("qac.py")
      %time execfile("M100_Band3_7m_Imaging_trimmed.py")

this took 1 minute on my laptop, and 3 minutes if the OMP setting was ignored and the
code ran across all my cores.


# References

## Links


1. CASA: https://casa.nrao.edu/casa_obtaining.shtml
1. Analysis Scripts: ftp://ftp.cv.nrao.edu/pub/casaguides/analysis_scripts.tar
2. CARTA: https://cartavis.org/
3. DataComb: https://github.com/teuben/DataComb 
4. QAC: https://github.com/teuben/QAC 
5. Phangs: https://github.com/akleroy/phangs_imaging_scripts
6. CASA-Guides-Script-Extractor: https://github.com/CasaGuides/CASA-Guides-Script-Extractor

## Papers

* [Ekers and Rots 1979](https://ui.adsabs.harvard.edu/abs/1979ASSL...76...61E) - Short Spacing Synthesis from a Primary Beam Scanned Interferometer 
* [Vogel et al. 1984](https://ui.adsabs.harvard.edu/abs/1984ApJ...283..655V) - Interaction of the outflow and quiescent gas in Orion : HCO+ aperture synthesis maps. 
* [Braun and Walterbos 1985](https://ui.adsabs.harvard.edu/abs/1985A%26A...143..307B) - A solution to the short spacing problem in radio interferometry. 
* [Jorsater and van Moorsel 1995](https://ui.adsabs.harvard.edu/abs/1995AJ....110.2037J) - High Resolution Neutral Hydrogen Observations of the Barred Spiral Galaxy NGC 1365 
* [Kurono, Morita, Kamazaki 2009](https://ui.adsabs.harvard.edu/abs/2009PASJ...61..873K) - A Study of Combining Technique of Single-Dish and Interferometer Data: Imaging Simulations and Analysis 
* [Koda et al. 2011](https://ui.adsabs.harvard.edu/abs/2011ApJS..193...19K) = CO(J = 1-0) Imaging of M51 with CARMA and the Nobeyama 45 m Telescope 
* [Cotton 2017](https://ui.adsabs.harvard.edu/abs/2017PASP..129i4501C/) - Fourier Plane Image Combination by Feathering
* [Hoffman & Kepley 2018](https://library.nrao.edu/public/memos/gbt/GBT_300.pdf) - Correcting ALMA 12-m Array Data for Missing Short Spacings Using the Green Bank Telescope
* [Koda et al. 2019](https://ui.adsabs.harvard.edu/abs/2019PASP..131e4505K) - Total Power Map to Visibilities (TP2VIS): Joint Deconvolution of ALMA 12m, 7m, and Total Power Array Data 
* [Rau et al. 2019](https://ui.adsabs.harvard.edu/abs/2019AJ....158....3R) -A Joint Deconvolution Algorithm to Combine Single-dish and Interferometer Data for Wideband Multiterm and Mosaic Imaging
* [Mason 2020](https://arxiv.org/abs/2006.06549) - Imaging Spatially Extended Objects with Interferometers: Mosaicking and the Short Spacing Correction
* [Miyoshi et al. 2024](https://arxiv.org/pdf/2410.19267) - An Independent Hybrid Imaging of Sgr A∗ from the Data in EHT 2017 Observations
