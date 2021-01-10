from ApplicationState import ApplicationState

import os
import cv2
from threading import Thread
from typing import Union


class Application:

    def __init__(self, label: str = "Shoplifting"):
        self.state = ApplicationState()
        self.label = label
        self.labels_path = None
        self.t: Union[Thread, None] = None

        self.commands = [
            "n",
            "next",
            "p",
            "prev",
            "close",
            "open",
            "add",
            "cur",
            "list",
            "l",
            "save",
            "s",
            "go",
            "g",
            "del",
            "d",
            "exit"
        ]

    def show_video(self):

        while True:

            if self.state.stream is not None:

                cv2.imshow(self.state.filename, self.state.frame())
                cv2.waitKey(50)
            else:
                break

        cv2.destroyAllWindows()

    def open(self, video_path: str):
        if os.path.exists(video_path):
            self.state.open(video_path)
            self.t = Thread(target=self.show_video)
            self.t.start()
        else:
            print(f"{video_path} does not exist.")

    def load(self, labels_path: str = "labels.txt"):
        if self.state.filename is None:
            print("First open a video file.")

        elif os.path.exists(os.path.join(os.getcwd(), labels_path)):
            self.labels_path = labels_path
        else:
            print(f"{labels_path} does not exist.")

    def close(self):
        self.state.close()
        self.t.join()
        self.t = None

    def __del__(self):
        if self.t is not None:
            self.t.join()
            self.t = None

    def run(self):

        while True:

            line = input("|>> ")
            words = line.split()

            if not len(words):
                continue

            cmd = words[0]

            if cmd == "exit":
                yes_no = input("Are you sure (y/n)?\n")
                if yes_no == "y":
                    self.close()
                    break

            elif cmd == "open":
                try:
                    filepath = words[1]
                    self.open(filepath)

                except IndexError:
                    print("Example Usage : open /path/to/file.txt\n")

            elif cmd == "load":
                try:
                    filepath = words[1]
                    self.load(filepath)

                except IndexError:
                    print("Example Usage : load /path/to/file.txt\n")


            elif cmd == "close":
                if self.t is not None:
                    self.close()


            elif cmd == "play":
                self.state.play()

            elif cmd == "pause":
                self.state.pause()

            else:
                print(f"No command found {cmd}")
