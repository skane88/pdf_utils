"""
Intended to contain some basic PDF utilities
"""

import sys
import tkinter as tk
import tkinter.filedialog as fd
from pathlib import Path
from typing import List

import rich
import rich.prompt
from borb.pdf.document import Document
from borb.pdf.pdf import PDF
from rich import print as rprint
from rich.pretty import pprint as rpprint

PDF_EXT = ".pdf"


def get_files(
    prompt: str = "\nWhat file do you want to open",
    open_dialog: bool = True,
    multiple: bool = True,
    allow_exists: bool = False,
    allow_missing: bool = False,
) -> List[Path]:
    """
    Get a file path.

    :return:
    """

    rprint(prompt)

    root = tk.Tk()
    root.withdraw()

    FILE_TYPE = "PDF Files"

    if open_dialog:
        if multiple:
            files = fd.askopenfilenames(
                parent=root,
                title="Choose Files",
                filetypes=[(FILE_TYPE, "*" + PDF_EXT)],
            )
        else:
            files = [
                fd.askopenfilename(
                    parent=root,
                    title="Choose File",
                    filetypes=[(FILE_TYPE, "*" + PDF_EXT)],
                )
            ]
    else:
        files = [
            fd.asksaveasfilename(
                parent=root, title="Choose File", filetypes=[(FILE_TYPE, "*" + PDF_EXT)]
            )
        ]

    root.destroy()

    ret_files = []

    for f in files:

        path = f.strip('"').strip("'")

        if str(path) == "":
            raise ValueError(f"Expected a path to a file, received: {path}")

        path = Path(path)

        if path.suffix.lower() != PDF_EXT:
            path = path.with_suffix(PDF_EXT)

        if not allow_exists and path.exists():
            raise FileExistsError(f"Cannot use existing file {path}")

        if not allow_missing and not path.exists():
            raise FileNotFoundError(f"Could not find {path}")

        ret_files.append(path)

    return ret_files


def merge_pdfs():
    """
    Provide a UI around the borb PDF Library to merge PDFs together.
    """

    rprint("\n[bold]Merge PDF Files[/bold]")
    rprint("Files will be merged in the order selected.")

    files = []

    def get_more():
        return rich.prompt.Confirm.ask("\nDo you want to add more files?")

    add_more = True

    while add_more:

        if add_more:
            files += get_files(allow_exists=True, allow_missing=False)

        add_more = get_more()

    rprint("\nAbout to combine the following files in the listed order:")
    rpprint(files)

    cont = rich.prompt.Confirm.ask("\nDo you wish to continue?")

    if not cont:
        return

    pdfs = []

    for f in files:

        if not f.exists():
            raise FileNotFoundError(f"File {f} not found.")

        with open(f, "rb") as file_handle:
            pdfs.append(PDF.loads(file_handle))

    out = Document()

    for p in pdfs:
        out.append_document(p)

    out_file = get_files(
        prompt="\nWhere do you want to save",
        open_dialog=False,
        allow_exists=False,
        allow_missing=True,
    )[0]

    with open(out_file, "wb") as file_handle:
        PDF.dumps(file_handle, out)


def rotate_page():
    """
    Provide a UI around the borb PDF library to rotate pages.
    """

    in_file = get_files(allow_exists=True)[0]

    page_no = rich.prompt.IntPrompt.ask(
        "Which page do you wish to rotate", default=1, show_default=True
    )

    rot_amount = rich.prompt.Prompt.ask(
        choices=["CW", "CCW", "180"], default="CW", show_default=True, show_choices=True
    )

    with open(in_file, "rb") as pdf_file:
        pdf = PDF.loads(pdf_file)

    # rotate the page

    page_no = page_no - 1  # decrement page no. as borb uses 0 based indexing.

    if rot_amount == "CW":
        pdf.get_page(page_no).rotate_right()
    elif rot_amount == "CCW":
        pdf.get_page(page_no).rotate_left()
    else:
        pdf.get_page(page_no).rotate_left()
        pdf.get_page(page_no).rotate_left()

    overwrite = not rich.prompt.Confirm.ask("Do you want to save to a different file?")

    if overwrite:
        if not rich.prompt.Confirm.ask(
            "Existing file will be overwritten - do you want to continue?"
        ):
            return

        out_file = in_file
    else:
        out_file = get_files(
            prompt="Where do you want to save the file?", allow_missing=True
        )

    with open(out_file, "wb") as pdf_file:
        PDF.dumps(pdf_file, pdf)


def quit_func():
    """
    Basic quit functionality.
    """

    rprint("Goodbye!")
    sys.exit()


def main():

    rprint("Select from the options below:\n")

    option_dict = {
        1: ("Merge PDFs", merge_pdfs),
        2: ("Rotate Page", rotate_page),
        10: ("Quit", quit_func),
    }

    while True:
        while True:

            for o, v in option_dict.items():
                rprint(f"{o:03}: {v[0]}")

            choice = rich.prompt.IntPrompt.ask("\nChoose which option you want to use")

            if choice in option_dict:
                break
            else:
                rprint(
                    f"[red]Your choice ([italic]{choice}[/italic]) "
                    + "was not in the list of available choices[/red]\n"
                )

        option_dict[choice][1]()
        rprint("\n")


if __name__ == "__main__":

    main()
