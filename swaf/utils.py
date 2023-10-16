import neo
import matplotlib.pyplot as plt

# ---------------------------------------------------------------- #
def get_t_start_t_stop(file_name, t_start=0, t_end="all"):
    # lazy option so data are not actually loaded
    data = neo.io.Spike2IO(filename=file_name).read(lazy=True)
    seg_sampling_rate = data[0].segments[0].analogsignals[2].sampling_rate
    seg_t_start = data[0].segments[0].t_start
    seg_t_stop = data[0].segments[0].t_stop

    if t_start <= 0:
        # need to add at least 2 data point after t_start, otherwise 't_start is outside' error during read_segment()
        t_start = seg_t_start + (2/float(seg_sampling_rate))*pq.s
    if t_end == "all" or t_end >= seg_t_stop:
        # need to decrease t_end otherwise 't_stop is outside' error during read_segment()
        t_end = seg_t_stop - (10/float(seg_sampling_rate))*pq.s

    return t_start, t_end

# ---------------------------------------------------------------- #
def plot_dg_slope(ave_waveform, Recording, point_list=[(615, 645)], show_plot=True, plot_save_path=""):
    # 615 = 0.009024s post stim ; 645 = 0.011904s post stim
    # new figure
    fig = plt.figure()
    # slope index number
    si = 0
    for points in point_list:
        si += 1
        s_start = points[0]
        s_stop = points[1]
        point_a = [s_start, ave_waveform[s_start]]
        point_b = [s_stop, ave_waveform[s_stop]]
        # plot centred arround stim time
        t_point_a = (point_a[0] - (len(ave_waveform)/2))/float(Recording.sampling_rate)
        t_point_b = (point_b[0] - (len(ave_waveform)/2))/float(Recording.sampling_rate)

        slope = round((point_b[1] - point_a[1]) / (point_b[0]/float(Recording.sampling_rate)  - point_a[0]/float(Recording.sampling_rate)), 3)

        # if first slope plot waveform
        if si == 1:
            plt.plot([t/float(Recording.sampling_rate) for t in range(int(-len(ave_waveform)/2), int(len(ave_waveform)/2))], ave_waveform, color='k')
        # plot waveform section between point a and b
        plt.plot([t/float(Recording.sampling_rate) for t in range(int(s_start-len(ave_waveform)/2), int(s_stop-len(ave_waveform)/2))], ave_waveform[s_start:s_stop], color='r')

        # plot point a and b
        plt.plot(t_point_a, point_a[1], marker='o', color='b', markersize=3)
        # plt.text(t_point_a, point_a[1], round(t_point_a, 5), color='b')
        plt.plot(t_point_b, point_b[1], marker='o', color='b', markersize=3)
        # plt.text(t_point_b, point_b[1], round(t_point_b, 5), color='b')

        # plot slope
        plt.plot([t_point_a, t_point_b], [point_a[1], point_b[1]], color='b', label="segment "+str(si)+" slope: "+str(slope))

        # TODO: txt_x and txt_y: + f * 90° vector of slope
        txt_x = (t_point_a + t_point_b) / 2
        txt_y = (ave_waveform[s_start] + ave_waveform[s_stop]) / 2
        plt.text(txt_x, txt_y, si, color='b')

    plt.legend(loc='upper left')

    if show_plot:
        plt.show()
    if len(plot_save_path) > 0:
        # NOTE: no path check or auto naming
        plt.savefig(plot_save_path, dpi=720)
