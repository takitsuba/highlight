import fitz
from fitz.utils import getColor


def main():
    file = "data/input/Can Large Language Models Be an Alternative to Human Evaluations?.pdf"
    doc = fitz.open(file)
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

    doc.save("data/output/highlighted.pdf", garbage=4, deflate=True)


if __name__ == "__main__":
    main()
