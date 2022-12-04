from qt_command_palette import CommandPalette

palette = CommandPalette()


def test_register_no_args():
    group = palette.add_group("test")

    @group.register
    def foo():
        pass


def test_register_desc():
    group = palette.add_group("test")

    @group.register(desc="test func")
    def foo():
        pass


def test_register_tooltip():
    group = palette.add_group("test")

    @group.register(tooltip="tooltip")
    def foo():
        pass


def test_register_args():
    group = palette.add_group("test")

    @group.register("test func", "tooltip")
    def foo():
        pass


def test_register_with_app_name():
    from qt_command_palette import get_palette

    palette = get_palette("test")

    assert len(palette.commands) == 2
