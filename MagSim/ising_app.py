import tkinter as tk
from tkinter import ttk

# The numpy random generator is preferrable,
# although I don't want to import the rest
# of numpy functionality. This can also be
# removed later not to introduce unnecesary
# dependencies.

from numpy import random as rnd
from math import exp

# Plotting libraries and settings
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from matplotlib import style, tight_layout

#from matplotlib.backend_tools import ToolBase
#from matplotlib.backend_managers import ToolManager

style.use("seaborn")


class Ising:
    
    def __init__(self, root, N):
        
        self.size = N
        self.paused = False	

	# Temperature belongs to the whole app
	# and it should exist independent of
	# which simulation is used
        root.temperature = tk.DoubleVar()
        root.magnetization = 0.0

	# I should implement at least few system sizes
	# but I need to figure out how to keep buttons
	# as squares and not rectangles
        mainframe = ttk.Frame(root, padding="5 5 5 5")
        mainframe.pack()
       
        simfrm = ttk.Frame(mainframe, padding="2 2 2 2")
        simfrm.grid(column=0, row=0)
      
        # Build the simulation structure
        self.buttons = [[Cell(simfrm, (i, j), N) for j in range(N)] for i in range(N)]
        self.build_pointers()

        # The frame for the simulation control
        controlfrm = ttk.Frame(mainframe, padding="2 2 2 2")
        controlfrm.grid(column=0, row=1)        

        # Temperature controller  
        self.temp_lbl = ttk.Label(controlfrm, text=f"T={root.temperature.get()}",
                                  style=root.style_names[3])
        self.temp_lbl.grid(row=0, column=0, padx=10, pady=3)
        self.temp = ttk.Scale(controlfrm, from_=0.0001, to=5.0, length=300,
                              style=root.style_names[2], variable=root.temperature,
                              command=self.set_temperature)
        self.temp.grid(row=0, column=1, padx=10)
        
        # Pause button
        pausepath = "images/pause32.png"
        self.pauseimg = tk.PhotoImage(file=pausepath)
        self.pausebtn = ttk.Button(controlfrm, command=self.pausesim)
        self.pausebtn['image'] = self.pauseimg
        self.pausebtn.grid(row=0, column=2, padx=30, pady=3)        
       
        # Play button
        playpath = "images/play32.png"
        self.playimg = tk.PhotoImage(file=playpath)
        self.playbtn = ttk.Button(controlfrm, command=self.playsim)
        self.playbtn['image'] = self.playimg
        self.playbtn.grid(row=0, column=3, padx=10, pady=3)      
 
        # Initialize and draw the plot
        self.plt = Plot(root, mainframe)

        # Initialize the simulation
        self.simulate()

       
    def build_pointers(self):
        for button_row in self.buttons:
            for button in button_row:
                
                btn_row, btn_col = button.position
                
                button.left = self.buttons[btn_row][(btn_col-1)%self.size]
                button.right = self.buttons[btn_row][(btn_col+1)%self.size]
                button.up = self.buttons[(btn_row-1)%self.size][btn_col]
                button.down = self.buttons[(btn_row+1)%self.size][btn_col]

         
    def simulate(self):
        if not self.paused:
            self.step()
            root.after(3, self.simulate)
   
    def step(self):
        # Perform one step of the simulation after which single spin
        # is either flipped or stays the same
        rx, ry = rnd.randint(0, self.size), rnd.randint(0, self.size)
        self.buttons[rx][ry].change_color(root.temperature.get())

        # Update the plot
        next(self.plt.iterator)
        self.plt.update()

    def set_temperature(self, event):
        self.temp_lbl.configure(text="T={:.2f}".format(root.temperature.get()))
        
    def get_temperature(self):
        return root.temperature.get()

    def dump(self):
        # The function that dumps the contents of the grid
        # It should be tidied up at certain point
        for button_row in self.buttons:
            for button in button_row:
                 
                print("POSITION: ", button.position)               
                print(" ", button.up.value ," ")
                print(button.left.value, button.value, button.right.value)
                print(" ", button.down.value, " ")
                print("\n")         
    
    def pausesim(self):
        self.paused=True

    def playsim(self):
        if self.paused:
            self.paused=False
            self.simulate()
                
class Cell:
            
    def __init__(self, frame, position, N):
        
        self.position=position
        self.value=rnd.randint(0, 2) # This is one way to initialize
        self.spin=-1+2*self.value
        self.text=f"{position}"
        self.N = N

        root.magnetization+=self.spin/N**2 # Append the spin value to calculate the initial
                                           # magnetization

        self.cell=ttk.Button(frame, width=0.5, style=root.style_names[self.value], command=self.change_color_click)
        self.cell.grid(column=position[1],
                        row=position[0],
                        padx=0.05,
                        pady=0.05,
                        ipadx=7.5,
                        ipady=1.0,
                        sticky="nesw")
            
        self.left = None
        self.right = None
        self.up = None
        self.down = None


    def change_color(self, temperature):
	# Generate a random number, depending on the temperature and 
        # and calculate the flip energy change and call bit_flip method 

        r = rnd.random()
        
        deltaE = 4*self.spin*(self.neighbour_sum()-2)
        gibbs=1.0
 
        if deltaE>=0:
            try:
                gibbs=exp(-deltaE/temperature)
            except ZeroDivisionError:
                gibbs=0.0
            except OverflowError:
                gibbs=0.0
            except:
                raise("Error: Not sure what happened!")        
         
        if r<gibbs:
            self.value = self.bit_flip(self.value)
            self.spin = -1+2*self.value
            root.magnetization+=2*self.spin/self.N**2
           
        
        self.cell.configure(style=root.style_names[self.value])

    def change_color_click(self):

        self.value = self.bit_flip(self.value)
        self.spin = -1+2*self.value
        root.magnetization+=2*self.spin/self.N**2
        self.cell.configure(style=root.style_names[self.value])        

    def bit_flip(self, x):        
        if x!=0 and x!=1:
            raise ValueError("Not a bit!")      
        return (1+x)%2

    
    def neighbour_sum(self):
        return self.left.value+self.right.value+self.up.value+self.down.value

    def set_temperature(self, temperature):
        return root.temperature.set(temperature)

class Menu:

    def __init__(self, root):
        
        menubar = tk.Menu(root)
        root['menu'] = menubar
        
        menu_sim = tk.Menu(menubar)
        menu_help = tk.Menu(menubar)
        menu_sim.add_separator()        
 
        menubar.add_cascade(menu=menu_sim, label="Simulation")
        menubar.add_cascade(menu=menu_help, label="Help")

        menu_sim_list = tk.Menu(menu_sim)
        menu_sim.add_cascade(menu=menu_sim_list, label="Choose")
        menu_sim.add_command(command=self.exit_program, label="Exit Program")

    def exit_program(self):
        # The exit window is opened 
        # which asks for the confirmation
        # that user wants to close the program
        ExitWindow(root)        
        

class ExitWindow:

    def __init__(self, root):
        
        self.win_exit = tk.Toplevel(root)
        self.win_exit.geometry("260x75")
        self.win_exit.title("Exit Window")
        
        win_mainframe = ttk.Frame(self.win_exit)
        win_mainframe.grid(column=0, row=0)
        win_mainframe.grid_columnconfigure(0, weight=1)
        win_mainframe.grid_rowconfigure(0, weight=1)
 
        win_lbl = ttk.Label(win_mainframe, text="Are you sure you want to quit?")
        win_lbl.grid(column=0, row=0, ipadx=20, ipady=5, columnspan=2, sticky="nesw")

        win_yes_btn = ttk.Button(win_mainframe, text="Yes", command=self.exit_yes)
        win_yes_btn.grid(column=0, row=1)

        win_no_btn = ttk.Button(win_mainframe, text="No", command=self.exit_no)
        win_no_btn.grid(column=1, row=1)

    def exit_yes(self):
        self.win_exit.destroy()
        root.destroy()

    def exit_no(self):
        self.win_exit.destroy()

class Plot:

    def __init__(self, root, mainframe):
        
        fig = Figure(figsize=(4, 3), dpi=100)
        self.ax = fig.add_subplot()
        fig.tight_layout()        

        # Creates a frame on the right hand side that contains the plot
        self.pltfrm = ttk.Frame(mainframe, padding="50 20 10 20")
        self.pltfrm.grid(row=0, column=1, ipadx=80, ipady=45, sticky="n")
       
        # Initialize the lists to be plotted
        self.steps = []
        self.magnetization_plot = []

        # The limit values of magnetization will be used to
        # draw the ylimits of the plot 
        # TO BE IMPLEMENTED!!!
        self.max = 0.0
        self.min = 0.0
     
        # Initialize the plot axis
        self.line, = self.ax.plot(self.steps, self.magnetization_plot, linewidth=2)
        self.line.set_label("Magnetization")
        self.ax.tick_params(axis="both", which="major", labelsize=14)
        self.ax.legend(fontsize=14)

        # Connect the figure to the tk interface
        self.canvas = FigureCanvasTkAgg(fig, master=self.pltfrm)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.canvas.mpl_connect("key_press_event", key_press_handler)          

        # Creates the toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.pltfrm, pack_toolbar=False)
        
        #toolmgr = ToolManager(figure=fig)
        #ToolBase(toolmgr, "ZoomPanBase").destroy()
        #toolmgr.remove_tool("Zoom")
        self.toolbar.update()
        self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Build an iterator
        self.iterator = iter(self)

    def update(self):
        # This function adds a point on the graph
        # and redraws the plot
         
        self.steps.append(self.step)
        self.magnetization_plot.append(root.magnetization)
        # self.ax.set_xlim(-0.1, self.step)
        self.ax.relim()
        self.ax.autoscale_view()

        self.line.set_data(self.steps, self.magnetization_plot)
        self.canvas.draw()

    # Building an iterator that adds steps to the simulation
    def __next__(self):
        self.step+=1
        return self.step

    def __iter__(self):
        self.step = 0
        return self

# All styling is implemented on the level of root        
class AppStyle:

    def __init__(self, root): 
        
        root.style = ttk.Style()
        root.style.theme_use("alt")

        root.style_names={0:"blue_cell.TButton", 1:"green_cell.TButton",
                          2:"bluish.Horizontal.TScale", 3:"templbl.TLabel"}
        
        root.style.configure(root.style_names[0],
                             font=("calibri", 8, "bold"),
                             foreground="white",
                                 #85151b 
                             background="#365577",
                             relief="sunken")
 
        root.style.configure(root.style_names[1],
                             font=("calibri", 8, "bold"),
                             foreground="white",
                                  #211cb0
                             background="#6d9a7d",
                             relief="raised")
            
        root.style.configure(root.style_names[2],
                             relief="raised")
        
        root.style.configure(root.style_names[3],
                             font="Arial 15",
                             padding = "3",
                             foreground = "#0c0c0d",
                             relief="raised")

    def __repr__(self):
        return str(root.style) 

            
if __name__=="__main__":
    
    root = tk.Tk()
    
    # This option removes the unwanted behavior
    # that is default for backward compatibility reasons
    root.option_add("*TearOff", False)
    root.title("Ising Simulation")
    
    Menu(root)
    AppStyle(root)
    
    ising_app = Ising(root, 30)
    root.mainloop()
