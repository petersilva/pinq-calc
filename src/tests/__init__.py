import os

# Prevent matplotlib from trying to start an interactive GUI backend during unit tests,
# which can cause the unittest runner to hang when tests exit.
try:
    import matplotlib
    matplotlib.use('Agg')
except ImportError:
    pass
