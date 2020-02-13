import os
import sys


# File locations
cfg_loc = __file__
research_dir = os.path.abspath(os.path.join(cfg_loc, '..'))
main_dir = os.path.abspath(os.path.join(research_dir, '..', 'main'))

sys.path.append(main_dir)
