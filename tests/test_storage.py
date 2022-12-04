from qt_command_palette import get_palette, get_storage

palette = get_palette(name=__name__)
storage = get_storage(name=__name__)


@storage.mark_getter("a")
def get_value():
    return 1


storage.mark_constant("b", 2)


def test_mark_getter():
    assert storage.call(lambda a: a) == 1


def test_mark_constant():
    assert storage.call(lambda b: b) == 2
