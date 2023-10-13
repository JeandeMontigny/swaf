import os, sys, inspect, neo
import numpy as np
import quantities as pq
import matplotlib.pyplot as plt
from scipy import signal

from .utils import *

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
    def plot_analogsig(self, t_start, t_stop, plot_stim=True, show_plot=False, plot_save_path=""):
        # catch out of recording errors
        self.check_t(t_start, t_stop)

        # get array id corresponding to t_start and t_stop
        id_start = int((t_start-float(self.segment.t_start)) * float(self.sampling_rate))
        id_stop = int((t_stop-float(self.segment.t_start)) * float(self.sampling_rate))

        plt.plot(self.segment.analogsignals[2].times[id_start:id_stop], self.signal[id_start:id_stop], color='k')
        plt.xlabel(f"Time ({self.segment.analogsignals[2].times.units.dimensionality.string})")
        plt.ylabel(f"{self.segment.analogsignals[2].units.dimensionality.string}")

        if plot_stim and len(self.stim_trigger_times) > 0:
            # get stim within t_start and t_stop
            stim_idx = np.where((self.stim_trigger_times > t_start) & (self.stim_trigger_times < t_stop))
            # plot stimulation times
            plt.vlines(self.stim_trigger_times[stim_idx], -6, -5.5, colors='r')

        if len(plot_save_path) > 0:
            if not plot_save_path[len(plot_save_path)-1] == "/":
                plot_save_path = plot_save_path + "/"
            # check that folder exists. if not, create it
            if not os.path.isdir(plot_save_path):
                os.makedirs(plot_save_path)
            plot_save_path = plot_save_path + "analog-signal_" + str(t_start) + "-" + str(t_stop) + ".png"
            plt.savefig(plot_save_path, dpi=720)

        if show_plot:
            plt.show()

    # ---------------- #
    def get_ave_waveform(self, t_start, t_stop, show_plot=False, plot_save_path=""):
        # catch out of recording errors
        self.check_t(t_start, t_stop)

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

        if show_plot or len(plot_save_path) > 0:
            self.plot_ave_waveform(ave_waveform, t_start, t_stop, show_plot, plot_save_path)

        return ave_waveform

    # ---------------- #
    def plot_ave_waveform(self, ave_waveform, t_start, t_stop, show_plot, plot_save_path):
        # catch out of recording errors
        self.check_t(t_start, t_stop)

        plt.figure()
        # centred arround stim time
        plt.plot([t/self.sampling_rate for t in range(-int(np.ceil(0.1*float(self.sampling_rate))/2), int(np.ceil(0.1*float(self.sampling_rate))/2))], ave_waveform, c='k')
        plt.xlabel(f"Time ({self.segment.analogsignals[2].times.units.dimensionality.string})")
        plt.ylabel(f"{self.segment.analogsignals[2].units.dimensionality.string}")
        plt.title("Waveform average: "+str(t_start)+" to "+str(t_stop)+" s")
        plt.tight_layout()

        if len(plot_save_path) > 0:
            if not plot_save_path[len(plot_save_path)-1] == "/":
                plot_save_path = plot_save_path + "/"
            # check that folder exists. if not, create it
            if not os.path.isdir(plot_save_path):
                os.makedirs(plot_save_path)
            plot_save_path = plot_save_path + "waveform-ave_" + str(t_start) + "-" + str(t_stop) + ".png"
            plt.savefig(plot_save_path, dpi=720)

        if show_plot:
            plt.show()

    # ---------------- #
    def check_t(self, t_start, t_stop):
        if t_start < self.segment.t_start:
            raise SystemExit("Error in \'" + inspect.stack()[1].function + "\' function: Specified t_start \'" + str(t_start) + "\' is smaller than the extracted recording stop time \'" + str(float(self.segment.t_start))+ "\'")
        if t_stop > self.segment.t_stop:
            raise SystemExit("Error in \'" + inspect.stack()[1].function + "\' function: Specified t_stop \'" + str(t_stop) + "\' is larger than the extracted recording stop time \'" + str(float(self.segment.t_stop))+ "\'")

# ---------------------------------------------------------------- #
def read_file(file_path, t_start=0, t_stop="all"):
    Recording = Spike_recording(file_path)
    Recording.read(file_path, t_start, t_stop)

    return Recording
