"""
Intended to contain some basic PDF utilities
"""

import sys
from pathlib import Path

import rich
import rich.prompt
from rich import print as rprint
from rich.pretty import pprint as rpprint

from borb.pdf.document import Document
from borb.pdf.pdf import PDF


def get_file(
    prompt: str = "\nWhat file do you want to open",
    allow_exists: bool = False,
    allow_missing: bool = False,
) -> Path:
    """
    Get a file path.

    :return:
    """

    path = rich.prompt.Prompt.ask(prompt).strip('"')

    if str(path) == "":
        raise ValueError(f"Expected a path to a file, received: {path}")

    path = Path(path)

    if not allow_exists and path.exists():
        raise FileExistsError(f"Cannot use existing file {path}")

    if not allow_missing and not path.exists():
        raise FileNotFoundError(f"Could not find {path}")

    return path


def merge_pdfs():
    """
    Provide a UI around the borb PDF Library to merge PDFs together.
    """

    rprint("\n[bold]Merge PDF Files[/bold]")
    rprint("Files will be merged in the order selected.")

    files = []

    def get_more():
        return rich.prompt.Confirm.ask("\nDo you want to add more files?")

    files.append(get_file())

    add_more = get_more()

    while add_more:

        if add_more:
            files.append(get_file())

        add_more = get_more()

    rprint("\nAbout to combine the following files in order:")
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

    out_file = Path(rich.prompt.Prompt.ask("\nWhere do you want to save").strip())

    if out_file.exists():
        raise FileExistsError(f"File {out_file} already exists. No overwrite.")

    with open(out_file, "wb") as file_handle:
        PDF.dumps(file_handle, out)


def rotate_page():
    """
    Provide a UI around the borb PDF library to rotate pages.
    """

    in_file = get_file(allow_exists=True)

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
        out_file = get_file(
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
