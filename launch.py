import sys
from qt_command_palette import CommandPalette


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

    palette = CommandPalette()
    group_0 = palette.add_group("Example")
    group_1 = palette.add_group("Something new")

    for txt in ["foo", "bar", "baz"]:
        group_0.register(define(txt))

    for txt in ["hello world", "goobye world", "hello again"]:
        group_1.register(define(txt))

    palette.install(main, "Ctrl+Shift+P")
    main.show()
    sys.exit(app.exec_())
