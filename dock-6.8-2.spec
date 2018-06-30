#
# Joe Allen
# 2018-06-28
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

%define shortsummary DOCK is a structure-based small molecule docking tool
Summary: %{shortsummary}

# Give the package a base name
%define pkg_base_name dock

# Create some macros (spec file variables)
%define major_version 6
%define minor_version 8
#%define patch_version 0

%define pkg_version %{major_version}.%{minor_version}

%define rpm_group G-820313

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

Release:   2
License:   UCSF
Group:     Applications/Life Sciences
URL:       http://dock.compbio.ucsf.edu
Packager:  TACC - wallen@tacc.utexas.edu
Source:    %{pkg_base_name}.%{major_version}.%{minor_version}_source.tar.gz

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
%setup -n %{pkg_base_name}%{major_version}
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
%include ./include/%{PLATFORM}/mpi-load.inc
%include ./include/%{PLATFORM}/mpi-env-vars.inc
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

# Example configure and make
cd install/

./configure intel
make all CFLAGS=" -O3 %{TACC_OPT} " \
         FFLAGS=" -O2 %{TACC_OPT} " \
         OCFLAGS=" -O3 -D_ANSI_SOURCE %{TACC_OPT} " \
         DOCKHOME=%{INSTALL_DIR}
make clean

./configure intel.intelmpi.parallel
make dock CFLAGS=" -DBUILD_DOCK_WITH_MPI -O3 %{TACC_OPT} " \
          FFLAGS=" -O2 %{TACC_OPT} " \
          OCFLAGS=" -O3 -D_ANSI_SOURCE %{TACC_OPT} " \
          CXX="mpicxx" \
          LOAD="mpicxx" \
          DOCKHOME=%{INSTALL_DIR}
make clean

cd ../

# sed -i bin/* | 'xxxxxxxxxx' | /opt/apps/... |
for bin_file in ` ls bin/ `; do

%if "%{PLATFORM}" == "stampede2"
	sed -i 's/tmprpm/home1\/apps/g' bin/$bin_file
%endif

%if "%{PLATFORM}" == "ls5"
	sed -i 's/tmprpm/opt\/apps/g' bin/$bin_file
%endif
done

cp -rp bin/ $RPM_BUILD_ROOT/%{INSTALL_DIR}
cp -rp parameters/ $RPM_BUILD_ROOT/%{INSTALL_DIR}
cp -rp tutorials/ $RPM_BUILD_ROOT/%{INSTALL_DIR}

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
 - %{MODULE_VAR}_PARAM

for the location of the %{pkg_base_name} distribution.

Most executables in the %{pkg_base_name} package are built for serial execution,
and should be called as, e.g.:

  dock6 -i infile -o outfile

For MPI calculations, use:

  ibrun dock6.mpi -i infile -o outfile

Documentation: %{url}

NOTE: Kuntz Lab programs are available free of charge for academic institutions,
but there is a licensing fee for industrial organizations. Full terms of service
here:

http://dock.compbio.ucsf.edu/Online_Licensing/index.htm


Version %{pkg_version}
]]



local err_message = [[
You do not have access to %{pkg_base_name} %{pkg_version}.

Users have to confirm with TACC that they plan to use %{pkg_base_name} in 
accordance with the licensing information provided here:

http://dock.compbio.ucsf.edu/Online_Licensing/index.htm

To be approved, please submit a ticket here:

https://portal.tacc.utexas.edu/tacc-consulting.

]]


local group  = "%{rpm_group}"
local grps   = capture("groups")
local found  = false
local isRoot = tonumber(capture("id -u")) == 0
for g in grps:split("[ \n]") do
   if (g == group or isRoot)  then
      found = true
      break
    end
end


help(help_message,"\n")

whatis("Name: %{pkg_base_name}")
whatis("Version: %{pkg_version}")
whatis("Category: computational biology, chemistry")
whatis("Keywords: Computational Biology, Chemistry, Structural Biology, Docking, Small Molecule, Protein")
whatis("Description: %{shortsummary}")
whatis("URL: %{url}")

if (found) then
  prepend_path("PATH",		"%{INSTALL_DIR}/bin")

  setenv("%{MODULE_VAR}_DIR",	"%{INSTALL_DIR}")
  setenv("%{MODULE_VAR}_BIN",	"%{INSTALL_DIR}/bin")
  setenv("%{MODULE_VAR}_PARAM",	"%{INSTALL_DIR}/parameters")
else
  LmodError(err_message,"\n")
end
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

  %defattr(750,root,%{rpm_group},)
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