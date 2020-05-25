import tkinter
from tkinter.colorchooser import askcolor
import cv2
import PIL.Image, PIL.ImageTk
import time
from Vision2 import VisionHandler
import numpy as np
import colorsys
import datetime
import os
from ws4py.client.threadedclient import WebSocketClient
from threading import *


def rgbtohsv(rgb):
    hsv = colorsys.rgb_to_hsv(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)
    hsvColor = np.array([int(hsv[0] * 179), int(hsv[1] * 255), int(hsv[2] * 255)])
    return hsvColor


def hsvtorgb(hsv):
    rgb = colorsys.hsv_to_rgb(hsv[0] / 179, hsv[1] / 255, hsv[2] / 255)
    rgbColor = [int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)]
    return rgbColor


class App:
    settingsOpen = False
    wait_on_command = False
    end_reached_count = 0
    tree_detected_count = 0

    def __init__(self, window, window_title, capture, video_source=0):
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source

        # open video source (by default this will try to open the computer webcam)
        self.cap = capture
        self.current_output = 0  # show regular RGB image

        # create menu bar
        self.menubar = tkinter.Menu(self.window)
        view_menu = tkinter.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="view rgb", command=lambda *args: self.select_output(0))
        view_menu.add_command(label="view mask", command=lambda *args: self.select_output(1))
        view_menu.add_command(label="view contour", command=lambda *args: self.select_output(2))
        view_menu.add_command(label="view vision", command=lambda *args: self.select_output(3))
        view_menu.add_separator()
        view_menu.add_command(label="view all", command=lambda *args: self.select_output(4))
        view_menu.add_separator()
        view_menu.add_command(label="view data", command=self.open_variables)

        edit_menu = tkinter.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Settings", command=self.open_settings)
        edit_menu.add_separator()
        edit_menu.add_command(label="Exit", command=self.quit)
        self.window.config(menu=self.menubar)

        # Create a canvas that can fit the above video source size
        self.canvas = tkinter.Canvas(window, width=self.cap.width * 2, height=self.cap.height * 2)
        self.canvas.pack()

        # Button that lets the user take a snapshot
        self.btn_snapshot = tkinter.Button(window, text="Snapshot", width=50, command=self.snapshot)
        self.btn_snapshot.pack(anchor=tkinter.CENTER, expand=True)

        # define the color variables for Vision
        self.lower_range_guide = np.array([85, 100, 50])
        self.upper_range_guide = np.array([150, 255, 255])
        self.lower_range_tree = np.array([85, 100, 50])
        self.upper_range_tree = np.array([150, 255, 255])
        self.lower_range_hand = np.array([85, 100, 50])
        self.upper_range_hand = np.array([150, 255, 255])
        self.distance = 50
        self.read_defaults()

        self.frames = []

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15
        self.update()

        self.window.mainloop()

    def select_output(self, screen):
        self.current_output = screen

    def quit(self):
        self.window.destroy()

    def open_variables(self):
        self.variables = tkinter.Toplevel()
        self.variables.wm_title("Values")
        self.variables.minsize(width=400, height=400)
        self.variables.lift()

    def color_picker_min(self, frame):
        if frame == 0:
            color = askcolor(initialcolor=tuple(hsvtorgb(self.lower_range_guide)))[0]
            self.lower_range_guide = rgbtohsv(color)
        elif frame == 1:
            color = askcolor(initialcolor=tuple(hsvtorgb(self.lower_range_tree)))[0]
            print(color)
            self.lower_range_tree = rgbtohsv(color)
        else:
            color = askcolor(initialcolor=tuple(hsvtorgb(self.lower_range_hand)))[0]
            self.lower_range_hand = rgbtohsv(color)
        self.settings.lift()

    def color_picker_max(self, frame):
        if frame == 0:
            color = askcolor(initialcolor=tuple(hsvtorgb(self.upper_range_guide)))[0]
            self.upper_range_guide = rgbtohsv(color)
        elif frame == 1:
            color = askcolor(initialcolor=tuple(hsvtorgb(self.upper_range_tree)))[0]
            self.upper_range_tree = rgbtohsv(color)
        else:
            color = askcolor(initialcolor=tuple(hsvtorgb(self.upper_range_hand)))[0]
            self.upper_range_hand = rgbtohsv(color)
        self.settings.lift()

    def close_settings(self, save):
        if save:
            print("Saving settings...")
            self.update_defaults()
        else:
            self.read_defaults()
        self.settingsOpen = False
        self.settings.destroy()

    def reset_defaults(self):
        self.lower_range_tree = np.array([85, 100, 50])
        self.upper_range_tree = np.array([150, 255, 255])
        self.lower_range_guide = self.lower_range_tree
        self.upper_range_guide = self.upper_range_tree
        self.update_defaults()

    def update_slider(self, event):
        self.distance = self.distance_slider.get()

    def open_settings(self):
        if self.settingsOpen:
            return
        else:
            self.settingsOpen = True
            self.settings = tkinter.Toplevel()
            self.settings.wm_title("Settings")
            min_range_color = tkinter.Button(self.settings, text="min range",
                                             command=lambda *args: self.color_picker_min(0))
            max_range_color = tkinter.Button(self.settings, text="max range",
                                             command=lambda *args: self.color_picker_max(0))
            min_range_color.grid(column=0, row=0)
            max_range_color.grid(column=1, row=0)

            min_range_color_tree = tkinter.Button(self.settings, text="min range tree",
                                                  command=lambda *args: self.color_picker_min(1))
            max_range_color_tree = tkinter.Button(self.settings, text="max range tree",
                                                  command=lambda *args: self.color_picker_max(1))
            min_range_color_tree.grid(column=0, row=1)
            max_range_color_tree.grid(column=1, row=1)

            min_range_color_hand = tkinter.Button(self.settings, text="min range hand",
                                                  command=lambda *args: self.color_picker_min(2))
            max_range_color_hand = tkinter.Button(self.settings, text="max range hand",
                                                  command=lambda *args: self.color_picker_max(2))
            min_range_color_hand.grid(column=0, row=2)
            max_range_color_hand.grid(column=1, row=2)

            reset_button = tkinter.Button(self.settings, text="Reset defaults", command=self.reset_defaults)
            reset_button.grid(column=0, row=3)
            self.distance_slider = tkinter.Scale(self.settings, from_=0, to=200, orient=tkinter.HORIZONTAL,
                                                 command=self.update_slider)
            self.distance_slider.set(self.distance)
            self.distance_slider.grid(column=0, row=4)

            ok_button = tkinter.Button(self.settings, text="Ok", command=lambda *args: self.close_settings(True))
            cancel_button = tkinter.Button(self.settings, text="Cancel",
                                           command=lambda *args: self.close_settings(False))
            ok_button.grid(column=0, row=5)
            cancel_button.grid(column=1, row=5)
            self.settings.lift()

    def snapshot(self):
        # Get a frame from the video source
        ranges = [[self.lower_range_guide, self.upper_range_guide], [self.lower_range_tree, self.upper_range_tree],
                  [self.lower_range_hand, self.upper_range_hand]]
        ret, frame = self.cap.update(ranges=ranges)  # lower_range=self.lower_range, upper_range=self.upper_range,

        if ret:
            cv2.imwrite("frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg", frame[4])


    def update(self):
        # Get a frame from the video source
        ranges = [[self.lower_range_guide, self.upper_range_guide], [self.lower_range_tree, self.upper_range_tree],
                  [self.lower_range_hand, self.upper_range_hand]]
        ret, self.frames = self.cap.update(ranges=ranges, go_left_size=self.distance)
        if ret:
            if self.current_output > 3:
                self.photos = []
                for i in range(4):
                    if self.frames[i] is not None:
                        self.frames[i] = cv2.resize(self.frames[i],
                                                    (int(self.frames[0].shape[1]), int(self.frames[0].shape[0])))
                        self.photos.append(
                            PIL.ImageTk.PhotoImage(master=self.canvas, image=PIL.Image.fromarray(self.frames[i])))
                        x, y = divmod(i, 2)

                        self.canvas.create_image(x * self.frames[0].shape[1], y * self.frames[0].shape[0],
                                                 image=self.photos[i],
                                                 anchor=tkinter.NW)
            else:
                frame = self.frames[self.current_output]
                frame = cv2.resize(frame, (int(frame.shape[1] * 2), int(frame.shape[0] * 2)))
                self.photo = PIL.ImageTk.PhotoImage(master=self.canvas, image=PIL.Image.fromarray(frame))
                self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)

        self.window.after(self.delay, self.update)

    def read_defaults(self):
        try:
            textFile = open("config.txt", "r")
            lines = textFile.readlines()

            lower_range_default = lines[1]  # first line = warning
            lower_range_default = lower_range_default.split(":")
            lower_range_default = lower_range_default[1].strip()
            lower_range_default = lower_range_default.replace(" ", "")
            lower_range_default = lower_range_default.split(",")
            self.lower_range_guide = np.array(
                [int(lower_range_default[0]), int(lower_range_default[1]), int(lower_range_default[2])])
            print(self.lower_range_guide)

            upper_range_default = lines[2]  # first line = warning
            upper_range_default = upper_range_default.split(":")
            upper_range_default = upper_range_default[1].strip()
            upper_range_default = upper_range_default.replace(" ", "")
            upper_range_default = upper_range_default.split(",")
            self.upper_range_guide = np.array(
                [int(upper_range_default[0]), int(upper_range_default[1]), int(upper_range_default[2])])

            distance_default = lines[3]
            distance_default = distance_default.split(":")
            distance_default = distance_default[1].strip()
            distance_default = distance_default.replace(" ", "")
            self.distance = int(distance_default)

            lower_range_default = lines[4]
            lower_range_default = lower_range_default.split(":")
            lower_range_default = lower_range_default[1].strip()
            lower_range_default = lower_range_default.replace(" ", "")
            lower_range_default = lower_range_default.split(",")
            self.lower_range_tree = np.array(
                [int(lower_range_default[0]), int(lower_range_default[1]), int(lower_range_default[2])])

            upper_range_default = lines[5]
            upper_range_default = upper_range_default.split(":")
            upper_range_default = upper_range_default[1].strip()
            upper_range_default = upper_range_default.replace(" ", "")
            upper_range_default = upper_range_default.split(",")
            self.upper_range_tree = np.array(
                [int(upper_range_default[0]), int(upper_range_default[1]), int(upper_range_default[2])])

            lower_range_default = lines[6]
            lower_range_default = lower_range_default.split(":")
            lower_range_default = lower_range_default[1].strip()
            lower_range_default = lower_range_default.replace(" ", "")
            lower_range_default = lower_range_default.split(",")
            self.lower_range_hand = np.array(
                [int(lower_range_default[0]), int(lower_range_default[1]), int(lower_range_default[2])])

            upper_range_default = lines[7]
            upper_range_default = upper_range_default.split(":")
            upper_range_default = upper_range_default[1].strip()
            upper_range_default = upper_range_default.replace(" ", "")
            upper_range_default = upper_range_default.split(",")
            self.upper_range_hand = np.array(
                [int(upper_range_default[0]), int(upper_range_default[1]), int(upper_range_default[2])])
            textFile.close()

        except FileNotFoundError:
            self.update_defaults()
        except IndexError:
            textFile.close()
            self.update_defaults()

    def update_defaults(self):
        print("Updating defaults")
        timeStamp = datetime.datetime.now().strftime("%b-%d-%y-%H%M%S")
        fileName = "config_{}.txt".format(timeStamp)
        print(fileName)
        textFileBackup = open(fileName, "w+")
        textFile = open("config.txt", "w+")
        textFileBackup.writelines([l for l in textFile.readlines()])
        textFileBackup.close()
        textFile.write("DO NOT MODIFY THIS FILE UNLESS YOU KNOW WHAT YOU ARE DOING! \n")
        lower_range_string = "Lower range guide: {}, {}, {} \n".format(self.lower_range_guide[0],
                                                                       self.lower_range_guide[1],
                                                                       self.lower_range_guide[2])
        upper_range_string = "Upper range guide: {}, {}, {} \n".format(self.upper_range_guide[0],
                                                                       self.upper_range_guide[1],
                                                                       self.upper_range_guide[2])
        distance_string = "Distance: {} \n".format(self.distance)
        lower_range_tree_string = "Lower range tree: {}, {}, {} \n".format(self.lower_range_tree[0],
                                                                           self.lower_range_tree[1],
                                                                           self.lower_range_tree[2])
        upper_range_tree_string = "Upper range tree: {}, {}, {} \n".format(self.upper_range_tree[0],
                                                                           self.upper_range_tree[1],
                                                                           self.upper_range_tree[2])
        lower_range_hand_string = "Lower range hand: {}, {}, {} \n".format(self.lower_range_hand[0],
                                                                           self.lower_range_hand[1],
                                                                           self.lower_range_hand[2])
        upper_range_hand_string = "Upper range hand: {}, {}, {} \n".format(self.upper_range_hand[0],
                                                                           self.upper_range_hand[1],
                                                                           self.upper_range_hand[2])
        textFile.write(lower_range_string)
        textFile.write(upper_range_string)
        textFile.write(distance_string)
        textFile.write(lower_range_tree_string)
        textFile.write(upper_range_tree_string)
        textFile.write(lower_range_hand_string)
        textFile.write(upper_range_hand_string)
        textFile.close()


class Client(WebSocketClient):
    def opened(self):
        print("Websocket open")

    def closed(self, code, reason=None):
        print("Connexion closed down", code, reason)

    def received_message(self, m):
        print(m)


def set_connection(cap):
    esp8266host = "ws://192.168.2.44:81/"
    ws = Client(esp8266host)
    ws.connect()

    while True:
        send_string = ""
        if cap.turn_around is True:
            send_string = "E\n"
            cap.turn_around = False
            print("End detected from stuff")
        elif cap.tree_detected is True:
            print("Tree found from stuff")
            send_string = "T\n"
        else:
            send_string = "D{}\n".format(cap.direction)
        ws.send(send_string)
        send_string = send_string.rstrip("\n")
        print(f'{send_string}\r', end="")
        time.sleep(.20)


Vision = VisionHandler(0)
t = Thread(target=set_connection, args=(Vision,))
t.start()


# Create a window and pass it to the Application object
App(tkinter.Tk(), "Tkinter and OpenCV", Vision)
