import argparse
import os
import json
import fitz
from fitz.utils import getColor

current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_dir, "..", "..", "data")


def get_color_phrases():
    """
    color_phrases is Dict like
    {
        "color1": ["phrase1", "phrase2"],
        "color2": ["phrase3"],
    }

    Colors list is in `scripts/`
    """
    color_phrases_path = os.path.join(
        current_dir, "..", "..", "color_phrases.json"
    )
    with open(color_phrases_path, "r") as file:
        color_phrases = json.load(file)

    return color_phrases


def extract_locs_by_phrase(page, phrase):
    # phrase: "On the contrary"
    # words: ["On", "the", "contrary"]
    words = phrase.split(" ")

    word_locs = page.get_text("words")

    # Format of a word_loc: (x0, y0, x1, y1, "word", block_no, line_no, word_no)
    # ref. https://pymupdf.readthedocs.io/en/latest/textpage.html#TextPage.extractWORDS
    word_idx = 4
    extracted_locs = []
    for start in range(len(word_locs) - len(words) + 1):
        for i in range(len(words)):
            idx = start + i
            if word_locs[idx][word_idx] != words[i]:
                break
        else:
            # when not break
            for fidx in range(start, start + len(words)):
                extracted_locs.append(word_locs[fidx][:word_idx])

    return extracted_locs


def highlight_in_color(page, locs, color: str):
    highlight = page.add_highlight_annot(locs)
    rgb = getColor(color.upper())
    highlight.set_colors(stroke=rgb)
    highlight.update()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_pdf", help="the path of input pdf")
    args = parser.parse_args()
    input_pdf_path = args.input_pdf
    input_pdf_filename = os.path.basename(input_pdf_path)
    doc = fitz.open(input_pdf_path)

    color_phrases = get_color_phrases()

    for color, phrases in color_phrases.items():
        for phrase in phrases:
            for page in doc:
                extracted_locs = extract_locs_by_phrase(page, phrase)
                highlight_in_color(page, extracted_locs, color)

    output_dir = os.path.join(data_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    output_pdf_filename = input_pdf_filename
    output_path = os.path.join(output_dir, output_pdf_filename)
    doc.save(output_path, garbage=4, deflate=True)


if __name__ == "__main__":
    main()
