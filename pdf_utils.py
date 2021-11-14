"""
Intended to contain some basic PDF utilities
"""

from pathlib import Path

from borb.pdf.pdf import PDF
from borb.pdf.document import Document

import rich, rich.prompt


def merge_pdfs():

    files = []

    def get_file():
        return Path(rich.prompt.Prompt.ask("\nWhat file do you want to open").strip('"'))

    def get_more():
        return rich.prompt.Confirm.ask("\nDo you want to add more files?")

    files.append(get_file())

    add_more = get_more()

    while add_more:

        if add_more:
            files.append(get_file())

        add_more = get_more()

    pdfs = []

    for f in files:
        with open(f, "rb") as file_handle:
            pdfs.append(PDF.loads(file_handle))

    out = Document()

    for p in pdfs:
        out.append_document(p)

    out_file = Path(rich.prompt.Prompt.ask("\nWhere do you want to save").strip())

    if out_file.exists():
        raise FileExistsError()

    with open(out_file, "wb") as file_handle:
        PDF.dumps(file_handle, out)


def main():

    rich.print("Select from the options below:\n")

    option_dict = {1: ("Merge PDFs", merge_pdfs)}

    for o, v in option_dict.items():
        rich.print(f"{o:03}: {v[0]}")

    while True:
        choice = rich.prompt.IntPrompt.ask("\nChoose which option you want to use")

        if choice in option_dict:
            break
        else:
            rich.print(
                f"[red]Your choice ([italic]{choice}[/italic]) "
                + "was not in the list of available choices[/red]"
            )

    option_dict[choice][1]()


if __name__ == "__main__":

    main()
