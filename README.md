# Quick Array Combinations 2024

Notes on ALMA array combinations for the Data Reduction Workshop (29-oct-2024)





# qac2024https://casa.nrao.edu/casa_obtaining.shtml

# https://casa.nrao.edu/download/distro/casa/release/rhel/casa-6.6.5-31-py3.10.el8.tar.xz
# https://alma-dl.mtk.nao.ac.jp/ftp/casa/distro/casa/release/rhel/casa-6.5.6-22-py3.8.el8.tar.xz

# tar xf casa-6.6.5-31-py3.10.el8.tar.xz
# tar xf casa-6.5.6-22-py3.8.el8.tar.xz


# just data
# https://bulk.cv.nrao.edu/almadata/public/combo_tutorial

$ casa-6.6.5-31-py3.10.el8/bin/casa

CASA <1> exportfits('demo/M100_combine12+7_CO_cube.image','M100-demo.fits')
CASA <2> exit

$ ds9 M100-demo.fits

$ carta M100-demo.fits





https://casaguides.nrao.edu/index.php/M100_Band3_Combine_6.5.4

https://almascience.nrao.edu/alma-data/science-verification   #4 on the list
http://almascience.org/almadata/sciver/M100Band3_12m
http://almascience.org/almadata/sciver/M100Band3ACA


# https://casaguides.nrao.edu/index.php/M100_Band3

# 12m data
  https://bulk.cv.nrao.edu/almadata/sciver/M100Band3_12m/M100_Band3_12m_CalibratedData.tgz    15GB  ***
  https://bulk.cv.nrao.edu/almadata/sciver/M100Band3_12m/M100_Band3_12m_Imaging.py
         M100_Band3_12m_CalibratedData.ms
	 M100_12m_CO_demo.mask
	 M100_Band3_12m_Imaging.py   (should produce M100_Band3_12m_ReferenceImages.tgz = 297M)
# 7m & TP data
  https://bulk.cv.nrao.edu/almadata/sciver/M100Band3ACA/M100_Band3_7m_CalibratedData.tgz            - 9.1G ***
  https://bulk.cv.nrao.edu/almadata/sciver/M100Band3ACA/M100_Band3_7m_Imaging.py
  https://bulk.cv.nrao.edu/almadata/sciver/M100Band3ACA/M100_Band3_TP_CalibratedData_5.1.tgz        - 13G   --no--
  https://bulk.cv.nrao.edu/almadata/sciver/M100Band3ACA/M100_Band3_DataComb_ReferenceImages_5.1.tgz - 393M
  https://bulk.cv.nrao.edu/almadata/sciver/M100Band3ACA/M100_Band3_ACA_ReferenceImages_5.1.tgz      - 24M

  !  had to move the ms and mask file into the top level directory where working


# https://casaguides.nrao.edu/index.php/M100_Band3_SingleDish_6.5.4

# https://casaguides.nrao.edu/index.php/M100_Band3_Combine_6.5.4
