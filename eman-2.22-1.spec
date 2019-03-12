#
# Joe Allen
# 2019-03-11
#
# Important Build-Time Environment Variables (see name-defines.inc)
# NO_PACKAGE=1    -> Do Not Build/Rebuild Package RPM
# NO_MODULEFILE=1 -> Do Not Build/Rebuild Modulefile RPM
#
# Important Install-Time Environment Variables (see post-defines.inc)
# RPM_DBPATH      -> Path To Non-Standard RPM Database Location
#
# Typical Command-Line Example:
# ./build_rpm.sh Bar.spec
# cd ../RPMS/x86_64
# rpm -i --relocate /tmprpm=/opt/apps Bar-package-1.1-1.x86_64.rpm
# rpm -i --relocate /tmpmod=/opt/apps Bar-modulefile-1.1-1.x86_64.rpm
# rpm -e Bar-package-1.1-1.x86_64 Bar-modulefile-1.1-1.x86_64

%define shortsummary EMAN2 is a scientific image processing suite for single particle reconstruction from cryoEM
Summary: %{shortsummary}

# Give the package a base name
%define pkg_base_name eman

# Create some macros (spec file variables)
%define major_version 2
%define minor_version 22
#%define patch_version 0

%define pkg_version %{major_version}.%{minor_version}

### Toggle On/Off ###
%include ./include/system-defines.inc
%include ./include/%{PLATFORM}/rpm-dir.inc                  
#%include ./include/%{PLATFORM}/compiler-defines.inc
#%include ./include/%{PLATFORM}/mpi-defines.inc
%include ./include/%{PLATFORM}/name-defines.inc
########################################
############ Do Not Remove #############
########################################

############ Do Not Change #############
Name:      %{pkg_name}
Version:   %{pkg_version}
########################################

Release:   1
License:   GPLv2
Group:     Applications/Life Sciences
URL:       http://blake.bcm.tmc.edu/EMAN2/
Packager:  TACC - wallen@tacc.utexas.edu
#Source:    %{pkg_base_name}%{major_version}.%{minor_version}.linux64.sh

%package %{PACKAGE}
Summary: %{shortsummary}
Group:   Applications/Life Sciences
%description package
%{pkg_base_name}: %{shortsummary}

%package %{MODULEFILE}
Summary: The modulefile RPM
Group:   Lmod/Modulefiles
%description modulefile
Module file for %{pkg_base_name}

%description
%{pkg_base_name}: %{shortsummary}

#---------------------------------------
%prep
#---------------------------------------

#------------------------
%if %{?BUILD_PACKAGE}
#------------------------
  # Delete the package installation directory.
  rm -rf $RPM_BUILD_ROOT/%{INSTALL_DIR}

# Comment this out if pulling from git
#%setup -n %{pkg_base_name}%{major_version}-%{major_version}.%{minor_version}
# If using multiple sources. Make sure that the "-n" names match.
#%setup -T -D -a 1 -n %{pkg_base_name}-%{pkg_version}

#-----------------------
%endif # BUILD_PACKAGE |
#-----------------------

#---------------------------
%if %{?BUILD_MODULEFILE}
#---------------------------
  #Delete the module installation directory.
  rm -rf $RPM_BUILD_ROOT/%{MODULE_DIR}
#--------------------------
%endif # BUILD_MODULEFILE |
#--------------------------

#---------------------------------------
%build
#---------------------------------------


#---------------------------------------
%install
#---------------------------------------

# Setup modules
%include ./include/%{PLATFORM}/system-load.inc
##################################
# If using build_rpm
##################################
#%include ./include/%{PLATFORM}/compiler-load.inc
#%include ./include/%{PLATFORM}/mpi-load.inc
#%include ./include/%{PLATFORM}/mpi-env-vars.inc
##################################
# Manually load modules
##################################
# module load
##################################

echo "Building the package?:    %{BUILD_PACKAGE}"
echo "Building the modulefile?: %{BUILD_MODULEFILE}"

#------------------------
%if %{?BUILD_PACKAGE}
#------------------------

  mkdir -p $RPM_BUILD_ROOT/%{INSTALL_DIR}
  
  #######################################
  ##### Create TACC Canary Files ########
  #######################################
  touch $RPM_BUILD_ROOT/%{INSTALL_DIR}/.tacc_install_canary
  #######################################
  ########### Do Not Remove #############
  #######################################

  #========================================
  # Insert Build/Install Instructions Here
  #========================================

  module purge
  module load TACC
  module unload python2
  
  ##### Install EMAN2 #####
  wget https://cryoem.bcm.edu/cryoem/static/software/release-2.22/eman2.22.linux64.sh
  bash eman2.22.linux64.sh -b -f -p $RPM_BUILD_ROOT/%{INSTALL_DIR}
  
  rm -rf $RPM_BUILD_ROOT/%{INSTALL_DIR}/doc
  rm -rf $RPM_BUILD_ROOT/%{INSTALL_DIR}/envs
  rm -rf $RPM_BUILD_ROOT/%{INSTALL_DIR}/examples
  rm -rf $RPM_BUILD_ROOT/%{INSTALL_DIR}/pkgs/*tar.bz2
  rm -rf $RPM_BUILD_ROOT/%{INSTALL_DIR}/recipes
  rm -rf $RPM_BUILD_ROOT/%{INSTALL_DIR}/test
  rm -rf $RPM_BUILD_ROOT/%{INSTALL_DIR}/utils
  rm -rf $RPM_BUILD_ROOT/%{INSTALL_DIR}/var


#-----------------------  
%endif # BUILD_PACKAGE |
#-----------------------


#---------------------------
%if %{?BUILD_MODULEFILE}
#---------------------------

  mkdir -p $RPM_BUILD_ROOT/%{MODULE_DIR}
  
  #######################################
  ##### Create TACC Canary Files ########
  #######################################
  touch $RPM_BUILD_ROOT/%{MODULE_DIR}/.tacc_module_canary
  #######################################
  ########### Do Not Remove #############
  #######################################
  
# Write out the modulefile associated with the application
cat > $RPM_BUILD_ROOT/%{MODULE_DIR}/%{MODULE_FILENAME} << 'EOF'
local help_message = [[
This module file defines the following environment variables:

 - %{MODULE_VAR}_DIR
 - %{MODULE_VAR}_BIN

for the location of the EMAN2 distribution.

To use all of the features of e2display.py, you may need to connect through a
VNC session as described in the Lonestar5 user guide:

https://portal.tacc.utexas.edu/user-guides/lonestar5

Documentation: %{url}

Version %{version}
]]

help(help_message,"\n")

whatis("Name: %{pkg_base_name}")
whatis("Version: %{version}")
whatis("Category: computational biology, chemistry")
whatis("Keywords: Computational Biology, Chemistry, Structural Biology, Image Processing, Image Reconstruction, CryoEM")
whatis("Description: %{shortsummary}")
whatis("URL: %{url}")

setenv("EMAN2DIR",              "%{INSTALL_DIR}")
setenv("%{MODULE_VAR}_DIR",     "%{INSTALL_DIR}")
setenv("%{MODULE_VAR}_BIN",	"%{INSTALL_DIR}/bin")
prepend_path("PATH", "%{INSTALL_DIR}/bin")

EOF
  
cat > $RPM_BUILD_ROOT/%{MODULE_DIR}/.version.%{version} << 'EOF'
#%Module3.1.1#################################################
##
## version file for %{BASENAME}%{version}
##

set     ModulesVersion      "%{version}"
EOF
  
  # Check the syntax of the generated lua modulefile
  %{SPEC_DIR}/scripts/checkModuleSyntax $RPM_BUILD_ROOT/%{MODULE_DIR}/%{MODULE_FILENAME}

#--------------------------
%endif # BUILD_MODULEFILE |
#--------------------------


#------------------------
%if %{?BUILD_PACKAGE}
%files package
#------------------------

  %defattr(-,root,install,)
  # RPM package contains files within these directories
  %{INSTALL_DIR}

#-----------------------
%endif # BUILD_PACKAGE |
#-----------------------
#---------------------------
%if %{?BUILD_MODULEFILE}
%files modulefile 
#---------------------------

  %defattr(-,root,install,)
  # RPM modulefile contains files within these directories
  %{MODULE_DIR}

#--------------------------
%endif # BUILD_MODULEFILE |
#--------------------------


########################################
## Fix Modulefile During Post Install ##
########################################
%post %{PACKAGE}
export PACKAGE_POST=1
%include ./include/%{PLATFORM}/post-defines.inc
%post %{MODULEFILE}
export MODULEFILE_POST=1
%include ./include/%{PLATFORM}/post-defines.inc
%preun %{PACKAGE}
export PACKAGE_PREUN=1
%include ./include/%{PLATFORM}/post-defines.inc
########################################
############ Do Not Remove #############
########################################

#---------------------------------------
%clean
#---------------------------------------
rm -rf $RPM_BUILD_ROOT
