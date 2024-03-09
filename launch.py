import sys
from qt_command_palette import get_palette, get_storage


def define(text: str):
    def fn():
        print("called:", text)

    fn.__doc__ = f"Prints {text!r}"
    fn.__name__ = text
    return fn


if __name__ == "__main__":
    from qtpy import QtWidgets as QtW

    app = QtW.QApplication([])
    main = QtW.QWidget()
    main.setMinimumSize(400, 300)

    main.setLayout(QtW.QVBoxLayout())
    _checkbox = QtW.QCheckBox("Check")
    main.layout().addWidget(_checkbox)

    palette = get_palette(name=__name__, alignment="screen")
    storage = get_storage(name=__name__)

    @storage.mark_getter("widget")
    def get_widget():
        return main

    group_0 = palette.add_group("Example")
    group_1 = palette.add_group("Something new")

    for txt in ["foo", "bar", "baz"]:
        group_0.register(define(txt))

    group_0.register(define("only if checked"), when=_checkbox.isChecked)

    for txt in ["hello world", "goobye world", "hello again"]:
        group_1.register(define(txt))

    group_1.register(define("only if checked"), when=_checkbox.isChecked)

    @group_1.register("Print widget")
    def print_widget(widget: QtW.QWidget):
        print(widget)

    @group_0.register("update max rows")
    def update_max_rows():
        palette.set_max_rows(5)

    palette.install(main, "Ctrl+Shift+P")
    main.show()
    sys.exit(app.exec_())
