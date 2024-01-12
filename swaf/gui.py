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
        [sg.Checkbox("save plot", key="-save plot-"), sg.Input(), sg.FolderBrowse("save path")],
        [sg.Checkbox("show data", key="-show data-"), sg.Checkbox("Save data (.csv)", key="-save data-")],
        [sg.Button("Go"), sg.Button("Exit")],
    ]

    processing_window = sg.Window("Swaf - File processing", layout)
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

        # ---- #
        if event == "Go":
            # check t_start t_stop
            if gui_check_t(float(Recording.t_stop), values):
                continue

            if values["-show data-"] or values["-save data-"]:
                display_data_gui(Recording, float(values["-t_start-"]), float(values["-t_stop-"]),  values["-show data-"], values["-save data-"],values["-plot_raw-"])

            if values["-plot_raw-"]:
                # if neither show/save plot or show/save data is ticked
                if not values["-save plot-"] and not values["-show plot raw-"] and not values["-show data-"] and not values["-save data-"]:
                    display_message_gui("tick at least one action to perform")
                    continue
                if values["-save plot-"]:
                    Recording.plot_analogsig(float(values["-t_start-"]), float(values["-t_stop-"]), plot_stim=not(values["-plot stim-"]) ,show_plot=values["-show plot raw-"], plot_save_path=values["save path"])
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
                    Recording.get_ave_waveform(float(values["-t_start-"]), float(values["-t_stop-"]), show_plot=values["-show plot ave-"], anotate=values["-anotate-"], plot_save_path=values["save path"])
                else:
                    Recording.get_ave_waveform(float(values["-t_start-"]), float(values["-t_stop-"]), show_plot=values["-show plot ave-"], anotate=values["-anotate-"])

# ---------------- #
def waveform_processing_gui(Recording):
    # TODO: export waveform measures to right part of gui, and save as .csv file?
    # TODO: add checkbox for what to extract: peaks, slope, point_list for slopes

    def add_line(i):
        return [[sg.T("waveform "+str(i+1)+" ->  t start: "), sg.InputText(key=("-t_start-", i), size=(10,1)), sg.T("t stop:"), sg.InputText(key=("-t_stop-", i), size=(10,1)), sg.Button("show plot", enable_events=True, key=("show_plot", i))]]

    column_layout = [[sg.T("waveform "+str(1)+" ->  t start: "), sg.InputText(key=("-t_start-", 0), size=(10,1)), sg.T("t stop:"), sg.InputText(key=("-t_stop-", 0), size=(10,1)), sg.Button("show plot", enable_events=True, key=("show_plot", 0)), sg.Button("+", enable_events=True, key="-add-")]]

    layout = [
        [sg.Text("Waveform features extraction:")],
        [sg.Checkbox("Peaks", key="-peaks-"), sg.Checkbox("Slopes", key="-slopes-")],
        [sg.Column(column_layout, key='-Column-')],
        [sg.Button("Go"), sg.Button("Reset"), sg.Button("Exit")]
    ]
    waveform_processing_window = sg.Window("Swaf - Average waveform processing", layout)
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
                Recording.get_ave_waveform(float(values[("-t_start-", try_i)]), float(values[("-t_stop-", try_i)]), show_plot=True, anotate=True)
                continue

        if event == "Go":
            peaks_list = []
            slope_list_list = []
            for waveform_i in range(i):
                Waveform = Recording.get_ave_waveform(float(values[("-t_start-", try_i)]), float(values[("-t_stop-", try_i)]))
                if values[("-peaks-")]:
                    peaks_list.append(Waveform.get_waveform_peaks())
                if values[("-slopes-")]:
                    slope_list_list.append(Waveform.get_waveform_slope_list())

            print(peaks_list)
            print(slope_list_list)

# ---------------- #
def display_data_gui(Recording, t_start, t_stop, show, save, raw):
    if show and raw:
        if t_stop - t_start > 2:
            display_message_gui("Aborting: too many data elements to display (from \'show data\' checkbox).\nPlease, define a smaller time window (< 2s for raw data)")
            return

        id_start = int((t_start-float(Recording.segment.t_start)) * float(Recording.sampling_rate))
        id_stop = int((t_stop-float(Recording.segment.t_start)) * float(Recording.sampling_rate))
        x = [[str(float(t))] for t in Recording.segment.analogsignals[2].times[id_start:id_stop]]
        y = [[str(float(v))] for v in Recording.signal[id_start:id_stop]]

    elif not raw:
        Ave_Waveform = Recording.get_ave_waveform(t_start, t_stop)
        x = [[str(t)] for t in Ave_Waveform.time]
        y = [[str(v)] for v in Ave_Waveform.waveform]

    data = np.concatenate((x, y), axis=1)
    if save:
        layout = [
            [sg.Input("output folder path"), sg.FolderBrowse("save path"), sg.InputText("file name", key="-file name-", size=(10,1))],
            [sg.Button("Go"), sg.Button("Exit")]
        ]
        save_data_window = sg.Window("Swaf - Data", layout)
        while True:
            event, values = save_data_window.read()

            if event == "Exit":
                save_data_window.close()
                return
            if event == "Go":
                if not save_csv(data, values):
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
                if not save_csv(data, values):
                    continue

# ---------------- #
def display_message_gui(message):
    layout = [
        [sg.Text(message)],
        [sg.Button("Ok")]
    ]
    display_message_window = sg.Window("Swaf - Message", layout)
    while True:
        event, values = display_message_window.read()
        if event == "Ok":
            display_message_window.close()
            return

# ---------------- #
def save_csv(data, values):
    if values["save path"] == "" or values["-file name-"] == "file name":
        display_message_gui("Please, enter a saving path and file name")
        return False
    path = ""
    if values["-file name-"][len(values["-file name-"])-4:] == ".csv":
        path = values["save path"]+"/"+values["-file name-"]
    else:
        path = values["save path"]+"/"+values["-file name-"]+".csv"

    np.savetxt(path, data, delimiter=',', fmt='%s')
    print("data saved as", values["save path"]+"/"+values["-file name-"])
    return True

# ---------------- #
def gui_check_t(rec_t_stop, values):
    if values["-t_start-"] == '' or values["-t_stop-"] == '' or (not values["-t_start-"].replace(".", "", 1).isdigit()) or (not values["-t_stop-"].replace(".", "", 1).isdigit()) or float(values["-t_start-"]) < 0 or float(values["-t_stop-"]) > rec_t_stop:
        display_message_gui("start and stop times need to be within the recording length")
        return True
    return False
