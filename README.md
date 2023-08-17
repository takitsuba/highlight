# highlight

Highlight specific strings of text in a PDF.

# Prerequisites

In order to use highlight, please make sure you have the [rye](https://rye-up.com/guide/installation/) tool installed on your machine.

## Installation

Follow these steps to get started with Highlight.

1. Clone this repository:

```bash
git clone <this repository>
```

2. Change into the `highlight` directory:

```bash
cd highlight
```

3. Sync using `rye`:

```bash
rye sync
```

4. Make a copy of the `color_phrases.json` file:

```bash
cp color_phrases.json.sample color_phrases.json
```

5. Customize your color and phrases:

You can customize the colors and phrases according to your preference. Please refer to the [scripts/color_list.pdf](https://github.com/takitsuba/highlight/blob/main/scripts/color_list.pdf) for color options.


## Running Highlight

To start using highlight, run the following command:

```bash
rye run python src/highlight/main.py <pdf_path>
```
Replace `<pdf_path>` with the path to your PDF file.
