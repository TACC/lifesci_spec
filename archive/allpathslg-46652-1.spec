# $Id$

Summary: ALLPATHS-LG - Broad Institute assembler for complex eukaryote genomes
Name: allpathslg
Version: 46652
Release: 1
License: MIT
Group: Applications/Life Sciences
Source0:  ftp://ftp.broadinstitute.org/pub/crd/ALLPATHS/Release-LG/latest_source_code/allpathslg-46652.tar.gz
Packager: TACC - vaughn@tacc.utexas.edu
BuildRoot: /var/tmp/%{name}_%{version}-buildroot

#------------------------------------------------
# BASIC DEFINITIONS
#------------------------------------------------
%include rpm-dir.inc
%include ../system-defines.inc

# Compiler Family Definitions
# %include compiler-defines.inc
# MPI Family Definitions
# %include mpi-defines.inc
# Other defs

%define PNAME %{name}

%define INSTALL_DIR %{APPS}/%{name}/%{version}
%define MODULE_DIR  %{APPS}/%{MODULES}/%{name}
%define MODULE_VAR TACC_ALLPATHS

#------------------------------------------------
# PACKAGE DESCRIPTION
#------------------------------------------------
%description
ALLPATHS‐LG is a short‐read assembler. It has been designed to use reads produced by new sequencing technology machines such as the Illumina Genome Analyzer. The version described here has been optimized for, but not necessarily limited to, reads of length 100 bases. ALLPATHS is not designed to assemble Sanger or 454 FLX reads, or a mix of these with short reads.

#------------------------------------------------
# PREPARATION SECTION
#------------------------------------------------
# Use -n <name> if source file different from <name>-<version>.tar.gz
%prep

# Remove older attempts
rm   -rf $RPM_BUILD_ROOT/%{INSTALL_DIR}

# Unpack source
# This will unpack the source to /tmp/BUILD/***
%setup -n %{name}-%{version}

#------------------------------------------------
# BUILD SECTION
#------------------------------------------------
%build

#------------------------------------------------
# INSTALL SECTION
#------------------------------------------------
%install

%include ../system-load.inc
mkdir -p $RPM_BUILD_ROOT/%{INSTALL_DIR}

# Load correct compiler
# %include compiler-load.inc
# Load correct mpi stack
# %include mpi-load.inc
# %include mpi-env-vars.inc
# Load additional modules here (as needed)

module purge
module load TACC
module swap $TACC_FAMILY_COMPILER gcc/4.7.1

./configure --prefix=%{INSTALL_DIR} 
make -j 12 LDFLAGS="-Wl,-rpath,$GCC_LIB"

# strip is important - otherwise the binaries sum to > 500 MB and packaging will fail
make DESTDIR=$RPM_BUILD_ROOT install-strip

# ADD ALL MODULE STUFF HERE
# TACC module

rm   -rf $RPM_BUILD_ROOT/%{MODULE_DIR}
mkdir -p $RPM_BUILD_ROOT/%{MODULE_DIR}
cat > $RPM_BUILD_ROOT/%{MODULE_DIR}/%{version}.lua << 'EOF'
help (
[[
This module loads %{name} built with gcc.
This module makes available the ALLPATHS-LG assembler. Documentation for %{name} is available online at the publisher\'s website: http://www.broadinstitute.org/software/allpaths-lg/
The ALLPATHS-LG executables can be found in %{MODULE_VAR}_DIR. 

ALLPATHS-LG requires Picard tools for data preparation, and Graphviz dot for plotting assembly graphs. The former is provided as a module, the latter may be self-installed in the user's $HOME directory.

Version %{version}
]])

whatis("Name: ALLPATHS-LG")
whatis("Version: %{version}")
whatis("Category: computational biology, genomics")
whatis("Keywords:  Biology, Genomics, Sequencing, Assembly")
whatis("Description: ALLPATHS-LG - Broad Institute assembler for complex eukaryote genomes")
whatis("URL: http://www.broadinstitute.org/software/allpaths-lg/")

prereq ("picard")

setenv("%{MODULE_VAR}_DIR","%{INSTALL_DIR}/")
prepend_path("PATH"       ,"%{INSTALL_DIR}/bin")

EOF

#--------------
#  Version file.
#--------------

cat > $RPM_BUILD_ROOT%{MODULE_DIR}/.version.%{version} << 'EOF'
#%Module3.1.1#################################################
##
## version file for %{PNAME}-%{version}
##

set     ModulesVersion      "%{version}"
EOF

#------------------------------------------------
# FILES SECTION
#------------------------------------------------
%files

# Define files permisions, user and group
%defattr(755,root,root,-)
%{INSTALL_DIR}
%{MODULE_DIR}

#------------------------------------------------
# CLEAN UP SECTION
#------------------------------------------------
%post
%clean
# Make sure we are not within one of the directories we try to delete
cd /tmp

# Remove the installation files now that the RPM has been generated
rm -rf $RPM_BUILD_ROOT

