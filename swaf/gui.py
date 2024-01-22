import pyperclip
import numpy as np
import PySimpleGUI as sg

from .traces import *

# ---------------- #
def create_gui():
    file_selection_gui()

# ---------------- #
def file_selection_gui():
    layout = [[
        sg.Text("Please, select your recording file (.smr):"),
        sg.In(size=(25, 1), enable_events=True, key="-file-"),
        sg.FileBrowse()
        ]]
    file_selection_window = sg.Window("Swaf - File selection", layout)
    event, values = file_selection_window.read()

    if event == "-file-":
        file_path = values["-file-"]

        if not file_path[len(file_path)-4:len(file_path)] == ".smr":
            file_selection_window.close()
            display_message_gui("Please, enter a valid recording file (.smr)")
            file_selection_gui()
            return

        print("file", file_path, "selected")
        file_selection_window.close()
        file_processing_gui(file_path)

# ---------------- #
def file_processing_gui(file_path):
    print("Reading file", file_path)
    Recording = read_file(file_path)

    rb = []
    rb.append(sg.Radio("Plot raw signal", "operation", key="-plot_raw-", enable_events=True, default=True))
    rb.append(sg.Radio("Get average waveform", "operation", key="-get_ave_waveform-", enable_events=True))

    layout_raw = [
        [sg.Text("Plot raw signal")],
        [sg.Checkbox("show plot", key="-show plot raw-"), sg.Checkbox("hide stimulation events", key="-plot stim-")]
    ]

    layout_ave = [
        [sg.Text("Get average waveform")],
        [sg.Checkbox("show plot", key="-show plot ave-"), sg.Checkbox("anotate plot", key="-anotate-")]
    ]

    # general layout
    layout = [
        [sg.Text("New recording file (.smr):"), sg.In(size=(25, 1), enable_events=True, key="-new file-"), sg.FileBrowse()],
        [sg.HSeparator()],
        [sg.Text("Recording " + file_path)],
        [sg.Text("  Recording length: " + str(Recording.t_stop) + " (at " + str(Recording.sampling_rate) + ")")],
        [sg.Button("Average waveform analysis")],
        [rb],
        [sg.Text("time window (s):"), sg.Input(np.ceil(float(Recording.t_start)), key="-t_start-", size=(16,1)), sg.Input(np.floor(float(Recording.t_stop)), key="-t_stop-", size=(16,1))],
        [sg.Column(layout_raw, key="-layout raw-"), sg.Column(layout_ave, visible=False, key="-layout ave-")],
        [sg.Checkbox("save plot", enable_events=True, key="-save plot-"), sg.Input("plot saving path", visible=False, key="-plot save path input-"), sg.FolderBrowse("save path", visible=False, key="-plot save path-")],
        [sg.Checkbox("show data", key="-show data-"), sg.Checkbox("Save data (.csv)", key="-save data-")],
        [sg.Button("Go"), sg.Button("Exit")],
    ]

    processing_window = sg.Window("Swaf - File processing", layout)

    # ---- #
    while True:
        event, values = processing_window.read()

        if event in (sg.WIN_CLOSED, "Exit"):
            break

        if event == "-new file-":
            file_path = values["-new file-"]
            print("file", file_path, "selected")
            processing_window.close()
            file_processing_gui(file_path)
            return

        if event =="-plot_raw-":
            processing_window["-layout ave-"].update(visible=False)
            processing_window["-layout raw-"].update(visible=True)

        if event == "-get_ave_waveform-":
            processing_window["-layout raw-"].update(visible=False)
            processing_window["-layout ave-"].update(visible=True)

        if event == "Average waveform analysis":
            waveform_processing_gui(Recording)

        if event == "-save plot-":
            processing_window["-plot save path input-"].update(visible=True)
            processing_window["-plot save path-"].update(visible=True)

        if event == "Go":
            # check t_start t_stop
            if not gui_check_t(float(Recording.t_stop), values["-t_start-"], values["-t_stop-"]):
                continue

            if values["-show data-"] or values["-save data-"]:
                display_data_gui(Recording, float(values["-t_start-"]), float(values["-t_stop-"]),  values["-show data-"], values["-save data-"], values["-plot_raw-"])

            if values["-plot_raw-"]:
                # if neither show/save plot or show/save data is ticked
                if not values["-save plot-"] and not values["-show plot raw-"] and not values["-show data-"] and not values["-save data-"]:
                    display_message_gui("tick at least one action to perform")
                    continue
                if values["-save plot-"]:
                    Recording.plot_analogsig(float(values["-t_start-"]), float(values["-t_stop-"]), plot_stim=not(values["-plot stim-"]), show_plot=values["-show plot raw-"], plot_save_path=values["-plot save path-"])
                else:
                    if float(values["-t_stop-"]) - float(values["-t_start-"]) > 3600:
                        display_message_gui("Aborting: you are trying to plot the raw data over a long time window (from \'show plot\' checkbox). This might cause some issues.\nPlease, define a smaller time window (< 3600s (1h))")
                        continue
                    Recording.plot_analogsig(float(values["-t_start-"]), float(values["-t_stop-"]), plot_stim=not(values["-plot stim-"]), show_plot=values["-show plot raw-"])

            # if -get_ave_waveform- key
            else:
                # if neither show or save is ticked
                if not values["-save plot-"] and not values["-show plot ave-"] and not values["-show data-"] and not values["-save data-"]:
                    display_message_gui("tick at least one action to perform")
                    continue
                if values["-save plot-"]:
                    Recording.get_ave_waveform(float(values["-t_start-"]), float(values["-t_stop-"]), show_plot=values["-show plot ave-"], anotate=values["-anotate-"], plot_save_path=values["-plot save path-"])
                else:
                    Recording.get_ave_waveform(float(values["-t_start-"]), float(values["-t_stop-"]), show_plot=values["-show plot ave-"], anotate=values["-anotate-"])

# ---------------- #
def waveform_processing_gui(Recording):

    def add_line(i):
        return [[sg.T("waveform "+str(i+1)+" ->  t start: "), sg.InputText(key=("-t_start-", i), size=(10,1)), sg.T("t stop:"), sg.InputText(key=("-t_stop-", i), size=(10,1)), sg.Button("show plot", enable_events=True, key=("show_plot", i))]]

    column_layout = [[sg.T("waveform "+str(1)+" ->  t start: "), sg.InputText(key=("-t_start-", 0), size=(10,1)), sg.T("t stop:"), sg.InputText(key=("-t_stop-", 0), size=(10,1)), sg.Button("show plot", enable_events=True, key=("show_plot", 0)), sg.Button("+", enable_events=True, key="-add-")]]

    layout_display = [
        [sg.Text("You can select multiple rows (using shit+click or ctrl+click) and copy them to clip board using Ctrl+c.\nSave button saves all the talbe.")],
        [sg.Table([], headings=["peak time (s)", "peak value (V)"], enable_events=True, key="-results peaks-"), sg.Table([], headings=["window (frame)", "slope value (V)"], enable_events=True, key="-results slopes-")],
        [sg.HSeparator()],
        [sg.Input("output folder path", size=(20,1)), sg.FolderBrowse("save path"), sg.InputText("file name", key="-file name-", size=(10,1))],
        [sg.Button("Save as .csv")]
    ]

    layout = [
        [sg.Text("Waveform features extraction:")],
        [sg.Checkbox("Peaks", key="-peaks-"), sg.Checkbox("Slopes", key="-slopes-")],
        [sg.Column(column_layout, key='-Column-'), sg.VSeparator(), sg.Column(layout_display, visible=False, key="-display results-")],
        [sg.Button("Go"), sg.Button("Reset"), sg.Button("Exit")]
    ]
    waveform_processing_window = sg.Window("Swaf - Average waveform processing", layout, finalize=True)
    waveform_processing_window.bind("<Control-c>", "-control c-")

    # ---- #
    i = 1
    while True:
        event, values = waveform_processing_window.read()
        if event == "Exit":
            waveform_processing_window.close()
            return

        if event == "Reset":
            waveform_processing_window.close()
            waveform_processing_gui(Recording)
            return

        if event == "-add-":
            waveform_processing_window.extend_layout(waveform_processing_window['-Column-'], add_line(i))
            i += 1

        for try_i in range(i):
            if event == ("show_plot", try_i):
                if gui_check_t(float(Recording.t_stop), values[("-t_start-", try_i)], values[("-t_stop-", try_i)]):
                    Recording.get_ave_waveform(float(values[("-t_start-", try_i)]), float(values[("-t_stop-", try_i)]), show_plot=True, anotate=True)
                continue

        if event == "Go":
            peaks_list_list = []
            slope_list_list = []
            for waveform_i in range(i):
                if not gui_check_t(float(Recording.t_stop), values[("-t_start-", waveform_i)], values[("-t_stop-", waveform_i)]):
                    continue
                else:
                    Waveform = Recording.get_ave_waveform(float(values[("-t_start-", waveform_i)]), float(values[("-t_stop-", waveform_i)]))
                    if values[("-peaks-")]:
                        peaks_list = []
                        # TODO: parameters exclusion_dist, half_width, overlap
                        for peak_t in Waveform.get_waveform_peaks():
                            peaks_list.append([round((peak_t-(0.05*float(Waveform.sampling_rate)))/float(Waveform.sampling_rate), 5), round(Waveform.waveform[peak_t], 3)])
                        peaks_list_list.append(peaks_list)

                    if values[("-slopes-")]:
                        # TODO: point_list option and other parameters
                        # if not values["-slope time list"]:
                        slope_time_list = Waveform.get_waveform_slope_list()
                        slope_list_list.append(Waveform.get_waveform_slope(slope_time_list))

                    tab_peaks = []
                    for peak_list in peaks_list_list:
                        for tuple in peak_list:
                            tab_peaks.append(tuple)
                        tab_peaks.append([[], []])
                    waveform_processing_window["-results peaks-"].update(tab_peaks)

                    tab_slopes = []
                    for slope_list in slope_list_list:
                        for tuple in slope_list:
                            tab_slopes.append([str(tuple[0]), tuple[1]])
                        tab_slopes.append([[], []])
                    waveform_processing_window["-results slopes-"].update(tab_slopes)

                    waveform_processing_window["-display results-"].update(visible=True)

            if values[("-peaks-")]:
                print(peaks_list_list)
            if values[("-slopes-")]:
                print(slope_list_list)

        if event == "-control c-":
            items_peaks = values["-results peaks-"]
            items_slopes = values["-results slopes-"]
            lst = list(map(lambda x:' '.join(str(tab_peaks[x]).replace('[','').replace(']','')), items_peaks)) + list(map(lambda y:' '.join(str(tab_slopes[y]).replace('[','').replace(']','').replace('\'','')), items_slopes))
            text = "\n".join(lst)
            pyperclip.copy(text)

        if event == "Save as .csv":
            if values[("-peaks-")]:
                if not save_csv([str(tuple).replace('[','').replace(']','') for tuple in tab_peaks], values["save path"], values["-file name-"]+"_peaks"):
                    continue
            if values[("-slopes-")]:
                # TODO: improve output. change time from frames to seconds
                if not save_csv([str(tuple).replace('[','').replace(']','').replace('(','').replace(')','') for tuple in slope_list_list], values["save path"], values["-file name-"]+"_slopes"):
                    continue

# ---------------- #
def display_data_gui(Recording, t_start, t_stop, show, save, raw):
    if (raw and show) or (raw and save):
        if (raw and show) and t_stop - t_start > 2:
            display_message_gui("Aborting: too many data elements to display (from \'show data\' checkbox).\nPlease, define a smaller time window (< 2s for raw data)")
            return

        id_start = int((t_start-float(Recording.segment.t_start)) * float(Recording.sampling_rate))
        id_stop = int((t_stop-float(Recording.segment.t_start)) * float(Recording.sampling_rate))
        x = [[str(float(t))] for t in Recording.segment.analogsignals[2].times[id_start:id_stop]]
        y = [[str(float(v))] for v in Recording.signal[id_start:id_stop]]

    if not raw:
        Ave_Waveform = Recording.get_ave_waveform(t_start, t_stop)
        x = [[str(t)] for t in Ave_Waveform.time]
        y = [[str(v)] for v in Ave_Waveform.waveform]

    if x and y:
        data = np.concatenate((x, y), axis=1)

    if save:
        layout = [
            [sg.Input("output folder path"), sg.FolderBrowse("save path"), sg.InputText("file name", key="-file name-", size=(10,1))],
            [sg.Button("Go"), sg.Button("Exit")]
        ]
        save_data_window = sg.Window("Swaf - Data", layout)

        # ---- #
        while True:
            event, values = save_data_window.read()

            if event == "Exit":
                save_data_window.close()
                return
            if event == "Go":
                if not save_csv(data, values["save path"], values[("-file name-")]):
                    continue

    if show:
        layout = [
            [sg.Text("You can select multiple rows (using shit+click or ctrl+click) and copy them to clip board using Ctrl+c.\nSave button saves all the talbe.")],
            [sg.Table(data, headings=["time (s)", "V"], enable_events=True, key="-table-")],
            [sg.Input("output folder path"), sg.FolderBrowse("save path"), sg.InputText("file name", key="-file name-", size=(10,1))],
            [sg.Button("Save as .csv"), sg.Button("Exit")]
        ]

        display_data_window = sg.Window("Swaf - Data", layout, finalize=True)
        display_data_window.bind("<Control-c>", "-control c-")

        # ---- #
        while True:
            event, values = display_data_window.read()

            if event == "-control c-":
                items = values['-table-']
                lst = list(map(lambda x:' '.join(data[x]), items))
                text = "\n".join(lst)
                pyperclip.copy(text)

            if event == "Exit":
                display_data_window.close()
                return
            if event == "Save as .csv":
                if not save_csv(data, values["save path"], values[("-file name-")]):
                    continue

# ---------------- #
def display_message_gui(message):
    layout = [
        [sg.Text(message)],
        [sg.Button("Ok")]
    ]
    display_message_window = sg.Window("Swaf - Message", layout)

    # ---- #
    while True:
        event, values = display_message_window.read()
        if event == "Ok":
            display_message_window.close()
            return

# ---------------- #
def save_csv(data, path, name):
    if path == "" or name == "file name":
        display_message_gui("Please, enter a saving path and file name")
        return False
    save_path = ""
    if name[len(name)-4:] == ".csv":
        save_path = path+"/"+name
    else:
        save_path = path+"/"+name+".csv"

    np.savetxt(save_path, data, delimiter=',', fmt='%s')
    print("data saved as", save_path)
    return True

# ---------------- #
def gui_check_t(rec_t_stop, t_start, t_stop):
    if t_start == '' or t_stop == '' or (not t_start.replace(".", "", 1).isdigit()) or (not t_stop.replace(".", "", 1).isdigit()) or float(t_start) < 0 or float(t_stop) > rec_t_stop:
        display_message_gui("start and stop times need to be within the recording length")
        return False
    return True
