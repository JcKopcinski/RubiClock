from tqdm import tqdm
import time

from graphics import PlotObject
import modeling

import numpy as np


class FreqAnalysis:
    def __init__(self, interface, freq_base) -> None:
        self.interface = interface #sets the clock interface
        self.freq_base = freq_base #sets the base frequency

    # return information about scanned data
    def single_scan(self, detune_low, detune_high):

        # get raw data into two arrays
        freq_data, intensity_data = self.interface.get_data( #
            self.freq_base, 
            detune_low + self.freq_base, 
            detune_high + self.freq_base)
        
        min_index = freq_data.index(8150) #compresses the x data lists into start x value (freq)
        max_index = freq_data.index(8300) #compresses the x data list into end x value (freq)
        
        min_y = min(intensity_data[min_index:max_index]) #finds the minimum intensity between the min_index and max_index
        min_y_index = intensity_data.index(min_y) #grabs the index value at the min intensity
        

        W = 20
        x_data = freq_data[min_y_index-W : min_y_index+W]
        y_data = intensity_data[min_y_index-W : min_y_index+W]

        fit_y, fit_y_error = modeling.modified_gauss_fit(
            x_data=x_data,
            y_data=y_data)

        scan_plot = PlotObject(x_label="detune freq [Hz]", y_label="Intensity")
        scan_plot.plot_points(x_data=freq_data, y_data=intensity_data, label="measured")
        scan_plot.plot_line(x_data=x_data, y_data=fit_y, label="modified guass fit")
        scan_plot.show_plot()

        # if fit_y is None:
        #     return None, None
        
        # min_y_index = fit_y.argmin()
        # return x_data[min_y_index], abs(fit_y[min_y_index] / (fit_y_error[min_y_index] * 2))


    # continous scanning of clock
    def cont_scan(self, detune_low, detune_high, rounds=1): #TODO perform ZSWEEP by passing in a high nimber of rounts to continuous scan, one for each in current step. Or, create new function called zsweep
        start_t = time.time()
        res_freqs = []
        res_freqs_error = []
        res_times = []

        for _ in tqdm(range(rounds), desc="scanning..."):
            scan, perr = self.single_scan(
                detune_low=detune_low, 
                detune_high=detune_high)

            if scan is not None:
                res_freqs.append(scan)
                res_freqs_error.append(perr)
                res_times.append(time.time() - start_t) 


        plot = PlotObject(
            x_label="ellapsed time [S]",
            y_label="detuning frequency [Hz]",
            show_annotate=True)
        
        print(res_freqs)
        print(res_freqs_error)

        plot.plot_points(res_times, res_freqs, res_freqs_error)
        plot.show_plot()