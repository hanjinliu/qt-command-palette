from qt_command_palette import QCommandPalette, Command

if __name__ == "__main__":
    from qtpy.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
    import sys
    app = QApplication([])
    main = QWidget()
    main.setLayout(QVBoxLayout())
    button = QPushButton("show palette")
    main.layout().addWidget(button)
    button.clicked.connect(lambda: palette.show())
    palette = QCommandPalette()
    for txt in ["foo", "bar", "baz"]:
        palette.add_command(Command(lambda t=txt: print(t), "Test", txt))
    palette.install_to(main)
    main.show()
    sys.exit(app.exec_())
