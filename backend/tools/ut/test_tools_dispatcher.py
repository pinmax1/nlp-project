from tools.tool_dispatcher import ToolsDispatcher


class DummyLogger:
    def debug(self, *a, **k): pass
    def error(self, *a, **k): pass
    def warning(self, *a, **k): pass
    def info(self, *a, **k): pass
    def exception(self, *a, **k): pass


class DummyLoggerConfig:
    def get_logger(self, name): return DummyLogger()


class DummyServerConfig:
    logger_config = DummyLoggerConfig()


def test_tools_dispatcher():
    dispatcher = ToolsDispatcher(DummyServerConfig())
    args = {
        "function": "example_tool",
        "arguments": {
            "string_param": "abc",
            "number_param": 1.23,
            "integer_param": 7,
            "boolean_param": True,
            "simple_array": ["a", "b"],
            "object_array": [{"id": 1, "data": "foo"}, {"id": 2, "data": "bar"}],
            "nested_object": {"level1": {"level2": "deep"}},
            "mixed_array": ["str", 5, {"bar": "baz"}],
        }
    }

    result = dispatcher.parse_and_call(args)
    assert "result" in result

    expected = """
Параметры функции:
- string_param: abc
- number_param: 1.23
- integer_param: 7
- boolean_param: True
- simple_array: ['a', 'b']
- object_array: [{'id': 1, 'data': 'foo'}, {'id': 2, 'data': 'bar'}]
- nested_object: {'level1': {'level2': 'deep'}}
- mixed_array: ['str', 5, {'bar': 'baz'}]
- optional_param: default_value
""".strip()

    assert result["result"] == expected
