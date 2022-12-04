import sys
from qt_command_palette import CommandPalette


def define(text: str):
    def fn():
        print("called:", text)

    fn.__doc__ = f"Prints {text!r}"
    fn.__name__ = text
    return fn


if __name__ == "__main__":
    from qtpy.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton

    app = QApplication([])
    main = QWidget()
    main.setLayout(QVBoxLayout())

    for i in range(10):
        label = QLabel(f"label {i}")
        main.layout().addWidget(label)

    button = QPushButton("show")
    main.layout().addWidget(button)
    button.clicked.connect(lambda: palette.get_widget(main).show())

    palette = CommandPalette()
    group_0 = palette.add_group("test")
    group_1 = palette.add_group("some other")

    for txt in ["foo", "bar", "baz"]:
        group_0.register(define(txt))

    for txt in ["hello", "world"]:
        group_1.register(define(txt))

    palette.install(main, "Ctrl+Shift+P")
    main.show()
    sys.exit(app.exec_())
