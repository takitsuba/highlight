"""
main.pyのテスト
"""

import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock, mock_open, patch

from src.highlight.main import (
    extract_locs_by_phrase,
    get_color_phrases,
    highlight_in_color,
    main,
    process_pdf,
)


class TestExtractLocsByPhrase(unittest.TestCase):
    """extract_locs_by_phraseのテスト"""

    def test_single_word_extraction(self):
        """単一単語の抽出テスト"""
        # モックページの作成
        mock_page = MagicMock()
        mock_page.get_text.return_value = [
            (0, 0, 10, 10, "First", 0, 0, 0),
            (15, 0, 25, 10, "of", 0, 0, 1),
            (30, 0, 40, 10, "all", 0, 0, 2),
            (0, 15, 10, 25, "First", 0, 1, 0),
        ]

        # テスト
        locs = extract_locs_by_phrase(mock_page, "First")

        # 検証 - "First"という単語が2つあるので、2つの位置情報が返されるべき
        self.assertEqual(len(locs), 2)
        self.assertEqual(locs[0], (0, 0, 10, 10))
        self.assertEqual(locs[1], (0, 15, 10, 25))

    def test_single_column_extraction(self):
        """単一列のPDFからフレーズを抽出するテスト"""
        # モックページの作成
        mock_page = MagicMock()
        mock_page.get_text.return_value = [
            (0, 0, 10, 10, "First", 0, 0, 0),
            (15, 0, 25, 10, "of", 0, 0, 1),
            (30, 0, 40, 10, "all", 0, 0, 2),
            (0, 15, 10, 25, "Second", 0, 1, 0),
            (15, 15, 25, 25, "line", 0, 1, 1),
        ]

        # テスト
        locs = extract_locs_by_phrase(mock_page, "First of all")

        # 検証
        self.assertEqual(len(locs), 3)
        self.assertEqual(locs[0], (0, 0, 10, 10))
        self.assertEqual(locs[1], (15, 0, 25, 10))
        self.assertEqual(locs[2], (30, 0, 40, 10))

    def test_double_column_extraction(self):
        """二段列のPDFからフレーズを抽出するテスト"""
        # モックページの作成 - 左右二段列を模擬
        mock_page = MagicMock()
        # 左列の単語
        left_col_words = [
            (0, 0, 10, 10, "First", 0, 0, 0),
            (15, 0, 25, 10, "word", 0, 0, 1),
            (0, 15, 10, 25, "Second", 0, 1, 0),
            (15, 15, 25, 25, "line", 0, 1, 1),
        ]
        # 右列の単語
        right_col_words = [
            (100, 0, 110, 10, "First", 1, 0, 0),
            (115, 0, 125, 10, "column", 1, 0, 1),
            (100, 15, 110, 25, "Second", 1, 1, 0),
            (115, 15, 125, 25, "row", 1, 1, 1),
        ]
        # 全ての単語を結合
        all_words = left_col_words + right_col_words
        mock_page.get_text.return_value = all_words

        # テスト - 左列のフレーズ
        locs = extract_locs_by_phrase(mock_page, "First word")

        # 検証 - 左列のみから抽出されるべき
        self.assertEqual(len(locs), 2)
        self.assertEqual(locs[0], (0, 0, 10, 10))
        self.assertEqual(locs[1], (15, 0, 25, 10))

        # テスト - 右列のフレーズ
        locs = extract_locs_by_phrase(mock_page, "First column")

        # 検証 - 右列のみから抽出されるべき
        self.assertEqual(len(locs), 2)
        self.assertEqual(locs[0], (100, 0, 110, 10))
        self.assertEqual(locs[1], (115, 0, 125, 10))

    def test_phrase_not_found(self):
        """フレーズが見つからない場合のテスト"""
        # モックページの作成
        mock_page = MagicMock()
        mock_page.get_text.return_value = [
            (0, 0, 10, 10, "First", 0, 0, 0),
            (15, 0, 25, 10, "of", 0, 0, 1),
            (30, 0, 40, 10, "all", 0, 0, 2),
        ]

        # テスト
        locs = extract_locs_by_phrase(mock_page, "Not found")

        # 検証 - 空のリストが返されるべき
        self.assertEqual(len(locs), 0)


class TestHighlightInColor(unittest.TestCase):
    """highlight_in_colorのテスト"""

    @patch("src.highlight.main.getColor")
    def test_highlight_in_color(self, mock_get_color):
        """ハイライト処理のテスト"""
        # モックの設定
        mock_page = MagicMock()
        mock_highlight = MagicMock()
        mock_page.add_highlight_annot.return_value = mock_highlight
        mock_get_color.return_value = (1, 0, 0)  # 赤色を返すように設定

        # テスト
        locs = [(0, 0, 10, 10), (15, 0, 25, 10)]
        highlight_in_color(mock_page, locs, "red")

        # 検証
        mock_page.add_highlight_annot.assert_called_once_with(locs)
        mock_get_color.assert_called_once_with("RED")
        mock_highlight.set_colors.assert_called_once_with(stroke=(1, 0, 0))
        mock_highlight.update.assert_called_once()


class TestGetColorPhrases(unittest.TestCase):
    """get_color_phrasesのテスト"""

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='{"red": ["phrase1", "phrase2"], "blue": ["phrase3"]}',
    )
    @patch("os.path.join")
    def test_get_color_phrases(self, mock_join, mock_file):
        """色とフレーズのマッピングを取得するテスト"""
        # モックの設定
        mock_join.return_value = "/path/to/color_phrases.json"

        # テスト
        result = get_color_phrases()

        # 検証
        expected = {"red": ["phrase1", "phrase2"], "blue": ["phrase3"]}
        self.assertEqual(result, expected)
        mock_join.assert_called()
        mock_file.assert_called_once_with("/path/to/color_phrases.json", "r")


class TestProcessPDF(unittest.TestCase):
    """process_pdfのテスト"""

    @patch("src.highlight.main.fitz.open")
    @patch("src.highlight.main.extract_locs_by_phrase")
    @patch("src.highlight.main.highlight_in_color")
    @patch("os.makedirs")
    def test_process_pdf(self, mock_makedirs, mock_highlight, mock_extract, mock_open):
        """PDFを処理するテスト"""
        # モックの設定
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_doc.__iter__.return_value = [mock_page]
        mock_open.return_value = mock_doc
        mock_extract.return_value = [(0, 0, 10, 10)]
        color_phrases = {"red": ["phrase1", "phrase2"], "blue": ["phrase3"]}

        # テスト
        process_pdf("input.pdf", "output.pdf", color_phrases)

        # 検証
        mock_open.assert_called_once_with("input.pdf")
        self.assertEqual(
            mock_extract.call_count, 3
        )  # 3つのフレーズに対して呼び出されるべき
        self.assertEqual(
            mock_highlight.call_count, 3
        )  # 3つのフレーズに対して呼び出されるべき
        mock_makedirs.assert_called_once_with(
            os.path.dirname("output.pdf"), exist_ok=True
        )
        mock_doc.save.assert_called_once_with("output.pdf")
        mock_doc.close.assert_called_once()

    @patch("src.highlight.main.fitz.open")
    @patch("src.highlight.main.extract_locs_by_phrase")
    @patch("src.highlight.main.highlight_in_color")
    @patch("os.makedirs")
    def test_process_pdf_no_phrases_found(
        self, mock_makedirs, mock_highlight, mock_extract, mock_open
    ):
        """フレーズが見つからない場合のテスト"""
        # モックの設定
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_doc.__iter__.return_value = [mock_page]
        mock_open.return_value = mock_doc
        mock_extract.return_value = []  # フレーズが見つからない
        color_phrases = {"red": ["phrase1"]}

        # テスト
        process_pdf("input.pdf", "output.pdf", color_phrases)

        # 検証
        mock_open.assert_called_once_with("input.pdf")
        mock_extract.assert_called_once()
        mock_highlight.assert_not_called()  # フレーズが見つからないのでハイライトは呼び出されない
        mock_makedirs.assert_called_once_with(
            os.path.dirname("output.pdf"), exist_ok=True
        )
        mock_doc.save.assert_called_once_with("output.pdf")
        mock_doc.close.assert_called_once()


class TestMain(unittest.TestCase):
    """mainのテスト"""

    @patch("src.highlight.main.argparse.ArgumentParser")
    @patch("src.highlight.main.get_color_phrases")
    @patch("src.highlight.main.process_pdf")
    @patch("os.path.basename")
    @patch("os.path.join")
    def test_main(
        self, mock_join, mock_basename, mock_process, mock_get_color, mock_argparse
    ):
        """メイン関数のテスト"""
        # モックの設定
        mock_args = MagicMock()
        mock_args.input_pdf = "/path/to/input.pdf"
        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = mock_args
        mock_argparse.return_value = mock_parser
        mock_basename.return_value = "input.pdf"
        mock_join.side_effect = lambda *args: "/".join(args)
        mock_get_color.return_value = {"red": ["phrase1"]}

        # テスト
        main()

        # 検証
        mock_argparse.assert_called_once()
        mock_parser.add_argument.assert_called_once_with(
            "input_pdf", help="入力PDFのパス"
        )
        mock_parser.parse_args.assert_called_once()
        mock_basename.assert_called_once_with("/path/to/input.pdf")
        mock_get_color.assert_called_once()
        mock_process.assert_called_once()


if __name__ == "__main__":
    unittest.main()
