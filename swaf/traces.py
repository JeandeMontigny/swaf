import os, sys, inspect, neo
import numpy as np
import scipy.signal as sig
import quantities as pq
import matplotlib.pyplot as plt

from .utils import *

# ---------------------------------------------------------------- #
class Spike_Recording:

    def __init__(self, rec_path):
        self.path = rec_path

    # ---------------- #
    def read(self, file_path, t_start, t_stop):
        """
        TODO
        """
        # get t_start, t_stop values
        t_start, t_stop = get_t_start_t_stop(file_path, t_start, t_stop)

        reader = neo.io.Spike2IO(filename=file_path)
        self.segment = reader.read_segment(lazy=True)
        self.signal_proxy = self.segment.analogsignals[2]
        self.sampling_rate = self.segment.analogsignals[2].sampling_rate
        # get stimulation trigger times
        self.stim_trigger_times = np.array(self.segment.events[0].load(time_slice=(t_start, t_stop)))
        # signal is not loaded (read_segment lazy option). contains whole data for this time window, not just the analog signal
        self.loaded_sig = None
        self.click_coords = []
        self.key_shift = False

    # ---------------- #
    def get_signal(self, t_start, t_stop, return_sig=True):
        """
        TODO
        """
        self.loaded_sig = self.signal_proxy.load(time_slice=(t_start, t_stop))

        if return_sig:
            # transpose the analog signal to get an array of shape [2, x], instead of [x, 2]
            return np.transpose(self.loaded_sig)[1]

    # ---------------- #
    def plot_analogsig(self, t_start, t_stop, plot_stim=True, show_plot=False, plot_save_path="", create_path=""):
        """
        TODO
        """
        # catch out of recording errors
        self.check_t(t_start, t_stop)
        #  fetched signal (read_segment lazy option)
        self.get_signal(t_start, t_stop, return_sig=False)

        fig = plt.subplot()
        # get array id corresponding to t_start and t_stop
        id_start = int((t_start-float(self.loaded_sig.t_start)) * float(self.sampling_rate))
        id_stop = int((t_stop-float(self.loaded_sig.t_start)) * float(self.sampling_rate))

        # transpose the analog signal to get an array of shape [2, x], instead of [x, 2]
        plt.plot(self.loaded_sig.times[id_start:id_stop], np.transpose(self.loaded_sig)[1][id_start:id_stop], color='k')
        plt.xlabel(f"Time ({self.loaded_sig.times.units.dimensionality.string})")
        plt.ylabel(f"{self.loaded_sig[2].units.dimensionality.string}")
        fig.spines['right'].set_visible(False)
        fig.spines['top'].set_visible(False)
        plt.tight_layout()

        if plot_stim and len(self.stim_trigger_times) > 0:
            # get stim within t_start and t_stop
            stim_idx = np.where((self.stim_trigger_times > t_start) & (self.stim_trigger_times < t_stop))
            # plot stimulation times
            plt.vlines(self.stim_trigger_times[stim_idx], -6, -5.5, colors='r')

        if len(plot_save_path) > 0 and check_save_path(plot_save_path, create_path):
            plot_save_path = get_plot_name(plot_save_path, "analog-signal_"+str(t_start)+"-"+str(t_stop)+".png")
            plt.savefig(plot_save_path, dpi=720)
            if not show_plot:
                plt.close()
        if show_plot:
            plt.show()

    # ---------------- #
    def get_ave_waveform(self, t_start, t_stop, show_plot=False, anotate=False, plot_save_path="", create_path=""):
        """
        TODO
        """
        # catch out of recording errors
        self.check_t(t_start, t_stop)
        # get the stim trigget time for the specified time window, and not for the whole rec segment
        window_stim_trigger_times = np.array(self.segment.events[0].load(time_slice=(t_start, t_stop)))
        waveform_length = int(np.floor(0.1*float(self.sampling_rate)))
        waveforms = np.zeros(shape=(len(window_stim_trigger_times), waveform_length))

        # for each stim time between t_start and t_stop
        for i in range(len(window_stim_trigger_times)):
            # get data +-0.05s arround that signal stim time and transpose it
            data =  np.transpose(self.signal_proxy.load(time_slice=(window_stim_trigger_times[i]-0.05, window_stim_trigger_times[i]+0.05)))[1]
            # size of segment can vary (from neo load()), so add array's last value at the end of array if size < waveform_length
            if len(data) < waveform_length:
                data = np.append(data, [data[len(data)-1] for addval in range(0, waveform_length-len(data))])
            waveforms[i] = data

        ave_waveform = np.average(waveforms, axis=0)

        waveform_time = (np.asarray([range(int(np.floor(-len(ave_waveform)/2)), int(np.floor(len(ave_waveform)/2)))])/float(self.sampling_rate))[0]
        Ave_Waveform = Waveform(ave_waveform, waveform_time, t_start, t_stop, self.sampling_rate)

        if show_plot or anotate or len(plot_save_path) > 0:
            if len(plot_save_path) > 0:
                plot_save_path = get_plot_name(plot_save_path, "waveform-ave_" + str(t_start) + "-" + str(t_stop) + ".png")
            Ave_Waveform.plot_waveform(show_plot, anotate, plot_save_path, create_path)

        return Ave_Waveform

    # ---------------- #
    def check_t(self, t_start, t_stop):
        if t_start < self.segment.t_start:
            raise SystemExit("Error in \'" + inspect.stack()[1].function + "\' function: Specified t_start \'" + str(t_start) + "\' is smaller than the extracted recording stop time \'" + str(float(self.segment.t_start))+ "\'")
        if t_stop > self.segment.t_stop:
            raise SystemExit("Error in \'" + inspect.stack()[1].function + "\' function: Specified t_stop \'" + str(t_stop) + "\' is larger than the extracted recording stop time \'" + str(float(self.segment.t_stop))+ "\'")

# ---------------------------------------------------------------- #
def read_file(file_path, t_start=0, t_stop="all"):
    """
    TODO
    """
    Recording = Spike_Recording(file_path)
    Recording.read(file_path, t_start, t_stop)

    return Recording

# ---------------------------------------------------------------- #
class Waveform:

    def __init__(self, waveform, waveform_time, t_start, t_stop, sampling_rate):
        self.waveform = waveform
        self.time = waveform_time
        self.t_start = t_start
        self.t_stop = t_stop
        self.sampling_rate = sampling_rate
        self.click_coords = []
        self.key_shift = False

    # ---------------- #
    def get_waveform_peaks(self, i_start=None, i_stop=None, height=None, threshold=None, exclusion_dist=30, prominence=0.01, width=None, show_plot=False, plot_save_path="", create_path=""):
        """
        TODO
        """
        if show_plot or len(plot_save_path) > 0:
            fig = plt.subplot()
            plt.plot(self.waveform, color='k')

        if i_start == None:
            i_start = int(len(self.waveform) / 2) + 15
        if i_stop == None:
            i_stop = int(len(self.waveform) / 2) + 350

        # find positive peaks
        p_peaks, p_peaks_dict = sig.find_peaks(self.waveform[i_start:i_stop], height=height, threshold=threshold, distance=exclusion_dist, prominence=prominence, width=width)
        # find negative peaks
        n_peaks, n_peaks_dict = sig.find_peaks(-self.waveform[i_start:i_stop], height=height, threshold=threshold, distance=exclusion_dist, prominence=prominence, width=width)

        # add i_start to get correct position on whole sig
        p_peaks = p_peaks+i_start
        n_peaks = n_peaks+i_start

        # if there is no negative peak before the first positive peak
        if len(n_peaks)==0 or min(n_peaks) > min(p_peaks):
            # add a negative peak point so we can calculate the first slope position
            n_peaks = [i_start+15, *n_peaks]
        # merge and sort negative and positive peaks in one array
        peaks = np.sort([*p_peaks, *n_peaks])

        if show_plot or len(plot_save_path) > 0:
            # plot peaks (positive in red, negative in blue) and slopes middle position (grey)
            for i in range(len(p_peaks)):
                plt.plot(p_peaks[i], self.waveform[p_peaks[i]], 'o', color='r')
            for i in range(len(n_peaks)):
                plt.plot(n_peaks[i], self.waveform[n_peaks[i]], 'o', color='b')
            for i in range(len(peaks)-1):
                mean_i = int((peaks[i] + peaks[i+1])/2)
                plt.plot(mean_i, self.waveform[mean_i], 'o', color='grey')

            plt.xlabel("Frames")
            plt.ylabel("V")
            plt.ylim(-5.1, 5.1)
            fig.spines['right'].set_visible(False)
            fig.spines['top'].set_visible(False)
            plt.tight_layout()

            if len(plot_save_path) > 0 and check_save_path(plot_save_path, create_path):
                plot_save_path = get_plot_name(plot_save_path, "waveform_peaks.png")
                plt.savefig(plot_save_path, dpi=720)
                if not show_plot:
                    plt.close()
            if show_plot:
                plt.show()

        self.peaks = peaks
        return peaks

    # ---------------- #
    def get_waveform_slope_list(self, dist=5, exclusion_dist=30):
        """
        TODO
        """
        peaks = self.get_waveform_peaks()

        slope_list = []
        for i in range(len(peaks)-1):
            peak_a = peaks[i]
            peak_b = peaks[i+1]
            mean_i = int((peak_a + peak_b) / 2)
            slope_list.append((mean_i-dist, mean_i+dist))

        return slope_list

    # ---------------- #
    def get_waveform_slope(self, point_list=[], print_val=False, exclusion_dist=30, show_plot=False, plot_save_path="", create_path=""):
        """
        TODO
        """
        # if no slope point list is specified, call get_waveform_slope_list() to get a list
        if len(point_list) == 0:
            point_list = self.get_waveform_slope_list(exclusion_dist=exclusion_dist)
        if show_plot or len(plot_save_path) > 0:
            plt.figure()
            fig = plt.subplot()

        # store slopes values
        slope_val_list = []
        # slope index number
        si = 0
        for points in point_list:
            si += 1
            # check if times are expressed as seconds (value < 1) or frames
            s_start = int(np.floor((points[0]+0.05)*float(self.sampling_rate))) if points[0] < 1 else int(points[0])
            s_stop = int(np.floor((points[1]+0.05)*float(self.sampling_rate))) if points[1] < 1 else int(points[1])

            point_a = [s_start, self.waveform[s_start]]
            point_b = [s_stop, self.waveform[s_stop]]

            # calculate slope
            slope = round((point_b[1] - point_a[1]) / ((point_b[0] - point_a[0]) / float(self.sampling_rate)), 2)
            slope_val_list.append(([point_a[0], point_b[0]], slope))
            if print_val:
                print(point_a[0], "to", point_b[0], "slope:", slope)

            if show_plot or len(plot_save_path) > 0:
                # waveform plot is centred arround stim time
                t_point_a = (point_a[0] - (len(self.waveform)/2))/float(self.sampling_rate)
                t_point_b = (point_b[0] - (len(self.waveform)/2))/float(self.sampling_rate)
                # if first slope plot waveform
                if si == 1:
                    plt.plot(self.time, self.waveform, color='k')
                # plot waveform section between point a and b
                t_ab = (np.asarray([range(int(s_start-len(self.waveform)/2), int(s_stop-len(self.waveform)/2))])/float(self.sampling_rate))[0]
                plt.plot(t_ab, self.waveform[s_start:s_stop], color='r')
                # plot point a and b
                plt.plot(t_point_a, point_a[1], marker='o', color='b', markersize=3)
                # plt.text(t_point_a, point_a[1], round(t_point_a, 5), color='b')
                plt.plot(t_point_b, point_b[1], marker='o', color='b', markersize=3)
                # plt.text(t_point_b, point_b[1], round(t_point_b, 5), color='b')
                # plot slope
                plt.plot([t_point_a, t_point_b], [point_a[1], point_b[1]], color='b', label="segment "+str(si)+" slope: "+str(slope))

                # TODO: txt_x and txt_y: + f * 90° vector of slope
                txt_x = (t_point_a + t_point_b) / 2
                txt_y = (self.waveform[s_start] + self.waveform[s_stop]) / 2
                plt.text(txt_x, txt_y, si, color='b')

                plt.legend(loc='upper left')
                plt.xlabel("Time (s)")
                plt.ylabel("V")
                plt.ylim(-5.1, 5.1)
                fig.spines['right'].set_visible(False)
                fig.spines['top'].set_visible(False)
                plt.tight_layout()

        if len(plot_save_path) > 0 and check_save_path(plot_save_path, create_path):
            plot_save_path = get_plot_name(plot_save_path, "waveform_slope.png")
            plt.savefig(plot_save_path, dpi=720)
            if not show_plot:
                plt.close()
        if show_plot:
            plt.show()

        self.slope_val_list = slope_val_list
        return slope_val_list

    # ---------------- #
    def plot_waveform(self, show_plot=True, anotate=False, plot_save_path="", create_path=""):
        # TODO: click and drag misplaced point on anotation?
        """
        TODO
        """
        fig, ax = plt.subplots()
        plt.plot(self.time, self.waveform, color='k')
        plt.xlabel("Time (s)")
        plt.ylabel("V")
        # plt.title("Waveform average: "+str(t_start)+" to "+str(t_stop)+" s")
        plt.ylim(-5.1, 5.1)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        plt.tight_layout()

        if anotate:
            print("Use shit+click to anotate the plot")
            fig.canvas.mpl_connect('button_press_event', self.on_click)
            fig.canvas.mpl_connect('key_press_event', self.on_key_press)
            fig.canvas.mpl_connect('key_release_event', self.on_key_release)

        if len(plot_save_path) > 0 and check_save_path(plot_save_path, create_path):
            plot_save_path = get_plot_name(plot_save_path, "waveform.png")
            plt.savefig(plot_save_path, dpi=720)
            if not show_plot:
                plt.close()
        if show_plot or anotate:
            plt.show()

    # ---------------- #
    def on_key_press(self, event):
       if event.key == 'shift':
           self.key_shift = True

    def on_key_release(self, event):
       if event.key == 'shift':
           self.key_shift = False

    # ---------------- #
    def on_click(self, event):
        if not self.key_shift:
            return
        coord_x, coord_y = round(event.xdata, 5), round(event.ydata, 5)
        # print("clicked on coord:", f'x = {ix}, y = {iy}')
        self.click_coords.append([coord_x, coord_y])
        # draw a blue point at click location and a label
        plt.plot(coord_x, coord_y, marker='o', color='b', markersize=3)
        plt.text(coord_x, coord_y+0.2, "P"+str(len(self.click_coords)), color='b')

        # print slope for every 2 points
        if len(self.click_coords) > 1 and len(self.click_coords) % 2 == 0:
            # first of the 2 lasts clicked points
            point_a = self.click_coords[len(self.click_coords)-2]
            # last point
            point_b = self.click_coords[len(self.click_coords)-1]
            slope = round((point_b[1] - point_a[1]) / (point_b[0] - point_a[0]), 3)
            print("point", len(self.click_coords)-1, "to point", len(self.click_coords), "slope:", slope, "\n( coord", point_a, "to", point_b, ")")
            # plot line between the two points and add label for this slope
            plt.plot([point_a[0], point_b[0]], [point_a[1], point_b[1]], color='b', label="P"+str(len(self.click_coords)-1)+" to P"+str(len(self.click_coords))+" slope: "+str(slope))
            # show legend for slope lines
            plt.legend()

        plt.draw()

# ---------------------------------------------------------------- #
def get_ave_waveform_from_rec(file_path, t_start, t_stop, anotate=False):
    """
    TODO
    """
    Ave_Waveform = read_file(file_path, t_start, t_stop).get_ave_waveform(t_start, t_stop, anotate=anotate)

    return Ave_Waveform
