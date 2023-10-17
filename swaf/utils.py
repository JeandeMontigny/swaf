import neo

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
