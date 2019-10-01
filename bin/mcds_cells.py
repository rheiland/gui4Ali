# "Out: Cells" tab
import os
from ipywidgets import Layout, Label, Text, Checkbox, Button, HBox, VBox, Box, \
    FloatText, BoundedIntText, BoundedFloatText, HTMLMath, Dropdown, interactive, Output
from collections import deque
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
#from matplotlib.patches import Circle, Ellipse, Rectangle
from matplotlib.patches import Circle
from matplotlib.collections import PatchCollection
import matplotlib.colors as mplc
import numpy as np
import zipfile
import glob
import platform

from pyMCDS import pyMCDS
# from debug import debug_view

hublib_flag = True
if platform.system() != 'Windows':
    try:
#        print("Trying to import hublib.ui")
        from hublib.ui import Download
    except:
        hublib_flag = False
else:
    hublib_flag = False


class CellsTab(object):

    def __init__(self):
        # tab_height = '520px'
        # tab_layout = Layout(width='900px',   # border='2px solid black',
        #                     height=tab_height, overflow_y='scroll')

        self.output_dir = '.'

        constWidth = '180px'

#        self.fig = plt.figure(figsize=(6, 6))
        # self.fig = plt.figure(figsize=(7, 7))

        max_frames = 1
        self.cells_plot = interactive(self.plot_cells, frame=(0, max_frames), continuous_update=False)

# https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20List.html#Play-(Animation)-widget
        # play = widgets.Play(
        # #     interval=10,
        #     value=50,
        #     min=0,
        #     max=100,
        #     step=1,
        #     description="Press play",
        #     disabled=False
        # )
        # slider = widgets.IntSlider()
        # widgets.jslink((play, 'value'), (slider, 'value'))
        # widgets.HBox([play, slider])

        # "plot_size" controls the size of the tab height, not the plot (rf. figsize for that)
        plot_size = '500px'  # small: 
        plot_size = '750px'  # medium
        plot_size = '700px'  # medium
        plot_size = '600px'  # medium
        self.cells_plot.layout.width = plot_size
        self.cells_plot.layout.height = plot_size
        self.use_defaults = True
        self.show_nucleus = 1  # 0->False, 1->True in Checkbox!
        self.show_edge = 1  # 0->False, 1->True in Checkbox!
        self.show_tracks = 0  # 0->False, 1->True in Checkbox!
        self.trackd = {}  # dictionary to hold cell IDs and their tracks: (x,y) pairs
        # self.scale_radius = 1.0
        # self.axes_min = 0
        # self.axes_max = 2000
        self.axes_min = -1000.0
        self.axes_max = 1000.   # TODO: get from input file
        self.axes_min = -500.0
        self.axes_max = 500.   # TODO: get from input file

        self.max_frames = BoundedIntText(
            min=0, max=99999, value=max_frames,
            description='Max',
            layout=Layout(width='160px'),
#            layout=Layout(flex='1 1 auto', width='auto'),  #Layout(width='160px'),
        )
        self.max_frames.observe(self.update_max_frames)

        self.show_nucleus_checkbox= Checkbox(
            description='nucleus', value=True, disabled=False,
            layout=Layout(width=constWidth),
#            layout=Layout(flex='1 1 auto', width='auto'),  #Layout(width='160px'),
        )
        self.show_nucleus_checkbox.observe(self.show_nucleus_cb)

        self.show_edge_checkbox= Checkbox(
            description='edge', value=True, disabled=False,
            layout=Layout(width=constWidth),
#            layout=Layout(flex='1 1 auto', width='auto'),  #Layout(width='160px'),
        )
        self.show_edge_checkbox.observe(self.show_edge_cb)

        self.show_tracks_checkbox= Checkbox(
            description='tracks', value=True, disabled=False,
            layout=Layout(width=constWidth),
#            layout=Layout(flex='1 1 auto', width='auto'),  #Layout(width='160px'),
        )
        # self.show_tracks_checkbox.observe(self.show_tracks_cb)

#        row1 = HBox([Label('(select slider: drag or left/right arrows)'), 
#            self.max_frames, VBox([self.show_nucleus_checkbox, self.show_edge_checkbox])])
#            self.max_frames, self.show_nucleus_checkbox], layout=Layout(width='500px'))

#        self.tab = VBox([row1,self.cells_plot], layout=tab_layout)

        items_auto = [Label('select slider: drag or left/right arrows'), 
            self.max_frames, 
            # self.show_nucleus_checkbox,  
            # self.show_edge_checkbox, 
            # self.show_tracks_checkbox, 
         ]
#row1 = HBox([Label('(select slider: drag or left/right arrows)'), 
#            max_frames, show_nucleus_checkbox, show_edge_checkbox], 
#            layout=Layout(width='800px'))
        box_layout = Layout(display='flex',
                    flex_flow='row',
                    align_items='stretch',
                    width='70%')
        row1 = Box(children=items_auto, layout=box_layout)

    #     if (hublib_flag):
    #         self.download_button = Download('svg.zip', style='warning', icon='cloud-download', 
    #                                         tooltip='You need to allow pop-ups in your browser', cb=self.download_cb)
    #         download_row = HBox([self.download_button.w, Label("Download all cell plots (browser must allow pop-ups).")])
    # #        self.tab = VBox([row1, self.cells_plot, self.download_button.w], layout=tab_layout)
    # #        self.tab = VBox([row1, self.cells_plot, self.download_button.w])
    #         self.tab = VBox([row1, self.cells_plot, download_row])
    #     else:
    #         self.tab = VBox([row1, self.cells_plot])

        self.tab = VBox([row1, self.cells_plot])


    # def update(self, rdir=''):
    def update(self, rdir=''):
        # with debug_view:
        #     print("mcds_cells:update(): rdir=", rdir)        

        if rdir:
            self.output_dir = rdir

        all_files = sorted(glob.glob(os.path.join(self.output_dir, 'output*.xml')))
        if len(all_files) > 0:
            last_file = all_files[-1]
            # Note! the following will trigger: self.max_frames.observe(self.update_max_frames)
            self.max_frames.value = int(last_file[-12:-4])  # assumes naming scheme: "snapshot%08d.svg"

        # with debug_view:
        #     print("mcds_cells": added %s files" % len(all_files))


    # def download_cb(self):
    #     file_str = os.path.join(self.output_dir, '*.svg')
    #     # print('zip up all ',file_str)
    #     with zipfile.ZipFile('svg.zip', 'w') as myzip:
    #         for f in glob.glob(file_str):
    #             myzip.write(f, os.path.basename(f))   # 2nd arg avoids full filename path in the archive

    def show_nucleus_cb(self, b):
        global current_frame
        if (self.show_nucleus_checkbox.value):
            self.show_nucleus = 1
        else:
            self.show_nucleus = 0
#        self.plot_cells(self,current_frame)
        self.cells_plot.update()

    def show_edge_cb(self, b):
        if (self.show_edge_checkbox.value):
            self.show_edge = 1
        else:
            self.show_edge = 0
        self.cells_plot.update()

    # def show_tracks_cb(self, b):
    #     if (self.show_tracks_checkbox.value):
    #         self.show_tracks = 1
    #     else:
    #         self.show_tracks = 0
    #     # print('--- show_tracks_cb: calling cells_plot.update()')
    #     # if (not self.show_tracks):
    #     #     self.cells_plot.update()
    #     # else:
    #     if (self.show_tracks):
    #         self.create_all_tracks()
    #     self.cells_plot.update()


    # Note! this is called for EACH change to "Max" frames, which is with every new .svg file created!
    def update_max_frames(self,_b): 
        self.cells_plot.children[0].max = self.max_frames.value
        # if (self.show_tracks):
        #     print('--- update_max_frames: calling create_all_tracks')
        #     self.create_all_tracks()

    #-----------------------------------------------------
    def circles(self, x, y, s, c='b', vmin=None, vmax=None, **kwargs):
        """
        See https://gist.github.com/syrte/592a062c562cd2a98a83 

        Make a scatter plot of circles. 
        Similar to plt.scatter, but the size of circles are in data scale.
        Parameters
        ----------
        x, y : scalar or array_like, shape (n, )
            Input data
        s : scalar or array_like, shape (n, ) 
            Radius of circles.
        c : color or sequence of color, optional, default : 'b'
            `c` can be a single color format string, or a sequence of color
            specifications of length `N`, or a sequence of `N` numbers to be
            mapped to colors using the `cmap` and `norm` specified via kwargs.
            Note that `c` should not be a single numeric RGB or RGBA sequence 
            because that is indistinguishable from an array of values
            to be colormapped. (If you insist, use `color` instead.)  
            `c` can be a 2-D array in which the rows are RGB or RGBA, however. 
        vmin, vmax : scalar, optional, default: None
            `vmin` and `vmax` are used in conjunction with `norm` to normalize
            luminance data.  If either are `None`, the min and max of the
            color array is used.
        kwargs : `~matplotlib.collections.Collection` properties
            Eg. alpha, edgecolor(ec), facecolor(fc), linewidth(lw), linestyle(ls), 
            norm, cmap, transform, etc.
        Returns
        -------
        paths : `~matplotlib.collections.PathCollection`
        Examples
        --------
        a = np.arange(11)
        circles(a, a, s=a*0.2, c=a, alpha=0.5, ec='none')
        plt.colorbar()
        License
        --------
        This code is under [The BSD 3-Clause License]
        (http://opensource.org/licenses/BSD-3-Clause)
        """

        if np.isscalar(c):
            kwargs.setdefault('color', c)
            c = None

        if 'fc' in kwargs:
            kwargs.setdefault('facecolor', kwargs.pop('fc'))
        if 'ec' in kwargs:
            kwargs.setdefault('edgecolor', kwargs.pop('ec'))
        if 'ls' in kwargs:
            kwargs.setdefault('linestyle', kwargs.pop('ls'))
        if 'lw' in kwargs:
            kwargs.setdefault('linewidth', kwargs.pop('lw'))
        # You can set `facecolor` with an array for each patch,
        # while you can only set `facecolors` with a value for all.

        zipped = np.broadcast(x, y, s)
        patches = [Circle((x_, y_), s_)
                for x_, y_, s_ in zipped]
        collection = PatchCollection(patches, **kwargs)
        if c is not None:
            c = np.broadcast_to(c, zipped.shape).ravel()
            collection.set_array(c)
            collection.set_clim(vmin, vmax)

        ax = plt.gca()
        ax.add_collection(collection)
        ax.autoscale_view()
        # plt.draw_if_interactive()
        if c is not None:
            plt.sci(collection)
        # return collection

    #-------------------------
    # def plot_cells(self, frame, rdel=''):
    def plot_cells(self, frame):
        # global current_idx, axes_max
        global current_frame
        current_frame = frame
        fname = "output%08d.xml" % frame
        full_fname = os.path.join(self.output_dir, fname)
        # with debug_view:
            # print("plot_cells:", full_fname) 
        # print("-- plot_cells:", full_fname) 
        if not os.path.isfile(full_fname):
            print("Once output files are generated, click the slider.")   
            return
        
        mcds = pyMCDS(fname, self.output_dir)
        # print(mcds.get_time())

        cell_ids = mcds.data['discrete_cells']['ID']
#        print(cell_ids.shape)
#        print(cell_ids[:4])

        #cell_vec = np.zeros((cell_ids.shape, 3))
        num_cells = cell_ids.shape[0]
        cell_vec = np.zeros((cell_ids.shape[0], 3))
        vec_list = ['position_x', 'position_y', 'position_z']
        for i, lab in enumerate(vec_list):
            cell_vec[:, i] = mcds.data['discrete_cells'][lab]
        xvals = cell_vec[:, 0]
        yvals = cell_vec[:, 1]
        # print('x range: ',xvals.min(), xvals.max())
        # print('y range: ',yvals.min(), yvals.max())


        # xvals = np.array(xlist)
        # yvals = np.array(ylist)
        # rvals = np.array(rlist)
        # rgbs = np.array(rgb_list)

        # print("xvals[0:5]=",xvals[0:5])
        # print("rvals[0:5]=",rvals[0:5])
        # print("rvals.min, max=",rvals.min(),rvals.max())

        # rwh - is this where I change size of render window?? (YES - yipeee!)
        #   plt.figure(figsize=(6, 6))
        #   plt.cla()
        # title_str = svals[2] + "d, " + svals[4] + "h, " + svals[7] + "m"
        title_str = str(mcds.get_time()) + " min (" + str(num_cells) + " agents)"
        #   plt.title(title_str)
        #   plt.xlim(axes_min,axes_max)
        #   plt.ylim(axes_min,axes_max)
        #   plt.scatter(xvals,yvals, s=rvals*scale_radius, c=rgbs)

        # TODO: make figsize a function of plot_size? What about non-square plots?
        # self.fig = plt.figure(figsize=(9, 9))
        # self.fig = plt.figure(figsize=(18, 18))
        # self.fig = plt.figure(figsize=(15, 15))  # 
        self.fig = plt.figure(figsize=(9, 9))  # 


        #rwh - temp fix - Ah, error only occurs when "edges" is toggled on
        # cell_size = 5
        cell_vols = mcds.data['discrete_cells']['total_volume']
        cell_radii = (cell_vols* 0.75 / 3.14159)**0.3333
        # if (self.show_edge):
        #     try:
        #         # self.circles(xvals,yvals, s=rvals, color=rgbs, edgecolor='black', linewidth=0.5)
        #         # self.circles(xvals,yvals, s=cell_radii, edgecolor='black', linewidth=0.1)
        #         # self.circles(xvals,yvals, s=cell_radii, c='red', edgecolor='black', linewidth=0.5, fc='none')
        #         self.circles(xvals,yvals, s=cell_radii, c='red', fc='none')
        #         # cell_circles = self.circles(xvals,yvals, s=rvals, color=rgbs, edgecolor='black', linewidth=0.5)
        #         # plt.sci(cell_circles)
        #     except (ValueError):
        #         pass
        # else:
        #     # self.circles(xvals,yvals, s=rvals, color=rgbs)
        #     self.circles(xvals,yvals, s=cell_radii, fc='none')
        self.circles(xvals,yvals, s=cell_radii, fc='none')

        plt.xlim(self.axes_min, self.axes_max)
        plt.ylim(self.axes_min, self.axes_max)
        #   ax.grid(False)
#        axx.set_title(title_str)
        plt.title(title_str)

# video-style widget - perhaps for future use
# cells_play = widgets.Play(
#     interval=1,
#     value=50,
#     min=0,
#     max=100,
#     step=1,
#     description="Press play",
#     disabled=False,
# )
# def cells_slider_change(change):
#     print('cells_slider_change: type(change)=',type(change),change.new)
#     plot_cells(change.new)
    
#cells_play
# cells_slider = widgets.IntSlider()
# cells_slider.observe(cells_slider_change, names='value')

# widgets.jslink((cells_play, 'value'), (cells_slider,'value')) #  (cells_slider, 'value'), (plot_cells, 'value'))

# cells_slider = widgets.IntSlider()
# widgets.jslink((play, 'value'), (slider, 'value'))
# widgets.HBox([cells_play, cells_slider])

# Using the following generates a new mpl plot; it doesn't use the existing plot!
#cells_anim = widgets.HBox([cells_play, cells_slider])

#cells_tab = widgets.VBox([cells_dir, cells_plot, cells_anim], layout=tab_layout)

#cells_tab = widgets.VBox([cells_dir, cells_anim], layout=tab_layout)
#---------------------
