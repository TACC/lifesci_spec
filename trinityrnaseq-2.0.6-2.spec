###
### PLEASE ONLY USE THIS SPEC FILE ON HIKARI
###
#------------------------------------------------
# INITIAL DEFINITIONS
#------------------------------------------------
%define     PNAME trinityrnaseq
Version:    2.0.6
Release:    2
License:    BSD
Group:      Applications/Life Sciences
Source:     v%{version}.tar.gz
Packager:   TACC - gzynda@tacc.utexas.edu, then hacked by wallen@tacc.utexas.edu for hikari
Summary:    Trinity De novo RNA-Seq Assembler

## System Definitions
%include ./include/system-defines.inc
%include ./include/%{PLATFORM}/rpm-dir.inc
## Compiler Family Definitions
#%include ./include/%{PLATFORM}/compiler-defines.inc
## MPI Family Definitions
# %include ./include/%{PLATFORM}/mpi-defines.inc
## directory and name definitions for relocatable RPMs
%include ./include/name-defines.inc

%define MODULE_VAR  %{MODULE_VAR_PREFIX}TRINITY

%define __os_install_post    \
    /usr/lib/rpm/redhat/brp-compress \
    %{!?__debug_package:/usr/lib/rpm/redhat/brp-strip %{__strip}} \
    /usr/lib/rpm/redhat/brp-strip-static-archive %{__strip} \
    /usr/lib/rpm/redhat/brp-strip-comment-note %{__strip} %{__objdump} \
%{nil}

## PACKAGE DESCRIPTION
%description
Trinity, developed at the Broad Institute and the Hebrew University of Jerusalem, represents a novel method for the efficient and robust de novo reconstruction of transcriptomes from RNA-seq data. Trinity combines three independent software modules: Inchworm, Chrysalis, and Butterfly, applied sequentially to process large volumes of RNA-seq reads. Trinity partitions the sequence data into many individual de Bruijn graphs, each representing the transcriptional complexity at at a given gene or locus, and then processes each graph independently to extract full-length splicing isoforms and to tease apart transcripts derived from paralogous genes.

## PREP
%prep
rm -rf $RPM_BUILD_ROOT/%{INSTALL_DIR}
rm -rf $RPM_BUILD_ROOT/%{MODULE_DIR}

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
module swap $TACC_FAMILY_COMPILER gcc/4.9.3
make -j 4

rm -rf Analysis/DifferentialExpression/deprecated
rm -rf Analysis/DifferentialExpression/cluster_sample_data
rm -rf Butterfly/prev_vers
rm -rf Butterfly/src/sample_data
rm -rf Butterfly/src/src
rm -rf Chrysalis/obj
rm -rf hpc_conf
rm -rf Inchworm/src
rm -rf sample_data
rm -rf trinity-plugins/parafly-code/src
find . -name \*.tar.gz | xargs -n 1 rm
find . -name \*.[ch]pp | xargs -n 1 rm
find . -name \*.cc | xargs -n 1 rm
find . -name \*.[oc] | xargs -n 1 rm
cp -r * $RPM_BUILD_ROOT/%{INSTALL_DIR}/
chmod -R a+rX $RPM_BUILD_ROOT/%{INSTALL_DIR}

## Install Steps End

#------------------------------------------------
# MODULEFILE CREATION
#------------------------------------------------
rm   -rf $RPM_BUILD_ROOT/%{MODULE_DIR}
mkdir -p $RPM_BUILD_ROOT/%{MODULE_DIR}

#------------------------------------------------
## Modulefile Start
cat > $RPM_BUILD_ROOT/%{MODULE_DIR}/%{version}.lua << 'EOF'
help (
[[
The %{PNAME} module file defines the following environment variables:
%{MODULE_VAR}_DIR, %{MODULE_VAR}_BUTTERFLY, %{MODULE_VAR}_CHRYSALIS, %{MODULE_VAR}_INCHWORM and %{MODULE_VAR}_INCHWORM_BIN for the location of the %{PNAME} distribution.

Please refer to http://trinityrnaseq.sourceforge.net/#running_trinity for help running trinity.

Version %{version}
]])
whatis("Name: ${PNAME}")
whatis("Version: %{version}")
whatis("Category: computational biology, transcriptomics")
whatis("Keywords: Biology, Assembly, RNAseq, Transcriptome")
whatis("URL: http://trinityrnaseq.sourceforge.net/")
whatis("Description: Package for RNA-Seq de novo Assembly")

prepend_path("PATH"       	, "%{INSTALL_DIR}/")
setenv("%{MODULE_VAR}_DIR"	, "%{INSTALL_DIR}/")
setenv("%{MODULE_VAR}_BUTTERFLY", "%{INSTALL_DIR}/Butterfly")
setenv("%{MODULE_VAR}_CHRYSALIS", "%{INSTALL_DIR}/Chrysalis")
setenv("%{MODULE_VAR}_INCHWORM"	, "%{INSTALL_DIR}/Inchworm")
setenv("%{MODULE_VAR}_INCHWORM_BIN", "%{INSTALL_DIR}/Inchworm/bin")
setenv("%{MODULE_VAR}_UTIL"	, "%{INSTALL_DIR}/util")
setenv("%{MODULE_VAR}_PLUGINS"	, "%{INSTALL_DIR}/trinity-plugins")
EOF

cat >> $RPM_BUILD_ROOT/%{MODULE_DIR}/%{version}.lua << 'EOF'
prereq("samtools","gcc","bowtie")
EOF

## Modulefile End
#------------------------------------------------

## Lua syntax check
if [ -f $SPEC_DIR/checkModuleSyntax ]; then
    $SPEC_DIR/checkModuleSyntax $RPM_BUILD_ROOT/%{MODULE_DIR}/%{version}.lua
fi

#------------------------------------------------
# VERSON FILE
#------------------------------------------------
cat > $RPM_BUILD_ROOT%{MODULE_DIR}/.version.%{version} << 'EOF'
#%Module3.1.1#################################################
##
## version file for %{name}-%{version}
##

set     ModulesVersion      "%{version}"
EOF

#------------------------------------------------
# FILES SECTION
#------------------------------------------------
%files
#%files 

# Define files permisions, user and group
%defattr(-,root,install,)
%{INSTALL_DIR}
%{MODULE_DIR}
#------------------------------------------------
# CLEAN UP SECTION
#------------------------------------------------
%post
%clean
# Remove the installation files now that the RPM has been generated
cd /tmp && rm -rf $RPM_BUILD_ROOT
