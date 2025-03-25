# lightweight noxfile that calls common noxfile in
# https://bitbucket-mob.mplatform.co.uk/projects/DLIB/repos/digital-nox/browse/noxfile.py

import runpy
import os

# get common noxfile location as set by dignox
lib_noxfile = os.environ["LIB_NOXFILE"]

# supply dynamic REPO OPTIONS to common noxfile
os.putenv("LIBRARY", "src")

# run common noxfile
runpy.run_path(
    lib_noxfile,
    init_globals=globals(),
)
