# Minimum upload success percentage of available hosts to ensure proper file redundancy
MIN_FILE_REDUNDANCY      = 0.6

try:
    from local_settings import *
except ImportError:
    pass
