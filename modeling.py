import numpy as np
from scipy.optimize import curve_fit


def modified_gauss_func(x, x0, a, sigma, H, r):
        return -a * np.exp( -np.absolute(x - x0)**r / (2 * sigma **2) ) + H

def modified_gauss_fit(x_data=[], y_data=[]):
    x_data = np.array(x_data)
    y_data = np.array(y_data)
    
    mean = sum(x_data * y_data) / sum(y_data)
    sigma = np.sqrt(sum(y_data * (x_data - mean) ** 2) / sum(y_data))

    x0 = 8250
    a = 5e-7
    H = 7e-7
    r = 1.5

    try:
        popt, pcov = curve_fit(modified_gauss_func, x_data, y_data, p0=[x0, a, sigma, H, r])
        perr = np.sqrt(np.diag(pcov))

        ym = modified_gauss_func(x_data, *popt)
        ym_error = modified_gauss_func(x_data, *(popt + perr))
    except:
        ym = None
        ym_error = None
        r = None
        print("could not model data")

    return ym, ym_error