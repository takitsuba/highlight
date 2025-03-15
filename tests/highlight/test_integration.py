"""
統合テスト - 実際のPDFファイルを使用したテスト
"""

import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

import fitz

from src.highlight.main import process_pdf


class TestIntegration(unittest.TestCase):
    """統合テスト"""

    def setUp(self):
        """テスト前の準備"""
        # 一時ディレクトリを作成
        self.test_dir = tempfile.mkdtemp()

        # テスト用のcolor_phrasesを定義
        self.color_phrases = {"yellow": ["test", "example"], "red": ["integration"]}

        # テスト用のPDFを作成
        self.create_test_pdf()

    def tearDown(self):
        """テスト後のクリーンアップ"""
        # 一時ディレクトリを削除
        shutil.rmtree(self.test_dir)

    def create_test_pdf(self):
        """テスト用のPDFを作成する"""
        self.input_pdf_path = os.path.join(self.test_dir, "test_input.pdf")
        self.output_pdf_path = os.path.join(self.test_dir, "test_output.pdf")

        # 新しいPDFドキュメントを作成
        doc = fitz.open()
        page = doc.new_page()

        # テキストを追加
        text = "This is a test document for integration testing. This example should highlight some words."
        text += " This is an integration test."
        page.insert_text((50, 50), text)

        # PDFを保存
        doc.save(self.input_pdf_path)
        doc.close()

    def test_process_pdf_integration(self):
        """実際のPDFを処理する統合テスト"""
        # PDFを処理
        process_pdf(self.input_pdf_path, self.output_pdf_path, self.color_phrases)

        # 出力PDFが存在することを確認
        self.assertTrue(os.path.exists(self.output_pdf_path))

        # 出力PDFを開いてハイライトを確認
        doc = fitz.open(self.output_pdf_path)
        page = doc[0]

        # ハイライト（注釈）を取得
        annotations = list(page.annots())

        # ハイライトの数を確認（"test", "example", "integration"の3つ）
        self.assertGreaterEqual(len(annotations), 3)

        # ハイライトの色を確認
        yellow_count = 0
        red_count = 0

        for annot in annotations:
            if annot.type[0] == 8:  # ハイライト注釈
                colors = annot.colors["stroke"]
                if colors == (1, 1, 0):  # 黄色 (RGB: 1,1,0)
                    yellow_count += 1
                elif colors == (1, 0, 0):  # 赤色 (RGB: 1,0,0)
                    red_count += 1

        # 黄色のハイライトが少なくとも2つあることを確認（"test"と"example"）
        self.assertGreaterEqual(yellow_count, 2)

        # 赤色のハイライトが少なくとも1つあることを確認（"integration"）
        self.assertGreaterEqual(red_count, 1)

        doc.close()


if __name__ == "__main__":
    unittest.main()
