from qt_command_palette import get_palette, get_storage

palette = get_palette(name=__name__)
storage = get_storage(name=__name__)


@storage.mark_getter("a")
def get_value():
    return 1


@storage.mark_getter
def param_a():
    return 2


@storage.mark_getter
def b(a):
    return a + 10


storage.mark_constant("const", 2)


def test_mark_getter():
    assert storage.call(lambda a: a) == 1


def test_mark_getter_with_default_name():
    assert storage.call(lambda param_a: param_a) == 2


def test_mark_getter_with_params():
    assert storage.call(lambda b: b) == 11


def test_mark_constant():
    assert storage.call(lambda const: const) == 2
