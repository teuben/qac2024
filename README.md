# Quick Array Combinations 2024 (qac2024)

Notes on ALMA array combinations for the Data Reduction Workshop (29-oct-2024)

Original link: https://science.nrao.edu/facilities/alma/facilities/alma/naasc-workshops/nrao-dr-umd24

Program overview:


*    10:30 - 10:40  Welcome coffee & event logistics
*    10:40 - 11:40  ALMA Overview and Interferometry Basics (Eltha Teng)
*    11:40 - 12:00  Science Talk (Keaton Donaghue): "Enshrouded in Dust: Using ALMA to Probe the Embedded Super Star Clusters in NGC 253"
*    12:00 - 13:00  Lunch (provided for in-person attendees)
*    13:00 - 13:30  Verifying data, scripts, and using CASA and CARTA
*    13:30 - 14:30  Tutorial: continuum imaging and self-calibration with CASA (Eltha Teng)
*    14:30 - 14:50  Short break
*    14:50 - 16:20  Tutorial: imaging array combination with feathering and advanced methods (Peter Teuben)
*    16:20 - 16:45  Tutorial: data visualization with CARTA (Eltha & Peter)
*    16:45 - 17:00  Wrap-up & survey



## Installing

### CASA

example links

1. https://casa.nrao.edu/casa_obtaining.shtml
2. https://casa.nrao.edu/download/distro/casa/release/rhel/casa-6.6.5-31-py3.10.el8.tar.xz
3. https://alma-dl.mtk.nao.ac.jp/ftp/casa/distro/casa/release/rhel/casa-6.5.6-22-py3.8.el8.tar.xz


Although 6.6.5 is available, current examples have only been verified for 6.5.6

Download, extract, and run:

      tar xf casa-6.5.6-22-py3.8.el8.tar.xz
      casa-6.6.5-31-py3.10.el8/bin/casa

### CARTA

For ubuntu, carta is now available as a standard package

      sudo apt install carta

otherwise head over to https://cartavis.org to download

### Analysis Scripts




###  Converting CASA format to FITS

      casa-6.6.5-31-py3.10.el8/bin/casa
      CASA <1> exportfits('demo/M100_combine12+7_CO_cube.image','M100-demo.fits')
      CASA <2> exit

      $ ds9 M100-demo.fits
      $ carta M100-demo.fits

      #      for very large cubes, conversion can be useful to speed up CARTA
      $ fits2idia [-o M100-demo.hdf5] M100-demo.fits
      $ carta M100-demo.fits

### Sample CASA guides

0. https://almascience.nrao.edu/alma-data/science-verification   #4 on the list
1. https://casaguides.nrao.edu/index.php/M100_Band3
2. https://casaguides.nrao.edu/index.php/M100_Band3_Combine
3. https://casaguides.nrao.edu/index.php/M100_Band3_SingleDish


Note currently the Combine and SingleDish casaguides point to casa version 6.5.4 (Fall 2024)

### Data

For M100 We will need 12m, 7m, and TP data. For TW-Hyd .....

0. TW-Hyd data:  http://

   1.  bla bla
   2.  bla bla


1. M100 12m data: http://almascience.org/almadata/sciver/M100Band3_12m

   1. https://bulk.cv.nrao.edu/almadata/sciver/M100Band3_12m/M100_Band3_12m_CalibratedData.tgz    15GB  ***
   2. https://bulk.cv.nrao.edu/almadata/sciver/M100Band3_12m/M100_Band3_12m_Imaging.py
   
            M100_Band3_12m_CalibratedData.ms
            M100_12m_CO_demo.mask
            M100_Band3_12m_Imaging.py   (should produce M100_Band3_12m_ReferenceImages.tgz = 297M)
	 
2. M100 7m & TP data: http://almascience.org/almadata/sciver/M100Band3ACA

       https://bulk.cv.nrao.edu/almadata/sciver/M100Band3ACA/M100_Band3_7m_CalibratedData.tgz            - 9.1G ***
       https://bulk.cv.nrao.edu/almadata/sciver/M100Band3ACA/M100_Band3_7m_Imaging.py
       https://bulk.cv.nrao.edu/almadata/sciver/M100Band3ACA/M100_Band3_TP_CalibratedData_5.1.tgz        - 13G   --no--
       https://bulk.cv.nrao.edu/almadata/sciver/M100Band3ACA/M100_Band3_DataComb_ReferenceImages_5.1.tgz - 393M
       https://bulk.cv.nrao.edu/almadata/sciver/M100Band3ACA/M100_Band3_ACA_ReferenceImages_5.1.tgz      - 24M

  !  had to move the ms and mask file into the top level directory where working

3. M100 Combo Tutorial:  https://bulk.cv.nrao.edu/almadata/public/combo_tutorial

       M100_combine12+7_CO_cube.image.tgz
       script.py


## Data Symlinks:

As mentoined, the tgz files dump their (calibrated) data in subdirectories. To avoid confusion I decided to use
symlinks to these places, instead of moving them. So we would have:


      ln -s M100_Band3_12m_CalibratedData/M100_Band3_12m_CalibratedData.ms/
      ln -s M100_Band3_7m_CalibratedData/M100_Band3_7m_CalibratedData.ms
      ln -s M100_Band3_ACA_ReferenceImages_5.1/M100_TP_CO_cube.spw3.image.bl


# Links


1. CASA: https://casa.nrao.edu/casa_obtaining.shtml
1. Analysis Scripts: ftp://ftp.cv.nrao.edu/pub/casaguides/analysis_scripts.tar
2. CARTA: https://cartavis.org/
3. DataComb: https://github.com/teuben/DataComb 
4. QAC: https://github.com/teuben/QAC 
5. Phangs: https://github.com/akleroy/phangs_imaging_scripts
6. CASA-Guides-Script-Extractor: https://github.com/CasaGuides/CASA-Guides-Script-Extractor
