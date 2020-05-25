
from Vision2 import VisionHandler
import numpy as np
import colorsys
import datetime




def rgbtohsv(rgb):
    hsv = colorsys.rgb_to_hsv(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)
    hsvColor = np.array([int(hsv[0] * 179), int(hsv[1] * 255), int(hsv[2] * 255)])
    return hsvColor


def hsvtorgb(hsv):
    rgb = colorsys.hsv_to_rgb(hsv[0] / 179, hsv[1] / 255, hsv[2] / 255)
    rgbColor = [int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)]
    return rgbColor


class NoGUI:

    def __init__(self):
        self.video_source = 0
        self.cap = VisionHandler(self.video_source)
        self.lower_range_guide = np.array([85, 100, 50])
        self.upper_range_guide = np.array([150, 255, 255])
        self.lower_range_tree = np.array([85, 100, 50])
        self.upper_range_tree = np.array([150, 255, 255])
        self.lower_range_hand = np.array([85, 100, 50])
        self.upper_range_hand = np.array([150, 255, 255])
        self.distance = 50
        self.read_defaults()
        self.update()

    def update(self):
        # Get a frame from the video source
        while True:
            ranges = [[self.lower_range_guide, self.upper_range_guide], [self.lower_range_tree, self.upper_range_tree], [self.lower_range_hand, self.upper_range_hand]]
            ret = self.cap.update(ranges=ranges, go_left_size=self.distance, no_gui=True)

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


# Create a window and pass it to the Application object
VisionHandler()
