import powerlaw

def powerlaw_fit(degrees):
    fit = powerlaw.Fit(degrees, fit_method='Likelihood', verbose=False)
    return fit.alpha