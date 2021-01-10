from bumblebee.sources import FileStream
from bumblebee.effects import GoTo, CurrentFrame
from functools import wraps
from typing import Union, Tuple, List
import numpy as np
from helpers import precondition

import os


def update_frame(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        ret_value = func(*args, **kwargs)
        self: ApplicationState = args[0]

        self._read_given_frame(int(ret_value))
        return int(ret_value)

    return wrapper


class ApplicationState:

    def __init__(self):
        self.filename: Union[None, str] = None
        self._frame: Union[None, np.array] = None
        self.current_annotation: Union[None, int] = None
        self.all_annotations: Union[None, List[Tuple[int, int]]] = None
        self.stream: Union[None, FileStream] = None

        self._goto: Union[None, GoTo] = None
        self._current_frame: Union[None, CurrentFrame] = None
        self._duration: Union[None, int] = None
        self.playing = False


    @update_frame
    @precondition(lambda *args, **kwargs: args[0].stream is not None)
    def next(self, frame_number=1):
        goto_index = self._current_frame() + frame_number

        if goto_index > self._duration:
            print(f"Next has no effect. You've reached end of the video.")

        goto_index = min(goto_index, self._duration)

        self._goto(goto_index)
        return goto_index

    @update_frame
    @precondition(lambda *args, **kwargs: args[0].stream is not None)
    def prev(self, frame_number=1):

        goto_index = self._current_frame() - frame_number

        if goto_index < 0:
            print(f"Prev has no effect. You've reached beginning of the video.")

        goto_index = max(0, goto_index)
        self._goto(goto_index)

        return goto_index

    @update_frame
    @precondition(lambda *args, **kwargs: args[0].stream is not None)
    def goto(self, frame_number):

        self._goto(frame_number)
        return frame_number

    @precondition(lambda *args, **kwargs: args[0].stream is not None)
    def current_frame(self):
        return self._current_frame()

    @update_frame
    def open(self, path: str):

        if self.stream:
            self.close()

        self.filename = os.path.basename(path)
        self.stream = FileStream(path)
        self.current_annotation = None
        self._goto = GoTo(self.stream)
        self._current_frame = CurrentFrame(self.stream)
        self.all_annotations = []
        self._frame = self.stream.read()
        self._duration = self.stream.get_duration()
        self.playing = False

        return 0

    @precondition(lambda *args, **kwargs: args[0].stream is not None)
    def close(self):
        self.stream.close()
        self.filename = None
        self.stream = None
        self.current_annotation = None
        self._goto = None
        self._current_frame = None
        self.all_annotations = None
        self._frame = None
        self._duration = None
        self.playing = False


    def __del__(self):
        if self.stream:
            self.close()

    @precondition(lambda *args, **kwargs: args[0].stream is not None)
    def frame(self):

        if self.playing:
            self._frame = self.stream.read()

        return self._frame

    @precondition(lambda *args, **kwargs: args[0].stream is not None)
    def add(self, frame_number: Union[None, int] = None):

        if not frame_number:
            frame_number = self._current_frame()

        if self.current_annotation is not None:
            self.all_annotations.append((self.current_annotation, frame_number))
            self.current_annotation = None
        else:
            self.current_annotation = frame_number

    def _read_given_frame(self, frame_number):

        current_frame = self._current_frame()
        self._goto(frame_number)
        self._frame = self.stream.read()
        self._goto(current_frame)

    @precondition(lambda *args, **kwargs: args[0].stream is not None)
    def list_annotations(self):

        full_annotations = "\n".join(
            [f"{ind + 1}.  {start} - {end}" for ind, (start, end) in enumerate(self.all_annotations)])
        current_annotation = ""
        if self.current_annotation is not None:
            current_annotation += f"{len(self.all_annotations) + 1}. {self.current_annotation} - \n"

        return full_annotations + current_annotation

    @precondition(lambda *args, **kwargs: args[0].stream is not None)
    def del_annotation(self,anno_index : int):

        if anno_index == len(self.all_annotations) + 1 and self.current_annotation is not None:
            self.current_annotation = None
        else:
            try:
                self.all_annotations.pop(anno_index-1)
            except IndexError:
                print(f"No annotation is available at given index {anno_index}")


    @precondition(lambda *args, **kwargs: args[0].stream is not None)
    def init_annotations(self,annotations : [(int,int)]):

        self.all_annotations = annotations

    @precondition(lambda *args, **kwargs: args[0].stream is not None)
    def play(self):
        self.playing = True

    @precondition(lambda *args, **kwargs: args[0].stream is not None)
    def pause(self):
        self.playing = False