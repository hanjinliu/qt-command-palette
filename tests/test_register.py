from qt_command_palette import get_palette

palette = get_palette(name=__name__)


def test_register_no_args():
    group = palette.add_group("test-1")

    @group.register
    def foo():
        pass

    assert palette.commands[-1].desc == "foo"


def test_register_desc():
    group = palette.add_group("test-2")

    @group.register(desc="test func")
    def foo():
        """some tooltip"""

    assert palette.commands[-1].desc == "test func"
    assert palette.commands[-1].tooltip == "some tooltip"


def test_register_tooltip():
    group = palette.add_group("test-3")

    @group.register(tooltip="tooltip")
    def foo():
        pass


def test_register_args():
    group = palette.add_group("test-4")

    @group.register("test func", "tooltip")
    def foo():
        pass


def test_register_with_app_name():
    from qt_command_palette import get_palette

    palette = get_palette("test")

    from . import _file_0, _file_1  # noqa

    assert len(palette.commands) == 2
