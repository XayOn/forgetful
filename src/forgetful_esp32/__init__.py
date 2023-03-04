# SPDX-FileCopyrightText: 2023-present David Francos <me@davidfrancos.net>
import asyncio
from asyncio import Queue
from collections import Counter
from contextlib import suppress
import io
import os

from PIL import Image
import httpx
from numpy import asarray

from deepsparse import Pipeline
from ultralytics import YOLO

# TODO: Not the best tts out there, but TTS is having conflicts with yolov8
import pyttsx3

engine = pyttsx3.init()
model = YOLO("yolov8n.pt")
model_path = "yolov8n.onnx"
yolo_pipeline = Pipeline.create(
    task="yolov8",
    model_path=model_path,
)


async def get_next_image(iterator):
    headers = {}

    _ = await anext(iterator)  # delimiter
    headers_ = await anext(iterator)
    for header in headers_.strip().split(b"\r\n"):
        try:
            key, value = header.split(b": ")
        except ValueError:
            return
        headers[key.decode()] = value.decode()

    # Sometimes we receive the delimiter twice
    if headers.get("Content-Type") != "image/jpeg":
        return

    read_data = b""

    while len(read_data) != int(headers["Content-Length"]):
        read_data += await anext(iterator)

    return read_data


async def process_video(url: str, queue: Queue):
    """Process video in streaming mode."""
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", url) as resp:
            iterator = resp.aiter_bytes()
            while image := await get_next_image(iterator):
                if not queue.full():
                    images = [asarray(Image.open(io.BytesIO(image)))]
                    await queue.put(images)


async def process_objects(queue):
    """Read from queue and try to recognize objects"""
    while item := await queue.get():
        outs = yolo_pipeline(images=item)
        if res := [model.model.names[int(float(a))] for a in outs.labels[0]]:
            for element, number in Counter(res).items():
                print(f'{number} {element}{"s"*int(number > 1)}')
                engine.say(f'{number} {element}{"s"*int(number > 1)}')
                engine.runAndWait()


async def main():
    """Only process one image at a time.

    But keep consuming them so that our feed is "clean".
    TODO: That might be something with my firmware...
    """
    while True:
        with suppress(Exception):
            queue = Queue(maxsize=1)
            await asyncio.gather(
                process_video(os.getenv("STREAM_URL", ""), queue),
                process_objects(queue),
            )


def run_main():
    asyncio.run(main())


if __name__ == "__main__":
    run_main()
