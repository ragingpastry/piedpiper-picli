import pytest

from picli.command import style

def test_execute(mocker, patched_flake8, patched_style_pipe_config, config_instance):
    styler = style.Style(config_instance)
    styler.execute()

    patched_flake8.assert_called_once_with()
