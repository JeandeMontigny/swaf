import swaf.traces as sw

# ---------------------------------------------------------------- #
file_path = "./recordings/290923/Data3.smr"
Recording = sw.read_file(file_path, t_start=300, t_stop=3400)

Recording.plot_analogsig(300, 510, show_plot=True)

# Recording.get_ave_waveform(2723, 2922, plot_save_path="results/290923", create_path="y")
Ave_Waveform = Recording.get_ave_waveform(307, 506, anotate=True)

# ---------------- #
file_path = "./recordings/290923/Data3.smr"
Ave_Waveform = sw.get_ave_waveform_from_rec(file_path, 2723, 2922)
# Ave_Waveform.plot_waveform()
# sw.get_ave_waveform_from_rec("./recordings/290923/Data3.smr", 1220, 1419, anotate=True)
# point_list: list of frame (time) points [ (t1, t2), (t3, t4), (t5, t6), ...]
# 615 = 0.009024s post stim ; 645 = 0.011904s post stim
slope_list=[(570, 586), (615, 645), (675, 690), (740, 785)]
Ave_Waveform.get_waveform_slope(point_list=slope_list, show_plot=True)

file_path = "./recordings/111023/Data1.smr"
Ave_Waveform = sw.get_ave_waveform_from_rec(file_path, 3575, 3773)
peaks = Ave_Waveform.get_waveform_peaks(show_plot=True)
sw.get_ave_waveform_from_rec("./recordings/290923/Data3.smr", 1220, 1419).get_waveform_peaks(exclusion_dist=10, lag=1, show_plot=True)
slope_list = Ave_Waveform.get_waveform_slope_list()
Ave_Waveform.get_waveform_slope(point_list=slope_list, show_plot=True)

file_path = "./recordings/290923/Data3.smr"
Ave_Waveform = sw.get_ave_waveform_from_rec(file_path, 2723, 2922)
Ave_Waveform.get_waveform_slope(print_val=True, show_plot=False)
print("peaks times:", Ave_Waveform.peaks)
print("peaks values:", Ave_Waveform.waveform[Ave_Waveform.peaks])
print("slopes values:", Ave_Waveform.slope_val_list)
