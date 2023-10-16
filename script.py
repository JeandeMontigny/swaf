import swaf.traces as sw
import swaf.utils as su

# ---------------------------------------------------------------- #
file_path = "C:/Users/T3-JeanM/Documents/postdoc/ephy/recordings/290923/Data3.smr"
Recording = sw.read_file(file_path, t_start=300, t_stop=3400)

Recording.plot_analogsig(300, 510, show_plot=True)

ave_waveform = Recording.get_ave_waveform(307, 506, anotate=True)

# ave_waveform = Recording.get_ave_waveform(307, 506, plot_save_path="results/290923")
# ave_waveform = Recording.get_ave_waveform(536, 734, plot_save_path="results/290923")
# ave_waveform = Recording.get_ave_waveform(763, 962, plot_save_path="results/290923")
# ave_waveform = Recording.get_ave_waveform(994, 1193, plot_save_path="results/290923")
# ave_waveform = Recording.get_ave_waveform(1220, 1419, plot_save_path="results/290923")
# ave_waveform = Recording.get_ave_waveform(1493, 1692, plot_save_path="results/290923")
# ave_waveform = Recording.get_ave_waveform(1761, 1960, plot_save_path="results/290923")
# ave_waveform = Recording.get_ave_waveform(2016, 2215, plot_save_path="results/290923")
# ave_waveform = Recording.get_ave_waveform(2244, 2443, plot_save_path="results/290923")
# ave_waveform = Recording.get_ave_waveform(2505, 2704, plot_save_path="results/290923")
# ave_waveform = Recording.get_ave_waveform(2723, 2922, plot_save_path="results/290923")
# ave_waveform = Recording.get_ave_waveform(2933, 3131, plot_save_path="results/290923")
# ave_waveform = Recording.get_ave_waveform(3197, 3396, plot_save_path="results/290923")


# point_list: list of frame (time) points [ (t1, t2), (t3, t4), (t5, t6), ...]
slope_list=[(570, 586), (615, 645), (675, 690), (740, 785)]

file_path = "C:/Users/T3-JeanM/Documents/postdoc/ephy/recordings/290923/Data3.smr"
Recording = sw.read_file(file_path, t_start=2723, t_stop=2922)
ave_waveform = Recording.get_ave_waveform(2723, 2922,  anotate=False)
su.plot_dg_slope(ave_waveform, Recording, point_list=slope_list, show_plot=True)

# file_path = "C:/Users/T3-JeanM/Documents/postdoc/ephy/recordings/290923/Data3.smr"
# Recording = sw.read_file(file_path, t_start=2723, t_stop=2922)
# ave_waveform = Recording.get_ave_waveform(2723, 2922)
# su.plot_dg_slope(ave_waveform, Recording, point_list=slope_list, show_plot=False, plot_save_path="results/dg_slopes/290923_2723-2922")
#
# file_path = "C:/Users/T3-JeanM/Documents/postdoc/ephy/recordings/111023/Data1.smr"
# Recording = sw.read_file(file_path, t_start=4206, t_stop=4404)
# ave_waveform = Recording.get_ave_waveform(4206, 4404)
# su.plot_dg_slope(ave_waveform, Recording, point_list=[(562, 580), (615, 645), (665, 680), (740, 785)], show_plot=False, plot_save_path="results/dg_slopes/111023_4206-4404")
#
# file_path = "C:/Users/T3-JeanM/Documents/postdoc/ephy/recordings/111023/Data1.smr"
# Recording = sw.read_file(file_path, t_start=3575, t_stop=3773)
# ave_waveform = Recording.get_ave_waveform(3575, 3773)
# su.plot_dg_slope(ave_waveform, Recording, point_list=slope_list, show_plot=False, plot_save_path="results/dg_slopes/111023_3575-3773")
#
# file_path = "C:/Users/T3-JeanM/Documents/postdoc/ephy/recordings/111023/Data1.smr"
# Recording = sw.read_file(file_path, t_start=3783, t_stop=3981)
# ave_waveform = Recording.get_ave_waveform(3783, 3981)
# su.plot_dg_slope(ave_waveform, Recording, point_list=slope_list, show_plot=False, plot_save_path="results/dg_slopes/111023_3783-3981")
