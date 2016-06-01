###
### PLEASE ONLY USE THIS SPEC FILE ON HIKARI
###
#------------------------------------------------
# INITIAL DEFINITIONS
#------------------------------------------------
%define    PNAME tophat
Version:   2.1.1
Release:   1
License:   GPLv2
Group:     Applications/Life Sciences
Source:    tophat-2.1.1.tar.gz
Packager:  TACC - jfonner@tacc.utexas.edu vaughn@tacc.utexas.edu, then hacked by wallen@tacc.utexas.edu for hikari
Summary:   Fast splice junction mapper for RNA-Seq reads.

## System Definitions
%include ./include/system-defines.inc
%include ./include/%{PLATFORM}/rpm-dir.inc
## Compiler Family Definitions
# %include ./include/%{PLATFORM}/compiler-defines.inc
## MPI Family Definitions
# %include ./include/%{PLATFORM}/mpi-defines.inc
%include ./include/name-defines.inc

%define MODULE_VAR  %{MODULE_VAR_PREFIX}TOPHAT

## PACKAGE DESCRIPTION
%description
TopHat is a fast splice junction mapper for RNA-Seq reads. It aligns RNA-Seq reads to mammalian-sized genomes using the ultra high-throughput short read aligner Bowtie, and then analyzes the mapping results to identify splice junctions between exons. 

## PREP
%prep
rm -rf $RPM_BUILD_ROOT/%{INSTALL_DIR}

## SETUP
%setup -n %{PNAME}-%{version}

## BUILD
%build

#------------------------------------------------
# INSTALL
#------------------------------------------------
%install

# Start with a clean environment
%include ./include/%{PLATFORM}/system-load.inc
mkdir -p $RPM_BUILD_ROOT/%{INSTALL_DIR}

#------------------------------------------------
## Install Steps Start
module purge
module load TACC
module swap $TACC_FAMILY_COMPILER gcc/5.2.0
module load boost/1.61.0

# Build SAMtools first
export TOPHAT_DIR=$(pwd)
wget http://downloads.sourceforge.net/project/samtools/samtools/1.2/samtools-1.2.tar.bz2
tar xjf samtools*
cd samtools*
MY_SAMTOOLS_DIR=$PWD
make
mkdir -p ./include/bam
cp ./*.h ./include/bam

cd $TOPHAT_DIR

./configure  --prefix=%{INSTALL_DIR} --enable-intel64 --with-boost=$TACC_BOOST_DIR --with-bam=$MY_SAMTOOLS_DIR --with-bam-libdir=$MY_SAMTOOLS_DIR LDFLAGS="-Wl,-rpath,$TACC_BOOST_LIB,-rpath,$GCC_LIB"

make BOOST_LDFLAGS="-L$TACC_BOOST_LIB -Wl,-rpath,$TACC_BOOST_LIB,-rpath,$GCC_LIB"

make DESTDIR=$RPM_BUILD_ROOT install
## Install Steps End
#------------------------------------------------

#------------------------------------------------
# MODULEFILE CREATION
#------------------------------------------------
rm   -rf $RPM_BUILD_ROOT%{MODULE_DIR}
mkdir -p $RPM_BUILD_ROOT%{MODULE_DIR}

#------------------------------------------------
## Modulefile Start
cat   >  $RPM_BUILD_ROOT%{MODULE_DIR}/%{version}.lua << 'EOF'
help(
[[
The %{PNAME} module file defines the following environment variables:
%{MODULE_VAR}_DIR and %{MODULE_VAR}_BIN for the location of the %{PNAME}
distribution.

Version %{version}
]]
)

whatis("Name: %{PNAME}")
whatis("Version: %{version}")
whatis("Category: computational biology, genomics")
whatis("Keywords: Biology, Genomics, RNAseq, Transcriptome profiling, Alignment")
whatis("URL: http://tophat.cbcb.umd.edu/")
whatis("Description: TopHat2 is a fast splice junction mapper for RNA-Seq reads. It aligns RNA-Seq reads to mammalian-sized genomes using the ultra high-throughput short read aligner Bowtie, and then analyzes the mapping results to identify splice junctions between exons.")

prepend_path("PATH",              "%{INSTALL_DIR}/bin")
setenv (     "%{MODULE_VAR}_DIR", "%{INSTALL_DIR}")
setenv (     "%{MODULE_VAR}_BIN", "%{INSTALL_DIR}/bin")

prereq ("bowtie","boost")

EOF
## Modulefile End
#------------------------------------------------

## Lua syntax check
if [ -f $SPEC_DIR/checkModuleSyntax ]; then
    $SPEC_DIR/checkModuleSyntax $RPM_BUILD_ROOT/%{MODULE_DIR}/%{version}.lua
fi

## VERSION FILE
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
#%files -n %{name}-%{comp_fam_ver}
%files 

# Define files permisions, user and group
%defattr(755,root,root,-)
%{INSTALL_DIR}
%{MODULE_DIR}

## CLEAN UP
%clean
rm -rf $RPM_BUILD_ROOT

