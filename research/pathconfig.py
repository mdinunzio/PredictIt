import os
import sys


# File locations
this_loc = __file__
parent_dir = os.path.abspath(os.path.join(this_loc, '..'))
main_dir = os.path.abspath(os.path.join(parent_dir, '..', 'main'))

sys.path.append(main_dir)
