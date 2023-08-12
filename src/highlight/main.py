import argparse
import os
import fitz
from fitz.utils import getColor

current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_dir, "..", "..", "data")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input_pdf", help="the path of input pdf", required=True
    )
    args = parser.parse_args()

    doc = fitz.open(args.input_pdf)

    search_term = "Human"

    for current_page in range(len(doc)):
        page = doc.load_page(current_page)
        if page.search_for(search_term):
            # use quads because developers strongly recommend
            # ref. https://pymupdf.readthedocs.io/en/latest/page.html#Page.add_highlight_annot
            text_quads = page.search_for(search_term, quads=True)
            highlight = page.add_highlight_annot(text_quads)
            rgb = getColor("PLUM1")
            highlight.set_colors(stroke=rgb)
            highlight.update()

    output_path = os.path.join(data_dir, "output", "highlighted.pdf")
    doc.save(output_path, garbage=4, deflate=True)


if __name__ == "__main__":
    main()
