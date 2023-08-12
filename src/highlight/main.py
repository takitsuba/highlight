import argparse
import os
import json
import fitz
from fitz.utils import getColor

current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_dir, "..", "..", "data")


def get_color_words():
    """
    color_words is Dict like
    {
        "color1": ["word1", "word2"],
        "color2": ["word3"],
    }

    Colors list is in `scripts/`
    """
    color_words_path = os.path.join(
        current_dir, "..", "..", "color_words.json"
    )
    with open(color_words_path, "r") as file:
        color_words = json.load(file)

    return color_words


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_pdf", help="the path of input pdf")
    args = parser.parse_args()
    input_pdf_path = args.input_pdf
    input_pdf_filename = os.path.basename(input_pdf_path)
    doc = fitz.open(input_pdf_path)

    color_words = get_color_words()

    for color, targets in color_words.items():
        for target in targets:
            for current_page in range(len(doc)):
                page = doc.load_page(current_page)
                word_locs = page.get_text("words")

                # Format of a word_loc: (x0, y0, x1, y1, "word", block_no, line_no, word_no)
                # ref. https://pymupdf.readthedocs.io/en/latest/textpage.html#TextPage.extractWORDS
                word_idx = 4
                filtered_locs = [
                    word_loc[:word_idx]  # loc
                    for word_loc in word_locs
                    if word_loc[word_idx] == target  # filter by word
                ]

                highlight = page.add_highlight_annot(filtered_locs)
                rgb = getColor(color.upper())
                highlight.set_colors(stroke=rgb)
                highlight.update()

    output_pdf_filename = "hl_" + input_pdf_filename
    output_path = os.path.join(data_dir, "output", output_pdf_filename)
    doc.save(output_path, garbage=4, deflate=True)


if __name__ == "__main__":
    main()
