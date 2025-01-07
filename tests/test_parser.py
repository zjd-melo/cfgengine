import os
import unittest
from unittest.mock import MagicMock, mock_open, patch

from cfgengine import (
    DotDict,
    INIParser,
    JSONParser,
    ParserRegistry,
    returns_native_non_string,
)
from cfgengine.parser import FunctionCallExtractor, Parser


class TestDotDict(unittest.TestCase):
    def test_attribute_access(self):
        d = DotDict({"key": "value", "nested": {"subkey": "subvalue"}})
        self.assertEqual(d.key, "value")
        self.assertEqual(d.nested.subkey, "subvalue")

    def test_set_attribute(self):
        d = DotDict({})
        d.new_key = "new_value"
        self.assertEqual(d.new_key, "new_value")

    def test_delete_attribute(self):
        d = DotDict({"key": "value"})
        del d.key
        self.assertNotIn("key", d)

    def test_missing_attribute(self):
        d = DotDict({})
        with self.assertRaises(AttributeError):
            _ = d.nonexistent_key


class TestParserRegistry(unittest.TestCase):
    def test_register_and_get_parser(self):
        class DummyParser:
            pass

        ParserRegistry.register_parser("dummy", DummyParser)
        retrieved = ParserRegistry.get_parser_class("dummy")
        self.assertEqual(retrieved, DummyParser)

    def test_get_unregistered_parser(self):
        with self.assertRaises(ValueError):
            ParserRegistry.get_parser_class("unknown")


class TestJSONParser(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data='{"key": "value"}')
    def test_load_valid_json(self, mock_file):
        parser = JSONParser("dummy_path.json")
        config = parser.load()
        self.assertEqual(config, {"key": "value"})

    @patch("builtins.open", new_callable=mock_open, read_data="invalid json")
    def test_load_invalid_json(self, mock_file):
        parser = JSONParser("dummy_path.json")
        with self.assertRaises(ValueError):
            parser.load()

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_load_file_not_found(self, mock_file):
        parser = JSONParser("nonexistent.json")
        with self.assertRaises(FileNotFoundError):
            parser.load()


class TestINIParser(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data="[section]\nkey=value")
    def test_load_valid_ini(self, mock_file):
        parser = INIParser("dummy_path.ini")
        config = parser.load()
        self.assertEqual(config, {"section": {"key": "value"}})

    @patch("builtins.open", new_callable=mock_open, read_data="invalid ini")
    def test_load_invalid_ini(self, mock_file):
        parser = INIParser("dummy_path.ini")
        with self.assertRaises(ValueError):
            parser.load()


class TestFunctionCallExtractor(unittest.TestCase):
    def test_extract_function_calls(self):
        from jinja2.nativetypes import NativeEnvironment

        env = NativeEnvironment()
        env.globals = {"my_func": lambda: None}
        extractor = FunctionCallExtractor(env)

        template_str = "{{ my_func() }}"
        calls = extractor.extract(template_str)
        self.assertIn("my_func", calls)


class TestParser(unittest.TestCase):
    def setUp(self):
        env = MagicMock()
        env.from_string.return_value.render.return_value = "rendered_value"
        self.parser = Parser(env)

    def test_parse_string(self):
        result = self.parser.parse_string("{{ value }}", "key")
        self.assertEqual(result, "rendered_value")

    def test_parse_value_recursive(self):
        config = {
            "key1": "{{ value }}",
            "key2": ["{{ item }}"],
            "key3": {"subkey": "{{ nested_value }}"},
        }
        result = self.parser.parse_config(config)
        self.assertEqual(result["key1"], "rendered_value")


class TestGlobalFunctions(unittest.TestCase):
    def test_returns_native(self):
        @returns_native_non_string
        def dummy_func():
            pass

        self.assertTrue(getattr(dummy_func, "returns_native", False))


if __name__ == "__main__":
    unittest.main()
