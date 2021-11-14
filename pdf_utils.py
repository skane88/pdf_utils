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


def merge_pdfs():

    rprint("\n[bold]Merge PDF Files[/bold]")
    rprint("Files will be merged in the order selected.")

    files = []

    def get_file():
        return Path(
            rich.prompt.Prompt.ask("\nWhat file do you want to open").strip('"')
        )

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


def quit_func():

    rprint("Goodbye!")
    sys.exit()


def main():

    rprint("Select from the options below:\n")

    option_dict = {1: ("Merge PDFs", merge_pdfs), 10: ("Quit", quit_func)}

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
