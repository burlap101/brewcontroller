#!/usr/bin/python

import matplotlib as mpl
mpl.use('TKAgg')
import matplotlib.pyplot as plt
plt.style.use('ggplot')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib import animation
from matplotlib.figure import Figure
from matplotlib import dates

from tkinter import *
import tkinter.ttk
import tkinter.messagebox
import tkinter.filedialog
import time
from datetime import datetime
import pickle
import brewbrains as bb
import pandas as pd


class GUI(object):
    """
    GUI class for the brew app
    """

    refresh_time = 500  #GUI refreshes after so many ms 
    samples = 0
    logfile = ''

    def __init__(self, root, brain = None):
        self.root = root
        self.root.protocol('WM_DELETE_WINDOW', self.exit_app)
        self.gpo_count = 2      #How many gpo you want to control
        if not brain:
            self.bb = bb.BrewBrains(self.gpo_count)
        else:
            self.bb = brain

        
    def draw_iostatus_display(self):
        bg = 'antique white'
        defaultpadx = 2
        defaultpady = 2
        self.templabel = {}
        
        iostatusframe = Frame(self.root, bg = bg)
        iostatusframe.pack(side = LEFT, anchor = 'nw', padx = defaultpadx, pady = defaultpady, fill = 'both')

        Label(iostatusframe, text = "TEMPS", font = 'Helvetica 14 bold', bg = bg).grid(row = 0, column = 1, columnspan = 2, padx = defaultpadx, pady = 5, sticky = W)
        
        for sensor, i in zip(self.bb.get_sensors(), list(range(len(self.bb.get_sensors())))):
            Label(iostatusframe, text = "#%d:" %(i+1), bg=bg).grid(row = i+1, column = 1, padx = 2, pady = 2)   
            self.templabel[sensor] = Label(iostatusframe, text = "#### degC", bg = "dark grey", fg = "dark green", width = 11, font = "Courier 13 bold",
                                    relief = "sunken")
            self.templabel[sensor].grid(row = i+1, column = 2, padx = defaultpadx, pady = defaultpady)
            
        

    def draw_setpoint_display(self, bg = 'PaleGreen2', packside = 'left'):
        setpointbg = bg
        self.gpo_widgets = []

        for gpo in range(self.gpo_count):
            temp_off, temp_on = self.bb.get_setpoints(gpo)
            self.gpo_widgets.append({})
            self.gpo_widgets[gpo]['sensorselect'] = []
            self.gpo_widgets[gpo]['selected_sensor'] = StringVar()
            
            self.gpo_widgets[gpo]['setpointframe'] = Frame(self.root, bg = setpointbg)

            self.gpo_widgets[gpo]['setpointtitle'] = Label(self.gpo_widgets[gpo]['setpointframe'], text = "GPO #%d CONTROL" %(gpo+1),
                                                           font = 'Helvetica 14 bold', bg = setpointbg)
            self.gpo_widgets[gpo]['control_mode'] = Label(self.gpo_widgets[gpo]['setpointframe'], text = "HEAT",
                                                                font = 'Helvetica 14 bold', bg = setpointbg, fg = "IndianRed2")
            self.gpo_widgets[gpo]['on_entry'] = Entry(self.gpo_widgets[gpo]['setpointframe'], width = 5)
            self.gpo_widgets[gpo]['on_label'] = Label(self.gpo_widgets[gpo]['setpointframe'], text = "ON  (degC):", bg = setpointbg)
            self.gpo_widgets[gpo]['off_entry'] = Entry(self.gpo_widgets[gpo]['setpointframe'], width = 5)
            self.gpo_widgets[gpo]['off_label'] = Label(self.gpo_widgets[gpo]['setpointframe'], text = "OFF (degC):", bg = setpointbg)
            self.gpo_widgets[gpo]['setpointbutton'] = Button(self.gpo_widgets[gpo]['setpointframe'], text = "Change setpoints",
                                                             command = lambda gpo=gpo: self.change_setpoints(gpo))
            self.gpo_widgets[gpo]['gpotogglebutton'] = Button(self.gpo_widgets[gpo]['setpointframe'], text = "GPO On/Off",
                                                              command = lambda gpo=gpo: self.on_off_command(gpo))
            self.gpo_widgets[gpo]['gpostatelabel'] = Label(self.gpo_widgets[gpo]['setpointframe'], text = "OFF",
                                        font = "Helvetica 20 bold", fg = 'red', bg = 'gold', width = 4)

            i=0
            for sensor in self.bb.get_sensors():
                self.gpo_widgets[gpo]['sensorselect'].append(Radiobutton(self.gpo_widgets[gpo]['setpointframe'], text = 'Sensor #%d' %(i+1),
                                                                         variable = self.gpo_widgets[gpo]['selected_sensor'], value = sensor, bg = setpointbg,
                                                                         command = lambda gpo=gpo: self.change_sensor(gpo)))
                self.gpo_widgets[gpo]['sensorselect'][i].grid(column = 3, row = i+2,padx = 2, pady = 2)
                i+=1
            self.gpo_widgets[gpo]['sensorselect'].append(Radiobutton(self.gpo_widgets[gpo]['setpointframe'], text = 'None',
                                                                     variable = self.gpo_widgets[gpo]['selected_sensor'], value = 0, bg = setpointbg,
                                                                     command = lambda gpo=gpo: self.change_sensor(gpo)))
            self.gpo_widgets[gpo]['sensorselect'][i].grid(column = 4, row = 2, padx = 2, pady = 2)
            self.gpo_widgets[gpo]['sensorselect'][i].select()
            
            self.gpo_widgets[gpo]['setpointframe'].pack(side = packside, anchor = 'w', padx = 2, pady = 2, fill = 'both')
            self.gpo_widgets[gpo]['setpointtitle'].grid(row = 1, column = 0, columnspan = 2, padx = 2, pady = 5, sticky = 'w')
            self.gpo_widgets[gpo]['control_mode'].grid(row = 1, column = 2, columnspan = 2, padx = 2, pady = 5, sticky = 'e')
            self.gpo_widgets[gpo]['gpostatelabel'].grid(row = 2, column = 0, rowspan = 2, sticky = W+N+S, padx = 2, pady = 2)
            self.gpo_widgets[gpo]['on_label'].grid(row = 2, column = 1, padx = 2, pady = 2, sticky = 'e')
            self.gpo_widgets[gpo]['on_entry'].grid(row = 2, column = 2, padx = 2, pady = 2)
            self.gpo_widgets[gpo]['on_entry'].insert(0, temp_on)
            self.gpo_widgets[gpo]['off_label'].grid(row = 3, column = 1, padx = 2, pady = 2, sticky = 'e')
            self.gpo_widgets[gpo]['off_entry'].grid(row = 3, column = 2, padx = 2, pady = 2)
            self.gpo_widgets[gpo]['off_entry'].insert(0, temp_off)
            self.gpo_widgets[gpo]['setpointbutton'].grid(row = 4, column = 2, padx = 2, pady = 2, columnspan = 2, sticky = 'w')
            self.gpo_widgets[gpo]['gpotogglebutton'].grid(row = 4, column = 0, columnspan = 2, padx = 2, pady = 2, sticky = 'w')

    def draw_logging_display(self):
        loggingbg = 'bisque'
        self.loggingframe = Frame(self.root, bg = loggingbg)

        self.loggingtitle = Label(self.loggingframe, text = "LOGGING", font = "Helvetica 14 bold", bg = loggingbg)
        self.loggingbutton = Button(self.loggingframe, text = "Start Logging", command = self.toggle_logging)
        self.logfilelabel = Label(self.loggingframe, text = "Logfile: NONE", bg = loggingbg)

        self.loggingframe.pack(side = LEFT, anchor = 'nw', padx = 2, pady = 2, fill = 'both')
        self.loggingtitle.grid(row = 1, column = 1, padx = 2, pady = 5, sticky = 'w')
        self.logfilelabel.grid(row = 2, column = 1, padx = 2, pady = 5, sticky = 'w')
        self.loggingbutton.grid(row = 3, column = 1, padx = 2, pady = 2, sticky = 'w')

    def draw_infobar(self):
        self.infobar = Frame(self.root)

        self.logstatuslabel = Label(self.infobar, text = "Logging: DISABLED",
                                    relief = 'sunken')
        self.timelabel = Label(self.infobar, text = "Time: %s" %(time.asctime().split()[3])[:5], relief = 'sunken')

        self.infobar.pack(anchor = 'nw', side = LEFT)
        self.timelabel.pack(side = TOP, anchor = 'w', padx = 2, pady = 2)
        self.logstatuslabel.pack(side = TOP, anchor = 'w', padx = 2, pady = 2)
        for sensor, i in zip(self.bb.sensors.get_ids(), list(range(len(self.bb.sensors.get_ids())))):
            Label(self.infobar,
                  text = "Sensor #%d ID:\n%s" %((i+1), sensor.upper()),
                  relief = 'sunken').pack(side = TOP, anchor = 'w', padx = 2, pady = 2)

    def toggle_logging(self):
        if self.bb.get_logfile():
            self.bb.toggle_logging()
            self.logstatuslabel.configure(text = "Logging: ENABLED")
            self.loggingbutton.configure(text = "Stop Logging", state = DISABLED)
        else:
            tkinter.messagebox.showerror(title = "Invalid Logfile", message = "Open or create a valid logfile")
        

    def change_sensor(self, gpo):
        #This will change the controlling sensor for a GPO triggered by radio button
        self.bb.set_sensor(gpo=gpo, sensor=self.gpo_widgets[gpo]['selected_sensor'].get())
        
    def change_setpoints(self, gpo):
        temp_off, temp_on = self.bb.get_setpoints(gpo)
        try:
            if tkinter.messagebox.askyesno(title = "Change Setpoints",
                                     message = "Are you certain you want to change the setpoints?"):
                if float(self.gpo_widgets[gpo]['on_entry'].get()) == float(self.gpo_widgets[gpo]['off_entry'].get()):
                    tkinter.messagebox.showerror(title = "Level Mismatch",
                                           message = "Temperatures can't be equal")
                    self.gpo_widgets[gpo]['on_entry'].delete(0, END)
                    self.gpo_widgets[gpo]['off_entry'].delete(0, END)
                    self.gpo_widgets[gpo]['on_entry'].insert(0, temp_on)
                    self.gpo_widgets[gpo]['off_entry'].insert(0, temp_off)
                    
                else:
                    temp_on = float(self.gpo_widgets[gpo]['on_entry'].get())
                    temp_off = float(self.gpo_widgets[gpo]['off_entry'].get())
                    self.bb.change_setpoints(gpo, temp_off, temp_on)
                    if temp_on > temp_off:
                        self.gpo_widgets[gpo]['control_mode'].configure(text = "COOL", fg = 'SteelBlue1')
                    else:
                        self.gpo_widgets[gpo]['control_mode'].configure(text = "HEAT", fg = 'IndianRed2')
                
            else:
                self.gpo_widgets[gpo]['on_entry'].delete(0, END)
                self.gpo_widgets[gpo]['off_entry'].delete(0, END)
                self.gpo_widgets[gpo]['on_entry'].insert(0, temp_on)
                self.gpo_widgets[gpo]['off_entry'].insert(0, temp_off)
        
        except ValueError:
            tkinter.messagebox.showerror(title = "Invalid Temperature(s)",
                                   message = "Invalid temperature values entered")
            self.gpo_widgets[gpo]['on_entry'].delete(0, END)
            self.gpo_widgets[gpo]['off_entry'].delete(0, END)
            self.gpo_widgets[gpo]['on_entry'].insert(0, temp_on)
            self.gpo_widgets[gpo]['off_entry'].insert(0, temp_off)
    
    def create_menu(self):
        menubar = Menu(self.root)
        filemenu = Menu(menubar, tearoff = 0)
        filemenu.add_command(label="Load Brew", command= self.load_brew)
        filemenu.add_command(label="Save Brew", command = self.save_brew)
        filemenu.add_separator()
        filemenu.add_command(label = "Open Log File", command = self.open_log_file)
        filemenu.add_command(label = "Create Log File", command = self.create_log_file)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command = self.exit_app)
        menubar.add_cascade(label="File", menu=filemenu)
        viewmenu = Menu(menubar, tearoff = 0)
        viewmenu.add_command(label="Plot", command = self.view_plot)
        menubar.add_cascade(label="View", menu=viewmenu)
        optionsmenu = Menu(menubar, tearoff = 0)
        optionsmenu.add_command(label = "Configure Email Reports", command = self.email_report)
        menubar.add_cascade(label = "Options", menu = optionsmenu)
        aboutmenu = Menu(menubar, tearoff=0)
        aboutmenu.add_command(label="About", command=self.about)
        menubar.add_cascade(label="About", menu=aboutmenu)
        self.root.config(menu = menubar)

    def email_report(self):
        max_recipients = 2
        self.toaddr = []
        current_config = self.bb.email_reports_config()
        self.erwin = Toplevel(self.root)
        self.erwin.title("Email Reports Configuration")

        toaddr_frame = Frame(self.erwin)
        toaddr_frame.pack(side = TOP, anchor = 'nw')

        for i in range(max_recipients):
            self.toaddr.append(StringVar())
            Label(toaddr_frame, text = "Email %d:" %(i+1)).grid(row = i, column = 0, sticky = 'w', padx = 2, pady = 2)
            Entry(toaddr_frame, width = 30, textvariable = self.toaddr[i]).grid(row = i, column = 1, sticky = 'w', padx = 2, pady = 2)
            if len(current_config) >= (i+1):
                self.toaddr[i].set(current_config[i])
            
        button_panel = Frame(self.erwin)
        button_panel.pack(side = TOP, anchor = 'nw')

        Button(button_panel, text = 'OK', command = self.change_email_reporting).pack(side = LEFT, padx = 2, pady = 2)
        Button(button_panel, text = 'Cancel', command = self.erwin.destroy).pack(side = LEFT, padx = 2, pady = 2)

    def change_email_reporting(self):
        addrs = []
        for i in self.toaddr:
            addrs.append(i.get())
        self.bb.config_email_reports(*addrs)
        self.erwin.destroy()
        

    def view_plot(self):
        df = pd.read_csv(self.bb.get_logfile())
        df['DateTime'] = pd.to_datetime(df['DateTime'], dayfirst = True)

        df = df.set_index('DateTime')
        gb = df.groupby('Sensor ID')
        dfs = [gb.get_group(x) for x in gb.groups]

        pltwin = Toplevel(self.root)
        pltwin.title("Plot of Logfile {}".format(self.bb.get_logfile()))

        f = Figure(figsize=(5,4), dpi=100)
        ax = f.add_subplot(1, 1, 1)

        for x in dfs:
            ax.plot(x.index, x['Avg'].values, label=x['Sensor ID'].iloc[0])
        ax.set_xlabel('Date Time')
        ax.set_ylabel('\N{DEGREE SIGN}C')
        ax.legend()
        
        canvas = FigureCanvasTkAgg(f, master=pltwin)
        canvas.show()
        canvas.get_tk_widget().pack(side = TOP, fill = BOTH, expand = 1)

        toolbar = NavigationToolbar2TkAgg(canvas, pltwin)
        toolbar.update()
        canvas._tkcanvas.pack(side = TOP, fill = BOTH, expand = 1)
        

    def load_brew(self):
        brewfile = tkinter.filedialog.askopenfilename(filetypes=[("Brew config file", "*.pkl")],
                                                title = "Save Brew Config File As...", initialdir = "Saves")
        if brewfile:
            f = open(brewfile, 'rb')
            settings = pickle.load(brewfile)
            for gpo, setting in zip(list(range(self.gpo_count)), settings):
                self.gpo_widgets[gpo]['selected_sensor'].set(setting)
            f.close()

    def save_brew(self):
        brewfile = tkinter.filedialog.asksaveasfilename(filetypes=[("Brew config file", "*.pkl")],
                                                title = "Save Brew Config File As...", initialdir = "Saves")
        if brewfile:
            f = open(brewfile, 'wb')
            settings = {}
            for gpo in range(self.gpo_count):
                settings["GPO"+str(gpo)] = self.gpo_widgets[gpo]['selected_sensor'].get()

            pickle.dump(settings, brewfile)
            f.close()
            

    def open_log_file(self):
        logfile = tkinter.filedialog.askopenfilename(filetypes=[('Brewlog Mk2 file', '*.blgx')],
                                               title = "Open Brewlog...", initialdir = "Brewlogs")
        if logfile:
            self.logfilelabel.configure(text = "Logfile: %s" %logfile.split('/')[-1])
            self.bb.set_logfile(logfile, newlog=False)

    def create_log_file(self):
        logfile = tkinter.filedialog.asksaveasfilename(filetypes=[('Brewlog Mk2 file', '*.blgx')],
                                                 title = "Create Brewlog...", initialdir = "Brewlogs")

        if logfile:
            self.logfilelabel.configure(text = "Logfile: %s" %logfile.split('/')[-1])
            self.bb.set_logfile(logfile)
    
    def update(self):
        for sensor in self.bb.get_sensors():
            try:
                temp_c = self.bb.get_temp(sensor) 
                self.templabel[sensor].config(text="%.2f degC" %temp_c)
            except:
                self.templabel[sensor].config(text="#### degC")
        for gpo in range(self.gpo_count):
            self.change_gpo_status_label(gpo)
       
        self.timelabel.config(text = "Time: %s" %(time.asctime().split()[3])[:5])
        self.root.after(self.refresh_time, self.update)

    def change_gpo_status_label(self, gpo):
        if self.bb.get_gpo_state(gpo):
            self.gpo_widgets[gpo]['gpostatelabel'].configure(text = "ON", font = "Helvetica 20 bold", fg = 'dark green')
        else:
            self.gpo_widgets[gpo]['gpostatelabel'].configure(text = "OFF", font = "Helvetica 20 bold", fg = 'red')

    def on_off_command(self, gpo):
        self.bb.toggle_gpo(gpo)
        self.change_gpo_status_label(gpo)

    def exit_app(self):
        if tkinter.messagebox.askyesno(title='Quit', message='Do you really want to quit?'):
            self.bb.cleanup()
            self.root.destroy()
            
    def about(self):
        message = ("This application is good for use in both fermentation and possibly a keezer "
                   "where maintaining a close temperature range is important.")
        
        tkinter.messagebox.showinfo(title = "Temperature Control App", message = message)

    
    
def main():
    root = Tk()
    root.title("Temperature Control App")
    #root.geometry("350x150")
    img = PhotoImage(file = "Images/Logo1.gif")
    root.tk.call('wm', 'iconphoto', root._w, img)
    gui = GUI(root)
    gui.create_menu()
    gui.draw_iostatus_display()
    gui.draw_setpoint_display()
    gui.draw_logging_display()
    gui.draw_infobar()
    root.after(500, gui.update)
    root.mainloop()

if __name__ == '__main__':
    main()
