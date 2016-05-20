# Support for the lmod system
if [ -f "$BASH_ENV" ]; then
  . $BASH_ENV
fi

if [ -n "$MODULEPATH" ]; then
  module purge
  clearMT
  export MODULEPATH=/opt/apps/modulefiles
fi

module load TACC
