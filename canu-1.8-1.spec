#
# Greg Zyna
# 2018-03-15
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

%define shortsummary Canu is a fork of the Celera Assembler designed for high-noise single-molecule sequencing (such as the PacBio RSII or Oxford Nanopore MinION)
Summary: %{shortsummary}

# Give the package a base name
%define pkg_base_name canu

# Create some macros (spec file variables)
%define major_version 1
%define minor_version 8

%define pkg_version %{major_version}.%{minor_version}

### Toggle On/Off ###
%include ./include/system-defines.inc
%include ./include/%{PLATFORM}/rpm-dir.inc                  
%include ./include/%{PLATFORM}/compiler-defines.inc
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
License:   BSD
Group:     Applications/Life Sciences
URL:       https://github.com/marbl/canu
Packager:  TACC - gzynda@tacc.utexas.edu
Source:    %{pkg_base_name}-%{pkg_version}.tar.gz

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
%setup -n %{pkg_base_name}-%{pkg_version}
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
%include ./include/%{PLATFORM}/compiler-load.inc
#%include ./include/%{PLATFORM}/mpi-load.inc
#%include ./include/%{PLATFORM}/mpi-env-vars.inc
##################################
# Manually load modules
##################################
module load boost
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

patch -p1 << 'EOF'
diff --git a/src/Makefile b/src/Makefile
index febe963..38b6bbe 100644
--- a/src/Makefile
+++ b/src/Makefile
@@ -377,11 +377,12 @@ endif
 #  really used.
 
 ifeq (${OSTYPE}, Linux)
-  CC        ?= gcc
-  CXX       ?= g++
+  CC        = icc
+  CXX       = icpc
+  AR        = xiar
 
-  CXXFLAGS  += -D_GLIBCXX_PARALLEL -pthread -fopenmp -fPIC
-  LDFLAGS   += -D_GLIBCXX_PARALLEL -pthread -fopenmp -lm
+  CXXFLAGS  += -D_GLIBCXX_PARALLEL -xCORE-AVX2 -ipo -pthread -fopenmp -fPIC
+  LDFLAGS   += -D_GLIBCXX_PARALLEL -pthread -fopenmp -limf
 
   CXXFLAGS  += -Wall -Wextra -Wno-write-strings -Wno-unused -Wno-char-subscripts -Wno-sign-compare -Wformat
 
@@ -394,7 +395,7 @@ ifeq (${OSTYPE}, Linux)
 
   ifeq ($(BUILDDEBUG), 1)
   else
-    CXXFLAGS += -O4 -funroll-loops -fexpensive-optimizations -finline-functions -fomit-frame-pointer
+    CXXFLAGS += -O3 -funroll-loops -finline-functions -fomit-frame-pointer
   endif
 endif
 
diff --git a/src/main.mk b/src/main.mk
index d2e2a40..087adc5 100644
--- a/src/main.mk
+++ b/src/main.mk
@@ -138,7 +138,7 @@ SRC_INCDIRS  := . \
                 utgcns/libcns \
                 utgcns/libpbutgcns \
                 utgcns/libNDFalcon \
-                utgcns/libboost \
+               $(TACC_BOOST_INC) \
                 overlapInCore \
                 overlapInCore/libedlib \
                 overlapInCore/liboverlap
EOF

BI=${RPM_BUILD_ROOT}/%{INSTALL_DIR}
cd src
make BUILDOPTIMIZED=1 DESTDIR=$RPM_BUILD_ROOT PREFIX=%{INSTALL_DIR} -j 48
rm -rf ${BI}/Linux-amd64/obj
cd $BI && mv Linux-amd64/* . && rm -rf Linux-amd64

### New scontrol script with Array
tee ${RPM_BUILD_ROOT}/%{INSTALL_DIR}/scontrol << 'EOF'
#!/bin/bash

/bin/scontrol show config | sed -e "s/\(MaxArraySize\s\+=\s\)0/\11000/"
EOF


### New sinfo script with actual memory values
tee ${RPM_BUILD_ROOT}/%{INSTALL_DIR}/sinfo << 'EOF'
#!/usr/bin/env python
from subprocess import check_output

cores2mem = {"96":"192000", "272":"96000"}

orig = check_output(['/bin/sinfo', '--exact', '-o' "%N %D %c %m"])
orig = orig.rstrip('\n').split('\n')

# Print the header
print orig[0]
for line in orig[1:]:
	tmpLine = line.split(' ')
	# Substitute the corret memory specifications
	if tmpLine[2] in cores2mem:
		tmpLine[3] = cores2mem[tmpLine[2]]
	print ' '.join(tmpLine)
EOF

### Make executable
chmod +x ${RPM_BUILD_ROOT}/%{INSTALL_DIR}/s{info,control}

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
The %{pkg_base_name} module file defines the following environment variables:

 - %{MODULE_VAR}_DIR
 - %{MODULE_VAR}_BIN
 - %{MODULE_VAR}_LIB

for the location of the %{pkg_base_name} distribution.

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   This version of %{pkg_base_name} only supports
           single node execution using the

                    useGrid=false

   paramter. TACC systems do NOT allow job arrays!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

Documentation: %{url}

Version %{version}
]]

help(help_message,"\n")

whatis("Name: %{pkg_base_name}")
whatis("Version: %{version}")
whatis("Category: computational biology, genomics, assembly")
whatis("Keywords: Biology, Genomics, assembly, long-reads, nanopore")
whatis("Description: %{shortsummary}")
whatis("URL: %{url}")

prereq("python")

prepend_path("PATH",		"%{INSTALL_DIR}/bin")

setenv("%{MODULE_VAR}_DIR",     "%{INSTALL_DIR}")
setenv("%{MODULE_VAR}_BIN",	"%{INSTALL_DIR}/bin")
setenv("%{MODULE_VAR}_LIB",	"%{INSTALL_DIR}/lib")
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
