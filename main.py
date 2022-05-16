import multiprocessing
import random
import time
from enum import Enum, auto
from pathlib import Path

import PySimpleGUI as sg
from PIL import Image, ImageTk, ImageOps

from bst import Tree
from utils import IMAGE_FOLDER_NAME, COLOR_MAP, draw_image, update_image, prepare_folder

image_counter = 0
image_completion_count = 0
Image.MAX_IMAGE_PIXELS = None


class Actions(Enum):
    UPDATE_IMAGE = auto()
    RESET = auto()
    IMAGE = auto()
    LOAD_IMAGES = auto()
    BROWSE_IMAGES = auto()


def validate_rgb(values: dict) -> bool:
    """
    Validate values of dict
    :param values:
    :return: True if values in dict are RGB
    """
    return all(
        map(lambda k: values[k].isdigit() and int(values[k]) in range(256), list("RGB"))
    )


def update_image_counter(_):
    """Callback to increment number of processed images"""
    global image_counter
    image_counter += 1


def generate_images() -> None:
    """Clear image folder and generate images"""
    global image_counter
    prepare_folder()
    path = Path(IMAGE_FOLDER_NAME)
    progress_bar = [
        [
            sg.ProgressBar(1, size=(40, 20), pad=(0, 0), key="Progress Bar"),
            sg.Text("  0%", size=(4, 1), key="Percent"),
        ],
    ]
    layout = [
        [sg.Text("Write number of pictures you want to generate")],
        [
            sg.InputText(key="execute"),
            sg.Button("Execute Process"),
            sg.Exit(button_text="Stop"),
        ],
        [sg.pin(sg.Column(progress_bar, key="Progress", visible=True))],
    ]

    window = sg.Window("Image uploader", layout, size=(450, 100), modal=True)
    percent = window["Percent"]
    progress_bar = window["Progress Bar"]
    pictures_number = None
    while True:
        pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())

        event, values = window.read(timeout=100)
        if event == "Execute Process":
            if not values["execute"].isdigit():
                sg.popup_error("Enter integer value")
                continue
            pictures_number = int(values["execute"])
            progress_bar.UpdateBar(image_counter, pictures_number)
            window["Execute Process"].update(disabled=True)
            for color in random.sample(COLOR_MAP, pictures_number):
                pool.apply_async(
                    draw_image, args=(path, color), callback=update_image_counter
                )
        elif image_counter == pictures_number:
            percent.update(value="100%")
            progress_bar.update(current_count=image_counter)
            window.refresh()
            time.sleep(1)
            break

        if event == "Stop" or event == sg.WIN_CLOSED:
            break

        progress_bar.update(current_count=image_counter)
        percent.update(
            value=f"{int(image_counter / pictures_number * 100) if pictures_number else 0:>3d}%"
        )
        window.refresh()
    image_counter = 0
    pool.terminate()
    window.close()


def main() -> None:
    tree = None
    layout = [
        [
            sg.Button(
                button_text="Reset/Setup Image Folder", size=(100, 2), key=Actions.RESET
            )
        ],
        [sg.Text("Find a picture by RGB key and change it", justification="c")],
        [
            sg.Text(
                "R",
            ),
            sg.InputText(size=(5, 1), key="R"),
        ],
        [
            sg.Text(
                "G",
            ),
            sg.InputText(size=(5, 1), key="G"),
        ],
        [
            sg.Text(
                "B",
            ),
            sg.InputText(size=(5, 1), key="B"),
        ],
        [sg.Button("Submit", key=Actions.UPDATE_IMAGE)],
        [sg.Image(size=(1, 1), key=Actions.IMAGE)],
        [sg.Text("Images to load: ", key="ImageOutput")],
        [
            sg.FilesBrowse(key=Actions.BROWSE_IMAGES),
            sg.Button("Submit", key=Actions.LOAD_IMAGES),
        ],
        [sg.Output(size=(100, 15), key="ImagesOutput")],
    ]
    window = sg.Window("Progress Bar", layout, size=(640, 480))

    while True:
        event, values = window.read(timeout=1000)
        image_output = list(filter(None, values[Actions.BROWSE_IMAGES].split(";")))
        window["ImageOutput"].update(f"Images to load: {len(image_output)}")
        if event == Actions.UPDATE_IMAGE:
            if validate_rgb(values):
                if not tree:
                    sg.popup("Please, provide images")
                    # Create BST with images
                elif image := tree.find(tuple(int(values[k]) for k in list("RGB"))):
                    update_image(image)
                    sg.popup("Sucsessfully updated image", button_color="green")
                    window["R"].update("")
                    window["G"].update("")
                    window["B"].update("")
                    image = ImageTk.PhotoImage(
                        image=ImageOps.expand(
                            image.resize((100, 100)), border=2, fill="black"
                        )
                    )

                    # update image in sg.Image
                    window[Actions.IMAGE].update(data=image)
                else:
                    sg.popup(
                        "We didn't find any image, please try again",
                        button_color="blue",
                    )
                    r, g, b = tree.root.image.getpixel((1, 1))
                    window["R"].update(r)
                    window["G"].update(g)
                    window["B"].update(b)
            else:
                sg.popup_error(
                    "Please, provide value greater than zero in range (0, 255) inclusively"
                )
        elif event == Actions.LOAD_IMAGES:
            if not values[Actions.BROWSE_IMAGES]:
                sg.popup_error("Please, choose at least 1 image")

            image_fnames = values[Actions.BROWSE_IMAGES].split(";")
            window["ImagesOutput"].update("")
            window["ImageOutput"].update(f"Load image: {len(image_fnames)}")
            tree = Tree(Image.open(fn) for fn in image_fnames)
            print("\n".join(image_fnames))

        elif event == Actions.RESET:
            generate_images()
        elif event == sg.WIN_CLOSED:
            break

    window.close()


if __name__ == "__main__":
    main()
