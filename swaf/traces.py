import os, sys, pickle, neo
import numpy as np
import quantities as pq
import matplotlib.pyplot as plt
from scipy import signal

from .utils import *

import psutil, time

# ---------------------------------------------------------------- #
class Spike_recording:

    def __init__(self, rec_path):
        self.path = rec_path

    # ---------------- #
    def read(self, file_path, t_start, t_stop):
        # get t_start, t_stop values
        t_start, t_stop = get_t_start_t_stop(file_path, t_start, t_stop)

        reader = neo.io.Spike2IO(filename=file_path)
        self.segment = reader.read_segment(time_slice=(t_start, t_stop))
        self.t_start = self.segment.t_start
        self.t_stop = self.segment.t_stop
        self.sampling_rate = self.segment.analogsignals[2].sampling_rate
        # get stimulation trigger times
        self.stim_trigger_times = np.array(self.segment.events[0])
        # transpose the analog signal to get an array of shape [2, x], instead of [x, 2]
        self.signal = np.transpose(self.segment.analogsignals[2])[1]
        # get and plot signal

    # ---------------- #
    def plot_analogsig(self, plot_stim=True):
        plt.plot(self.segment.analogsignals[2].times, self.signal, color='k')
        plt.xlabel(f"Time ({self.segment.analogsignals[2].times.units.dimensionality.string})")
        plt.ylabel(f"{self.segment.analogsignals[2].units.dimensionality.string}")

        if plot_stim and len(self.stim_trigger_times) > 0:
            # plot stimulation times
            for trigger_time in self.stim_trigger_times:
                plt.vlines(trigger_time, -6, -5.5, colors='r')

        plt.show()

    # ---------------- #
    def get_ave_waveform(self, t_start, t_stop, plot=False):
        # catch out of recording errors
        if t_start < self.segment.t_start:
            raise ValueError('Specified t_start', t_start, 'is smaller than the extracted recording start time', self.segment.t_start, 'in function get_ave_waveform()')
        if t_stop > self.segment.t_stop:
            raise ValueError('Specified t_stop', t_stop, 'is larger than the extracted recording stop time', self.segment.t_stop, 'in function get_ave_waveform()')

        # get stims idx between t_start and t_stop
        stim_times_idx = np.where((self.stim_trigger_times > t_start) & (self.stim_trigger_times < t_stop))[0]
        waveforms = np.zeros(shape=(len(stim_times_idx), int(np.ceil(0.1*float(self.sampling_rate)))))

        # for each stim time between t_start and t_stop
        for i in range(len(stim_times_idx)):
            stim_time = self.stim_trigger_times[stim_times_idx[i]]
            # get signal array's id corresponding to this stim time
            signal_stim_id = (stim_time-float(self.segment.t_start)) * float(self.sampling_rate)
            # get data +-0.05s arround that signal id stim time
            data = self.signal[int(signal_stim_id-(0.05*float(self.sampling_rate))):int(signal_stim_id+(0.05*float(self.sampling_rate)))]

            # size of segment can vary (from read_segment()), so add array's last value at the end of array if size < np.ceil(0.1*float(seg_sampling_rate)))-len(data)
            if len(data) < int(np.ceil(0.1*float(self.sampling_rate))):
                data = np.append(data, [data[len(data)-1] for addval in range(0, int(np.ceil(0.1*float(self.sampling_rate)))-len(data))])
            waveforms[i] = data

        waveforms = np.transpose(waveforms)
        ave_waveform = np.average(waveforms, axis=1)

        if plot:
            # centred arround stim time
            plt.plot([t/self.sampling_rate for t in range(-int(np.ceil(0.1*float(self.sampling_rate))/2), int(np.ceil(0.1*float(self.sampling_rate))/2))], ave_waveform, c='k')
            plt.xlabel(f"Time ({self.segment.analogsignals[2].times.units.dimensionality.string})")
            plt.ylabel(f"{self.segment.analogsignals[2].units.dimensionality.string}")
            plt.title("Waveform average: "+str(t_start)+" to "+str(t_stop)+" s")
            plt.tight_layout()
            plt.savefig("results/waveform-ave_" + str(t_start) + "-" + str(t_stop) + ".png", dpi=720)
            # plt.show()

        return ave_waveform

# ---------------------------------------------------------------- #
def read_file(file_path, t_start=0, t_stop="all"):
    Recording = Spike_recording(file_path)
    Recording.read(file_path, t_start, t_stop)

    return Recording
