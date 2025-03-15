# Standard Library
import argparse
import json
import os

# Third Party Library
import fitz
from fitz.utils import getColor
from tqdm import tqdm

current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_dir, "..", "..", "data")


def get_color_phrases():
    """
    color_phrases.jsonファイルから色とフレーズのマッピングを取得する

    color_phrases is Dict like
    {
        "color1": ["phrase1", "phrase2"],
        "color2": ["phrase3"],
    }

    Returns:
        dict: 色とフレーズのマッピング
    """
    color_phrases_path = os.path.join(current_dir, "..", "..", "color_phrases.json")
    with open(color_phrases_path, "r") as file:
        color_phrases = json.load(file)

    return color_phrases


def extract_locs_by_phrase(page, phrase):
    """
    ページから指定されたフレーズの位置情報を抽出する

    Args:
        page: PDFのページオブジェクト
        phrase: 抽出するフレーズ（例: "On the contrary"）

    Returns:
        list: フレーズの位置情報のリスト [(x0, y0, x1, y1), ...]
    """
    # フレーズを単語に分割
    words = phrase.split(" ")

    # ページから単語の位置情報を取得
    word_locs = page.get_text("words")

    # Format of a word_loc: (x0, y0, x1, y1, "word", block_no, line_no, word_no)
    # ref. https://pymupdf.readthedocs.io/en/latest/textpage.html#TextPage.extractWORDS
    word_idx = 4
    extracted_locs = []

    for start in range(len(word_locs) - len(words) + 1):
        # フレーズの単語が連続して一致するか確認
        match = True
        for i in range(len(words)):
            idx = start + i
            if word_locs[idx][word_idx] != words[i]:
                match = False
                break

        # すべての単語が一致した場合、位置情報を抽出
        if match:
            for fidx in range(start, start + len(words)):
                extracted_locs.append(word_locs[fidx][:word_idx])

    return extracted_locs


def highlight_in_color(page, locs, color: str):
    """
    指定された位置情報に指定された色でハイライトを追加する

    Args:
        page: PDFのページオブジェクト
        locs: ハイライトする位置情報のリスト [(x0, y0, x1, y1), ...]
        color: ハイライトの色（例: "red"）
    """
    highlight = page.add_highlight_annot(locs)
    rgb = getColor(color.upper())
    highlight.set_colors(stroke=rgb)
    highlight.update()


def process_pdf(input_pdf_path, output_pdf_path, color_phrases):
    """
    PDFを処理し、指定されたフレーズをハイライトする

    Args:
        input_pdf_path: 入力PDFのパス
        output_pdf_path: 出力PDFのパス
        color_phrases: 色とフレーズのマッピング
    """
    doc = fitz.open(input_pdf_path)

    for color, phrases in tqdm(color_phrases.items(), desc="Processing colors"):
        for phrase in tqdm(
            phrases, desc=f"Processing phrases for {color}", leave=False
        ):
            for page in doc:
                extracted_locs = extract_locs_by_phrase(page, phrase)
                if extracted_locs:  # 位置情報が抽出された場合のみハイライト
                    highlight_in_color(page, extracted_locs, color)

    # 出力ディレクトリが存在しない場合は作成
    output_dir = os.path.dirname(output_pdf_path)
    os.makedirs(output_dir, exist_ok=True)

    # 処理したPDFを保存
    doc.save(output_pdf_path)
    doc.close()


def main():
    """
    メイン関数
    コマンドライン引数を解析し、PDFの処理を実行する
    """
    parser = argparse.ArgumentParser(description="PDFのフレーズをハイライトするツール")
    parser.add_argument("input_pdf", help="入力PDFのパス")
    args = parser.parse_args()

    input_pdf_path = args.input_pdf
    input_pdf_filename = os.path.basename(input_pdf_path)

    # 色とフレーズのマッピングを取得
    color_phrases = get_color_phrases()

    # 出力PDFのパスを設定
    output_dir = os.path.join(data_dir, "output")
    output_path = os.path.join(output_dir, input_pdf_filename)

    # PDFを処理
    process_pdf(input_pdf_path, output_path, color_phrases)

    print(f"処理が完了しました。出力ファイル: {output_path}")


if __name__ == "__main__":
    main()
