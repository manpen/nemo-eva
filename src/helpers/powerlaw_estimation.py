import numpy as np
import powerlaw
import helpers.tail_estimation as pl

#def powerlaw_fit(degrees):
#    fit = powerlaw.Fit(degrees, fit_method='Likelihood', verbose=False)
#    return fit.alpha

def powerlaw_fit(degrees):
    degrees = np.array(degrees)
    # Apply noise
    degrees = pl.add_uniform_noise(degrees, p=1)
    degrees[::-1].sort()
    try:
        result = pl.hill_estimator(degrees)
        alpha = 1 + 1 / result[3]
    except:
        alpha = 2.1
    return alpha