#------------------------------------------------
# INITIAL DEFINITIONS
#------------------------------------------------
%define PNAME gatk
Version:  3.4.0
Release:  3
License:  Broad Institute Software License Agreement
Group:    Applications/Life Sciences
Source:   GenomeAnalysisTK-3.4-0-g7e26428.tar.bz2
Packager: TACC - vaughn@tacc.utexas.edu
Summary:  GATK - Genome Analysis Toolkit

## System Definitions
%include ./include/system-defines.inc
%include ./include/%{PLATFORM}/rpm-dir.inc
## Compiler Family Definitions
# %include ./include/%{PLATFORM}/compiler-defines.inc
## MPI Family Definitions
# %include ./include/%{PLATFORM}/mpi-defines.inc
## directory and name definitions for relocatable RPMs
%include ./include/name-defines.inc

%define MODULE_VAR  %{MODULE_VAR_PREFIX}GATK

## PACKAGE DESCRIPTION
%description
The Genome Analysis Toolkit or GATK is a software package developed at the Broad Institute to analyze high-throughput sequencing data. The toolkit offers a wide variety of tools, with a primary focus on variant discovery and genotyping as well as strong emphasis on data quality assurance. Its robust architecture, powerful processing engine and high-performance computing features make it capable of taking on projects of any size.

## PREP
# Use -n <name> if source file different from <name>-<version>.tar.gz
%prep
rm -rf $RPM_BUILD_ROOT/%{INSTALL_DIR}
rm -rf $RPM_BUILD_ROOT/%{MODULE_DIR}

# do this so GATK has somewhere to unpack
mkdir -p $RPM_BUILD_ROOT/%{INSTALL_DIR}

## SETUP
# Run the setup macro - this removes old copies, then unpackages the program zip file
# from ~SOURCES into ~BUILD
# the -c option creates a dir and changes to it before unpacking
%setup -c

## BUILD
%build

#------------------------------------------------
# INSTALL
#------------------------------------------------
%install

# Disable jar repacking
#%define __jar_repack %{nil}

# Start with a clean environment
%include ./include/%{PLATFORM}/system-load.inc
mkdir -p $RPM_BUILD_ROOT/%{INSTALL_DIR}

#--------------------------------------
## Install Steps Start

# GATK is pre-compiled, no install necessary

# Copy the binaries
cp -r ./resources/ $RPM_BUILD_ROOT/%{INSTALL_DIR}/
cp -r GenomeAnalysisTK.jar $RPM_BUILD_ROOT/%{INSTALL_DIR}/

#------------------------------------------------
# MODULEFILE CREATION
#------------------------------------------------
mkdir -p $RPM_BUILD_ROOT/%{MODULE_DIR}

#--------------------------------------
## Modulefile Start
cat > $RPM_BUILD_ROOT/%{MODULE_DIR}/%{version}.lua << 'EOF'
help (
[[
This module provides %{PNAME} version 3.4-0-g7e26428
Documentation is available online at: https://www.broadinstitute.org/gatk/download/
The GATK jarfile can be found in %{MODULE_VAR}_DIR
Resources, including test files, can be found in %{MODULE_VAR}_RESOURCES

Version %{version}

]])

whatis("Name: %{PNAME}")
whatis("Version: %{version}")
whatis("Category: computational biology, genomics")
whatis("Keywords:  Biology, Genomics, Genotyping, Resequencing, SNP")
whatis("Description: The Genome Analysis Toolkit or GATK is a software package developed at the Broad Institute to analyze high-throughput sequencing data.")

whatis("URL: https://www.broadinstitute.org/gatk/download/")

setenv("%{MODULE_VAR}_DIR", "%{INSTALL_DIR}/")
setenv("%{MODULE_VAR}_RESOURCES", "%{INSTALL_DIR}/resources/")

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

