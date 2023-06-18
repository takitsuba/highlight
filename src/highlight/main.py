import fitz

file = "data/input/Can Large Language Models Be an Alternative to Human Evaluations?.pdf"
doc = fitz.open(file)
search_term = "First"

for current_page in range(len(doc)):
    page = doc.load_page(current_page)
    if page.search_for(search_term):
        text_instances = page.search_for(search_term)

        for inst in text_instances:
            highlight = page.add_highlight_annot(inst)
            highlight.update()

doc.save("data/output/highlighted.pdf", garbage=4, deflate=True)
