# $Id$

Summary: SamTools - utilities for manipulating alignments in the SAM format.
Name: samtools
Version: 0.1.18
Release: 1
License: GPL
Group: Applications/Life Sciences
Source0:  samtools-%{version}.tar.bz2
Packager: TACC - vaughn@tacc.utexas.edu
BuildRoot: /var/tmp/%{name}-%{version}-buildroot

%define debug_package %{nil}
%include rpm-dir.inc
# Compiler Family Definitions
# %include compiler-defines.inc
# MPI Family Definitions
# %include mpi-defines.inc
# Other defs

%define APPS        /opt/apps
%define PKG_BASE    /opt/apps/%{name}
%define MODULES     modulefiles
%define INSTALL_DIR %{APPS}/%{name}/%{version}
%define MODULE_DIR  %{APPS}/%{MODULES}/%{name}
%define MODULE_VAR TACC_SAMTOOLS

%description
SAM Tools provide various utilities for manipulating alignments in the SAM format, including sorting, merging, indexing and generating alignments in a per-position format.

# Use -n <name> if source file different from <name>-<version>.tar.gz
%prep
rm -rf $RPM_BUILD_ROOT/%{INSTALL_DIR}

##
## SETUP
##

%setup -n %{name}-%{version}

##
## BUILD
##

%build

##
## INSTALL
##
%install

mkdir -p $RPM_BUILD_ROOT/%{INSTALL_DIR}
mkdir -p $RPM_BUILD_ROOT/%{INSTALL_DIR}/lib
mkdir -p $RPM_BUILD_ROOT/%{INSTALL_DIR}/include

# Start with a clean environment
if [ -f "$BASH_ENV" ]; then
   . $BASH_ENV
   export MODULEPATH=/opt/apps/xsede/modulefiles:/opt/apps/modulefiles:/opt/modulefiles
fi

module purge
module load TACC

# Load correct compiler
# %include compiler-load.inc
# Load correct mpi stack
# %include mpi-load.inc
# %include mpi-env-vars.inc
# Load additional modules here (as needed)

#make CC=icc CXX=icpc
make

cp -R ./samtools ./bcftools ./misc ./examples $RPM_BUILD_ROOT/%{INSTALL_DIR}
cp -R ./libbam.a $RPM_BUILD_ROOT/%{INSTALL_DIR}/lib
cp -R *.h $RPM_BUILD_ROOT/%{INSTALL_DIR}/include

#-----------------
# Modules Section
#-----------------

rm -rf $RPM_BUILD_ROOT%{MODULE_DIR}
mkdir -p $RPM_BUILD_ROOT%{MODULE_DIR}
cat   >  $RPM_BUILD_ROOT%{MODULE_DIR}/%{version}.lua << 'EOF'
help(
[[
The %{name} module file defines the following environment variables:
%{MODULE_VAR}_DIR, %{MODULE_VAR}_INC, and %{MODULE_VAR}_LIB 
associated with %{name}

Version %{version}
]]
)

whatis("Name: SamTools")
whatis("Version: %{version}")
whatis("Category: computational biology, genomics")
whatis("Keywords: Biology, Genomics, Quality Control, Utility, Sequencing, Genotyping, Resequencing, SNP")
whatis("URL: http://samtools.sourceforge.net/")
whatis("Description: SAM Tools provide various utilities for manipulating alignments in the SAM format, including sorting, merging, indexing and generating alignments in a per-position format.")


prepend_path("PATH",              "%{INSTALL_DIR}")
setenv (     "%{MODULE_VAR}_DIR", "%{INSTALL_DIR}/")
setenv (     "%{MODULE_VAR}_INC", "%{INSTALL_DIR}/include")
setenv (     "%{MODULE_VAR}_LIB", "%{INSTALL_DIR}/lib")

EOF

#--------------
#  Version file.
#--------------

cat > $RPM_BUILD_ROOT%{MODULE_DIR}/.version.%{version} << 'EOF'
#%Module3.1.1#################################################
##
## version file for %{name}-%{version}
##

set     ModulesVersion      "%{version}"
EOF

%files
%defattr(755,root,root,-)
%{INSTALL_DIR}
%{MODULE_DIR}

%clean
rm -rf $RPM_BUILD_ROOT

