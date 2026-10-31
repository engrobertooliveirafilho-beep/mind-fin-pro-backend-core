"""Isolated fail-closed regression for admin activation guard (no DB/network)."""
import ast
import os
import unittest
from pathlib import Path
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[2] / "app" / "admin" / "public_runtime.py"

class FakeHTTPException(Exception):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail

class AdminTokenGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
        guard = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "guard")
        namespace = {"os": os, "HTTPException": FakeHTTPException}
        exec(compile(ast.Module(body=[guard], type_ignores=[]), str(SOURCE), "exec"), namespace)
        cls.guard = staticmethod(namespace["guard"])

    def test_unset_secret_and_none_token_rejected(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(FakeHTTPException) as caught:
                self.guard(None)
            self.assertEqual(caught.exception.status_code, 403)

    def test_unset_secret_and_supplied_token_rejected(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(FakeHTTPException): self.guard("test-token")

    def test_empty_secret_rejected(self):
        with patch.dict(os.environ, {"ADMIN_ACTIVATION_TOKEN": ""}):
            with self.assertRaises(FakeHTTPException): self.guard("")

    def test_empty_secret_with_nonempty_token_rejected(self):
        with patch.dict(os.environ, {"ADMIN_ACTIVATION_TOKEN": ""}):
            with self.assertRaises(FakeHTTPException): self.guard("test-token")

    def test_none_token_rejected(self):
        with patch.dict(os.environ, {"ADMIN_ACTIVATION_TOKEN": "test-token"}):
            with self.assertRaises(FakeHTTPException): self.guard(None)

    def test_empty_token_rejected(self):
        with patch.dict(os.environ, {"ADMIN_ACTIVATION_TOKEN": "test-token"}):
            with self.assertRaises(FakeHTTPException): self.guard("")

    def test_wrong_token_rejected(self):
        with patch.dict(os.environ, {"ADMIN_ACTIVATION_TOKEN": "test-token"}):
            with self.assertRaises(FakeHTTPException): self.guard("wrong")

    def test_matching_token_accepted(self):
        with patch.dict(os.environ, {"ADMIN_ACTIVATION_TOKEN": "test-token"}):
            self.assertIsNone(self.guard("test-token"))

    def test_non_string_token_rejected(self):
        with patch.dict(os.environ, {"ADMIN_ACTIVATION_TOKEN": "test-token"}):
            with self.assertRaises(FakeHTTPException): self.guard(123)

if __name__ == "__main__": unittest.main()
