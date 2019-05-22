import sys

import colorama

from picli import logger


def test_info(capsys):
    log = logger.get_logger(__name__)
    log.info("foo")
    stdout, _ = capsys.readouterr()

    print(
        "--> {}{}{}".format(
            colorama.Fore.CYAN, "foo".rstrip(), colorama.Style.RESET_ALL
        )
    )
    x, _ = capsys.readouterr()

    assert x == stdout


def test_out(capsys):
    log = logger.get_logger(__name__)
    log.out("foo")

    stdout, _ = capsys.readouterr()

    assert "    foo\n" == stdout


def test_warn(capsys):
    log = logger.get_logger(__name__)
    log.warning("foo")

    stdout, _ = capsys.readouterr()

    print(
        "{}{}{}".format(colorama.Fore.YELLOW, "foo".rstrip(), colorama.Style.RESET_ALL)
    )
    x, _ = capsys.readouterr()

    assert x == stdout


def test_error(capsys):
    log = logger.get_logger(__name__)
    log.error("foo")

    _, stderr = capsys.readouterr()

    print(
        "{}{}{}".format(colorama.Fore.RED, "foo".rstrip(), colorama.Style.RESET_ALL),
        file=sys.stderr,
    )
    _, x = capsys.readouterr()

    assert x in stderr


def test_critical(capsys):
    log = logger.get_logger(__name__)
    log.critical("foo")

    _, stderr = capsys.readouterr()

    print(
        "{}ERROR: {}{}".format(
            colorama.Fore.RED, "foo".rstrip(), colorama.Style.RESET_ALL
        ),
        file=sys.stderr,
    )
    _, x = capsys.readouterr()

    assert x in stderr


def test_success(capsys):
    log = logger.get_logger(__name__)
    log.success("foo")

    stdout, _ = capsys.readouterr()

    print(
        "{}{}{}".format(colorama.Fore.GREEN, "foo".rstrip(), colorama.Style.RESET_ALL)
    )
    x, _ = capsys.readouterr()

    assert x == stdout


def test_red_text():
    x = "{}{}{}".format(colorama.Fore.RED, "foo", colorama.Style.RESET_ALL)

    assert x == logger.red_text("foo")


def test_yellow_text():
    x = "{}{}{}".format(colorama.Fore.YELLOW, "foo", colorama.Style.RESET_ALL)

    assert x == logger.yellow_text("foo")


def test_green_text():
    x = "{}{}{}".format(colorama.Fore.GREEN, "foo", colorama.Style.RESET_ALL)

    assert x == logger.green_text("foo")


def test_cyan_text():
    x = "{}{}{}".format(colorama.Fore.CYAN, "foo", colorama.Style.RESET_ALL)

    assert x == logger.cyan_text("foo")
