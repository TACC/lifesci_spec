#------------------------------------------------
# INITIAL DEFINITIONS
#------------------------------------------------
%define   PNAME eman
Version:  2.2
Release:  1
License:  GPLv2
Group:    Applications/Life Sciences
Source:   v2.2.tar.gz
Packager: TACC - wallen@tacc.utexas.edu
Summary:  A scientific image processing suite for single particle reconstruction from cryoEM

## System Definitions
%include ./include/system-defines.inc
%include ./include/%{PLATFORM}/rpm-dir.inc
## Compiler Family Definitions
%include ./include/%{PLATFORM}/compiler-defines.inc
## MPI Family Definitions
#%include ./include/%{PLATFORM}/mpi-defines.inc
## directory and name definitions for relocatable RPMs
%include ./include/name-defines.inc
#prevent stripping of binaries
%define __spec_install_post %{nil}

%define MODULE_VAR %{MODULE_VAR_PREFIX}EMAN

## PACKAGE DESCRIPTION
%description
From the developers: EMAN2 is a scientific image processing suite with a particular focus on single particle reconstruction from cryoEM images. EMAN2 is a complete refactoring of the original EMAN1 library. The new system offers an easily extensible infrastructure, better documentation, easier customization, etc. EMAN2 was designed to happily coexist with EMAN1 installations, for users wanting to experiment, but not ready to completely switch from EMAN1 to EMAN2. 

## PREP
%prep
rm -rf $RPM_BUILD_ROOT/%{INSTALL_DIR}
rm -rf $RPM_BUILD_ROOT/%{MODULE_DIR}

## SETUP
# Use -n <name> if source file different from <name>-<version>.tar.gz
%setup -n eman2-2.2

## BUILD
%build

#------------------------------------------------
# INSTALL 
#------------------------------------------------
%install

# Start with a clean environment
%include ./include/%{PLATFORM}/system-load.inc
mkdir -p $RPM_BUILD_ROOT/%{INSTALL_DIR}

#--------------------------------------
##### Install Steps Start
module purge
module load TACC
module load cmake gsl/2.2.1 qt/4.8 fftw3/3.3.6 hdf5/1.8.16 python/2.7.12

BUILD_DIR=`dirname $(pwd)`
TMP_INSTALL_DIR="${BUILD_DIR}/install"
rm -rf ${TMP_INSTALL_DIR}/
mkdir ${TMP_INSTALL_DIR}

mkdir build-dependencies/
cd build-dependencies/


##### Install Boost with python bindings
export PYTHON_ROOT=/opt/apps/intel16/python/2.7.12
export PYTHON_VERSION=2.7.12
export PYTHONPATH=/opt/apps/intel16/python/2.7.12/lib/python2.7/site-packages:$PYTHONPATH


wget https://sourceforge.net/projects/boost/files/boost/1.59.0/boost_1_59_0.tar.gz/download -O boost_1_59_0.tar.gz
tar -xvzf boost_1_59_0.tar.gz
cd boost_1_59_0/
./bootstrap.sh --prefix=${TMP_INSTALL_DIR}/dependencies \
               --with-toolset=intel-linux \
               --with-libraries=all \
               --without-libraries=mpi \
               --with-python=/opt/apps/intel16/python/2.7.12/bin/python \
               --with-python-root=/opt/apps/intel16/python/2.7.12 \
               --with-python-version=2.7.12

./b2 -j 4 --prefix=${TMP_INSTALL_DIR}/dependencies install
cd ../


##### Install FTGL
git clone https://github.com/ulrichard/ftgl
cd ftgl
./autogen.sh
./configure --prefix=${TMP_INSTALL_DIR}/dependencies CXX=icpc CC=icc
make -j4
make install
cd ..


##### Install berkeley-db and bsddb3
wget http://download.oracle.com/berkeley-db/db-5.1.29.NC.tar.gz
tar -xvzf db-5.1.29.NC.tar.gz
cd db-5.1.29.NC/build_unix/
../dist/configure --disable-static --prefix=${TMP_INSTALL_DIR}/dependencies
make -j4
make install
cd ../../

# Need to define these now for the bsddb part
export PATH=${TMP_INSTALL_DIR}/dependencies/bin:$PATH
export LD_LIBRARY_PATH=${TMP_INSTALL_DIR}/dependencies/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=${TMP_INSTALL_DIR}/dependencies/lib/python2.7/site-packages:$LD_LIBRARY_PATH
export PYTHONPATH=${TMP_INSTALL_DIR}/dependencies/lib/python2.7/site-packages:$PYTHONPATH
mkdir -p ${TMP_INSTALL_DIR}/dependencies/lib/python2.7/site-packages/ 

wget https://pypi.python.org/packages/6e/42/b1bf49b6d740dcb3e7cf3ca1df0e9897b224bb558320f360ed71d77235a4/bsddb3-5.1.2.tar.gz
tar -xvzf bsddb3-5.1.2.tar.gz
cd bsddb3-5.1.2/
python setup.py --berkeley-db=${TMP_INSTALL_DIR}/dependencies build
python setup.py --berkeley-db=${TMP_INSTALL_DIR}/dependencies install --prefix=${TMP_INSTALL_DIR}/dependencies

cd ../


##### Install sip
wget https://sourceforge.net/projects/pyqt/files/sip/sip-4.19.3/sip-4.19.3.tar.gz
tar -xvzf sip-4.19.3.tar.gz
cd sip-4.19.3/
python configure.py \
       --bindir=${TMP_INSTALL_DIR}/dependencies/bin \
       --destdir=${TMP_INSTALL_DIR}/dependencies/lib/python2.7/site-packages \
       --incdir=${TMP_INSTALL_DIR}/dependencies/include/python2.7 \
       --sipdir=${TMP_INSTALL_DIR}/dependencies/share/sip \
       --stubsdir=${TMP_INSTALL_DIR}/dependencies/lib/python2.7/site-packages 

make -j4
make install
cd ../


##### Install pyqt4
wget https://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.12.1/PyQt4_gpl_x11-4.12.1.tar.gz
tar -xvzf PyQt4_gpl_x11-4.12.1.tar.gz
cd PyQt4_gpl_x11-4.12.1/
python configure-ng.py \
       --confirm-license \
       --bindir=${TMP_INSTALL_DIR}/dependencies/bin \
       --destdir=${TMP_INSTALL_DIR}/dependencies/lib/python2.7/site-packages \
       --designer-plugindir=${TMP_INSTALL_DIR}/dependencies/designer \
       --enable=QtCore \
       --enable=QtGui \
       --enable=QtOpenGL \
       --enable=QtWebKit \
       --sip-incdir=${TMP_INSTALL_DIR}/dependencies/include/python2.7 \
       --no-sip-files

make -j4
make install
cd ../


##### Install PyOpenGL
wget https://pypi.python.org/packages/df/fe/b9da75e85bcf802ed5ef92a5c5e4022bf06faa1d41b9630b9bb49f827483/PyOpenGL-3.1.1a1.tar.gz
tar -xvzf PyOpenGL-3.1.1a1.tar.gz
cd PyOpenGL-3.1.1a1
python setup.py install --prefix=${TMP_INSTALL_DIR}/dependencies
cd ../


##### Environment for eman2
export FFTWDIR=$TACC_FFTW3_DIR
export GSLDIR=$TACC_GSL_DIR
export BOOSTDIR=${TMP_INSTALL_DIR}/dependencies
export HDF5DIR=$TACC_HDF5_DIR
export CC=`which icc`
export CXX=`which icpc`


##### Install Eman2
cd ../
mkdir build
cd build/

cmake -DEMAN_INSTALL_PREFIX=${TMP_INSTALL_DIR} \
      -DCMAKE_C_COMPILER=icc \
      -DCMAKE_CXX_COMPILER=icpc \
      -DCMAKE_CXX_FLAGS="-O3 -xAVX -axCORE-AVX2 -I/usr/include/freetype2" \
      -DCMAKE_C_FLAGS="-O3 -xAVX -axCORE-AVX2 -I/usr/include/freetype2" \
      -DHDF5_LIBRARY=/opt/apps/intel16/hdf5/1.8.16/x86_64/lib/libhdf5.so \
      -DFTGL_INCLUDE_PATH=${TMP_INSTALL_DIR}/dependencies/include \
      -DFTGL_LIBRARY=${TMP_INSTALL_DIR}/dependencies/lib/libftgl.so \
      -DNUMPY_INCLUDE_PATH=$TACC_PYTHON_LIB/python2.7/site-packages/numpy-1.11.1-py2.7-linux-x86_64.egg/numpy/core/include \
      ../

make -j4    
make install

# small bug in eman2
cp ${TMP_INSTALL_DIR}/bin/e2version.py ${TMP_INSTALL_DIR}/lib/


##### Move tmp install files into buildroot
cp -r ${TMP_INSTALL_DIR}/* ${RPM_BUILD_ROOT}/%{INSTALL_DIR}
rm -rf ${TMP_INSTALL_DIR}/


#------------------------------------------------
# MODULEFILE CREATION
#------------------------------------------------
mkdir -p $RPM_BUILD_ROOT/%{MODULE_DIR}

#--------------------------------------
## Modulefile Start
cat > $RPM_BUILD_ROOT/%{MODULE_DIR}/%{version}.lua << 'EOF'
help (
[[

This module loads %{PNAME} version %{version}. Threading is enabled, but MPI is not.
Documentation for %{PNAME} is available online at: http://blake.bcm.edu/emanwiki/EMAN2

Loading this module defines the following environment variables:

    %{MODULE_VAR}_DIR
    %{MODULE_VAR}_BIN
    %{MODULE_VAR}_LIB


To use this package, please load these modules first:

    intel/16.0.1  gsl/2.2.1  qt/4.8  fftw3/3.3.6  hdf5/1.8.16  python/2.7.12


To use e2display.py, use a VNC session or X forwarding, e.g.:

    [local] ssh -X username@ls5.tacc.utexas.edu
    ...
    [login] module load intel/16.0.1 gsl/2.2.1 qt/4.8 fftw3/3.3.6 hdf5/1.8.16 python/2.7.12 eman/2.2
    [login] idev
    ...
    [compute] e2display.py


Version %{version}

]])

whatis("Name: %{PNAME}")
whatis("Version: %{version}")
whatis("Category: computational biology, electron microscopy")
whatis("Keywords: Biology, Cryo-EM, Image Processing, Reconstruction")
whatis("Description: EMAN2 is a scientific image processing suite for single particle reconstruction from cryoEM.")
whatis("URL: http://blake.bcm.edu/emanwiki/EMAN2")

setenv("%{MODULE_VAR}_DIR",     "%{INSTALL_DIR}")
setenv("%{MODULE_VAR}_BIN",	"%{INSTALL_DIR}/bin")
setenv("%{MODULE_VAR}_LIB",	"%{INSTALL_DIR}/lib")

setenv("EMAN2DIR",              "%{INSTALL_DIR}")

prepend_path("PATH",            "%{INSTALL_DIR}/dependencies/bin")
prepend_path("PATH",            "%{INSTALL_DIR}/bin")
prepend_path("LD_LIBRARY_PATH", "%{INSTALL_DIR}/dependencies/lib/python2.7/site-packages")
prepend_path("LD_LIBRARY_PATH", "%{INSTALL_DIR}/dependencies/lib")
prepend_path("LD_LIBRARY_PATH", "%{INSTALL_DIR}/lib")
prepend_path("PYTHONPATH",      "%{INSTALL_DIR}/dependencies/lib/python2.7/site-packages")
prepend_path("PYTHONPATH",      "%{INSTALL_DIR}/lib")

set_alias("sparx", "sx.py")

prereq("intel/16.0.1", "gsl/2.2.1", "qt/4.8", "fftw3/3.3.6", "hdf5/1.8.16", "python/2.7.12")

EOF

## Modulefile End
#--------------------------------------

# Lua sytax check
if [ -f $SPEC_DIR/checkModuleSyntax ]; then
    $SPEC_DIR/checkModuleSyntax $RPM_BUILD_ROOT/%{MODULE_DIR}/%{version}.lua
fi

#--------------------------------------
## VERSION FILE
cat > $RPM_BUILD_ROOT/%{MODULE_DIR}/.version.%{version} << 'EOF'
#%Module3.1.1#################################################
##
## version file for %{PNAME}-%{version}
##

set     ModulesVersion      "%{version}"
EOF
## VERSION FILE END
#--------------------------------------

#------------------------------------------------
# FILES SECTION
#------------------------------------------------
%files
%defattr(-,root,install,)
%{INSTALL_DIR}
%{MODULE_DIR}

## POST 
#prevent stripping of binaries
#%post

## CLEAN UP
%clean
# Make sure we are not within one of the directories we try to delete
cd /tmp

# Remove the installation files now that the RPM has been generated
rm -rf $RPM_BUILD_ROOT

# In SPECS dir:
# ./build_rpm.sh --intel=16 eman-2.2-1.spec
#
# In apps dir: 
# export RPM_DBPATH=$PWD/db/
# rpm --dbpath $PWD/db --relocate /opt/apps=$PWD -Uvh --force --nodeps /path/to/rpm/file/rpm_file.rpm
# sed -i 's?opt/apps?work/03439/wallen/stampede/apps?g' /path/to/modulefiles/package/version.lua

