"""
main.pyのテスト
"""

import unittest
from unittest.mock import MagicMock, patch

from src.highlight.main import (
    extract_locs_by_phrase,
    highlight_in_color,
    is_same_line_and_column,
)


class TestIsSameLineAndColumn(unittest.TestCase):
    """is_same_line_and_column関数のテスト"""

    def test_same_line_and_column(self):
        """同じ行と列にある単語のテスト"""
        word1 = (0, 0, 10, 10, "First", 1, 2, 0)
        word2 = (15, 0, 25, 10, "Second", 1, 2, 1)
        self.assertTrue(is_same_line_and_column(word1, word2))

    def test_different_block(self):
        """異なるブロックにある単語のテスト"""
        word1 = (0, 0, 10, 10, "First", 1, 2, 0)
        word2 = (100, 0, 110, 10, "Second", 2, 2, 0)
        self.assertFalse(is_same_line_and_column(word1, word2))

    def test_different_line(self):
        """異なる行にある単語のテスト"""
        word1 = (0, 0, 10, 10, "First", 1, 2, 0)
        word2 = (0, 15, 10, 25, "Second", 1, 3, 0)
        self.assertFalse(is_same_line_and_column(word1, word2))


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

    def test_cross_column_no_extraction(self):
        """列をまたがるフレーズは抽出されないことを確認するテスト"""
        # モックページの作成 - 左右二段列を模擬
        mock_page = MagicMock()
        # 左列の単語
        left_col_words = [
            (0, 0, 10, 10, "First", 0, 0, 0),
            (15, 0, 25, 10, "word", 0, 0, 1),
        ]
        # 右列の単語
        right_col_words = [
            (100, 0, 110, 10, "column", 1, 0, 0),
        ]
        # 全ての単語を結合
        all_words = left_col_words + right_col_words
        mock_page.get_text.return_value = all_words

        # テスト - 列をまたがるフレーズ
        locs = extract_locs_by_phrase(mock_page, "word column")

        # 検証 - 列をまたがるので抽出されないはず
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


if __name__ == "__main__":
    unittest.main()
