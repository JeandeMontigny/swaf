import neo, os

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
def check_save_path(save_path, create=""):
    # if save_path contains file name, extract only directory path
    if save_path[len(save_path)-4:len(save_path)] == ".png":
        save_path = os.path.dirname(save_path)
    # check that folder exists. if not, create it
    if not os.path.isdir(save_path):
        if len(create) == 0:
            create = input("Path \'" + save_path + "\' does not exist. Do you want to create it? y/n: ")
        if create == "y":
            os.makedirs(save_path)
        else:
            print("The figure has not been saved.")
            return False
    return True

# ---------------------------------------------------------------- #
def get_plot_name(plot_save_path, name=""):
    if not plot_save_path[len(plot_save_path)-4:len(plot_save_path)] == ".png":
        if not plot_save_path[len(plot_save_path)-1] == "/":
            plot_save_path = plot_save_path + "/"
        return plot_save_path + name
    return plot_save_path
