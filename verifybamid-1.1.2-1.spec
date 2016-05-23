#------------------------------------------------
# INITIAL DEFINITIONS
#------------------------------------------------
%define   PNAME verifybamid
Version:  1.1.2
Release:  1
License:  GNU General Public License Version 3
Group:    Applications/Life Sciences
Source:   https://github.com/statgen/verifyBamID/archive/v1.1.2.tar.gz
Packager: TACC - wallen@tacc.utexas.edu
Summary:  VerifyBamID - Verify data from NGS

## System Definitions
%include ./include/system-defines.inc
%include ./include/%{PLATFORM}/rpm-dir.inc
## Compiler Family Definitions
# %include ./include/%{PLATFORM}/compiler-defines.inc
## MPI Family Definitions
# %include ./include/%{PLATFORM}/mpi-defines.inc
## directory and name definitions for relocatable RPMs
%include ./include/name-defines.inc

%define MODULE_VAR  %{MODULE_VAR_PREFIX}VERIFYBAMID

## PACKAGE DESCRIPTION
%description
verifyBamID is a software that verifies whether the reads in particular file match previously known genotypes for an individual (or group of individuals), and checks whether the reads are contaminated as a mixture of two samples. verifyBamID can detect sample contamination and swaps when external genotypes are available. When external genotypes are not available, verifyBamID still robustly detects sample swaps

## PREP
%prep
rm -rf $RPM_BUILD_ROOT/%{INSTALL_DIR}
rm -rf $RPM_BUILD_ROOT/%{MODULE_DIR}

## SETUP
# Use -n <name> if source file different from <name>-<version>.tar.gz
# the -c option creates a dir and changes to it before unpacking
%setup -n verifyBamID-%{version}

## BUILD
%build

#------------------------------------------------
# INSTALL 
#------------------------------------------------
%install

# Start with a clean environment
%include ./include/%{PLATFORM}/system-load.inc

# Create a directory 
mkdir -p $RPM_BUILD_ROOT/%{INSTALL_DIR}

#--------------------------------------
## Install Steps Start
module purge
module load TACC
module swap intel gcc

# One-step compile
make cloneLib
make

# Copy the binaries
cp -r ./bin/ $RPM_BUILD_ROOT/%{INSTALL_DIR}/

#------------------------------------------------
# MODULEFILE CREATION
#------------------------------------------------
mkdir -p $RPM_BUILD_ROOT/%{MODULE_DIR}

#--------------------------------------
## Modulefile Start
cat > $RPM_BUILD_ROOT/%{MODULE_DIR}/%{version}.lua << 'EOF'
help (
[[

This module loads %{PNAME} version %{version}
Documentation for %{PNAME} is available online at: http://genome.sph.umich.edu/wiki/VerifyBamID

The executable can be found in %{MODULE_VAR}_BIN

Version %{version}

]])

whatis("Name: %{PNAME}")
whatis("Version: %{version}")
whatis("Category: computational biology, genomics")
whatis("Keywords:  Biology, Genomics, Genotyping, Resequencing, VCF")
whatis("Description: VerifyBamID - Verify data from NGS.")

whatis("URL: http://genome.sph.umich.edu/wiki/VerifyBamID")

setenv("%{MODULE_VAR}_DIR", "%{INSTALL_DIR}/")
setenv("%{MODULE_VAR}_BIN", "%{INSTALL_DIR}/bin/")
prepend_path("PATH", "%{INSTALL_DIR}/bin/")
prereq("gcc/5.2.0")

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
%post

## CLEAN UP
%clean
# Make sure we are not within one of the directories we try to delete
cd /tmp

# Remove the installation files now that the RPM has been generated
rm -rf $RPM_BUILD_ROOT


# In SPECS dir:
# ./build_rpm.sh verifybamid-1.1.2-1.spec
#
# In apps dir: 
# export RPM_DBPATH=$PWD/db/
# rpm --dbpath $PWD/db --relocate /opt/apps=$PWD -Uvh --force --nodeps /path/to/rpm/file/rpm_file.rpm
# sed -i 's?opt/apps?home/03439/wallen/hikari/apps?g' /path/to/modulefiles/package/version.lua

