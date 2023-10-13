import swaf.traces as sw

# ---------------------------------------------------------------- #
file_path = "C:/Users/T3-JeanM/Documents/postdoc/ephy/290923/Data3.smr"
Recording = sw.read_file(file_path, t_start=1490, t_stop=3400)
Recording.plot_analogsig()
ave_waveform = Recording.get_ave_waveform(1761, 1959, plot=True)
