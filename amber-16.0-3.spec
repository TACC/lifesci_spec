#
# John Fonner
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

%define shortsummary Amber Toolkit and parallel modules. 
Summary: %{shortsummary}

# Give the package a base name
%define pkg_base_name amber 

# Create some macros (spec file variables)
%define major_version 16
%define minor_version 0

%define pkg_version %{major_version}.%{minor_version}

### Toggle On/Off ###
%include ./include/system-defines.inc
%include ./include/%{PLATFORM}/rpm-dir.inc                  
%include ./include/%{PLATFORM}/compiler-defines.inc
%include ./include/%{PLATFORM}/mpi-defines.inc
%include ./include/%{PLATFORM}/name-defines.inc
########################################
############ Do Not Remove #############
########################################

############ Do Not Change #############
Name:      %{pkg_name}
Version:   %{pkg_version}
########################################

Release:   3
License:   UCSF
Group:     Applications/Life Sciences
URL:       http://ambermd.org
Packager:  TACC - jfonner@tacc.utexas.edu
Source0:   AmberTools17.tar.bz2
Source1:   Amber16.tar.bz2

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

%setup  -n %{pkg_base_name}%{major_version} 

  # The next command unpacks Source1
  # -b <n> means unpack the nth source *before* changing directories.
  # -a <n> means unpack the nth source *after* changing to the
  #        top-level build directory (i.e. as a subdirectory of the main source).
  # -T prevents the 'default' source file from re-unpacking.  If you don't have this, the
  #    default source will unpack twice... a weird RPMism.
  # -D prevents the top-level directory from being deleted before we can get there!
%setup -T -D -b 1 -n %{pkg_base_name}%{major_version}

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

%define MODULE_VAR %{MODULE_VAR_PREFIX}AMBER

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
%include ./include/%{PLATFORM}/mpi-load.inc
%include ./include/%{PLATFORM}/mpi-env-vars.inc
##################################
# Manually load modules
##################################
module load python2
module load netcdf
%if "%{PLATFORM}" != "stampede2"
  module load cuda
%endif
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

  echo COMPILER LOAD: %{comp_module}
  echo MPI      LOAD: %{mpi_module}

         AMBERHOME=`pwd`
                   CUDA_HOME=$TACC_CUDA_DIR
                             MKL_HOME=$TACC_MKL_DIR
  export AMBERHOME CUDA_HOME MKL_HOME 

  # Amber now tries to download and install new bugfixes during the configure step if you tell it "y"
  # make clean

  ./update_amber --update
  ./update_amber --update


  # serial version
  ./configure --with-python $TACC_PYTHON2_BIN/python --with-netcdf $TACC_NETCDF_DIR intel 
  make -j 4 install

  # MPI version
  make clean
  ./configure --with-python $TACC_PYTHON2_BIN/python -mpi --with-netcdf $TACC_NETCDF_DIR intel
  # cd to src so that we don't recompile ambertools
  # cd src
  make  -j 4 install
  # cd ..

%if "%{PLATFORM}" != "stampede2"
    # GPU serial version
    make clean
    ./configure -cuda --with-python $TACC_PYTHON2_BIN/python intel 
    make LDFLAGS="-Wl,-rpath,$TACC_CUDA_LIB" install
    
    # GPU parallel version
    make clean
    ./configure -cuda --with-python $TACC_PYTHON2_BIN/python -mpi intel 
    make LDFLAGS="-Wl,-rpath,$TACC_CUDA_LIB" install
%endif

cp    -rp AmberTools bin dat doc benchmarks   \
          GNU_LGPL_v2 include \
          lib README share             \
                            $RPM_BUILD_ROOT/%{INSTALL_DIR}
# rm -rf                      $RPM_BUILD_ROOT/%{INSTALL_DIR}/AmberTools/src
# chmod -Rf u+rwX,g+rwX,o=rX  $RPM_BUILD_ROOT/%{INSTALL_DIR}

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
cat >    $RPM_BUILD_ROOT/%{MODULE_DIR}/%{version}.lua << 'EOF'
help(
[[
This revision of Amber was built on %(date +'%B %d, %Y') and includes all bugfixes
up to that point. A list of bugfixes is on the Amber site here:
http://ambermd.org/bugfixes.html

The TACC Amber installation includes the parallel modules with the .MPI suffix:

The pmemd binaries for use with GPUs have "cuda" in the name.  For example:

pmemd.cuda.MPI  pmemd.cuda

Visit http://ambermd.org/gpus/ for more information on running with GPUs as 
well as the TACC userguide at https://portal.tacc.utexas.edu/user-guides

Amber tools examples and benchmarks are included in the AmberTools directory.
Examples, data, docs, includes, info, libs are included in directories with
corresponding names. 

The Amber modulefile defines the following environment variables:
TACC_AMBER_DIR   TACC_AMBER_TOOLS   TACC_AMBER_BIN   TACC_AMBER_DAT
TACC_AMBER_DOC   TACC_AMBER_INC     TACC_AMBER_LIB   TACC_AMBER_MAN 
for the corresponding Amber directories.

Also, AMBERHOME is set to the Amber Home Directory (TACC_AMBER_DIR),
and $AMBERHOME/bin is included in the PATH variable.

Version %{version}
]]
)

whatis("Name: %{pkg_base_name}")
whatis("Version: %{version}")
whatis("Version-notes: Compiler:%{comp_fam_ver}, MPI:%{mpi_fam_ver}")
whatis("Category: computational biology, chemistry")
whatis("Keywords:  Chemistry, Biology, Molecular Dynamics, Cuda, Application")
whatis("URL: %{url}")
whatis("Description: %{shortsummary}")

--
-- Create environment variables.
--
local amber_dir   = "%{INSTALL_DIR}"
local amber_tools = "%{INSTALL_DIR}/AmberTools"
local amber_bin   = "%{INSTALL_DIR}/bin"
local amber_dat   = "%{INSTALL_DIR}/dat"
local amber_doc   = "%{INSTALL_DIR}/doc"
local amber_inc   = "%{INSTALL_DIR}/include"
local amber_lib   = "%{INSTALL_DIR}/lib"
local amber_python= "%{INSTALL_DIR}/lib/python2.7/site-packages"
local amber_man   = "%{INSTALL_DIR}/share/man"

setenv("TACC_AMBER_DIR"   , amber_dir  )
setenv("TACC_AMBER_TOOLS" , amber_tools)
setenv("TACC_AMBER_BIN"   , amber_bin  )
setenv("TACC_AMBER_DAT"   , amber_dat  )
setenv("TACC_AMBER_DOC"   , amber_doc  )
setenv("TACC_AMBER_INC"   , amber_inc  )
setenv("TACC_AMBER_LIB"   , amber_lib  )
setenv("TACC_AMBER_MAN"   , amber_man  )
setenv("AMBERHOME"        , amber_dir  )

append_path("PATH"        ,amber_bin   )
append_path("LD_LIBRARY_PATH",amber_lib)
append_path("PYTHONPATH"  ,amber_python)
append_path("MANPATH"     ,amber_man   )

family("amber")

always_load("python2")
always_load("netcdf")
EOF



cat > $RPM_BUILD_ROOT/%{MODULE_DIR}/.version.%{version} << 'EOF'
#%Module1.0#################################################
##
## Version file for AMBER %version
## Compiler: %{comp_fam_ver} and  MPI: %{mpi_fam_ver}
##

set     ModulesVersion      "%{version}"
EOF

  # Check the syntax of the generated lua modulefile
  %{SPEC_DIR}/scripts/checkModuleSyntax $RPM_BUILD_ROOT/%{MODULE_DIR}/%{MODULE_FILENAME}

#############################    MODULES  ######################################

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
#rm -rf $RPM_BUILD_ROOT
