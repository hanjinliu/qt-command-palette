import sys
from qt_command_palette import get_palette, get_storage


def define(text: str):
    def fn():
        print("called:", text)

    fn.__doc__ = f"Prints {text!r}"
    fn.__name__ = text
    return fn


if __name__ == "__main__":
    from qtpy.QtWidgets import QApplication, QWidget

    app = QApplication([])
    main = QWidget()
    main.setMinimumSize(400, 300)

    palette = get_palette(name=__name__)
    storage = get_storage(name=__name__)

    @storage.mark_getter("widget")
    def get_widget():
        return main

    group_0 = palette.add_group("Example")
    group_1 = palette.add_group("Something new")

    for txt in ["foo", "bar", "baz"]:
        group_0.register(define(txt))

    for txt in ["hello world", "goobye world", "hello again"]:
        group_1.register(define(txt))

    @group_1.register("Print widget")
    def print_widget(widget: QWidget):
        print(widget)

    palette.install(main, "Ctrl+Shift+P")
    main.show()
    sys.exit(app.exec_())
