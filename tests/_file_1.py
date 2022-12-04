from qt_command_palette import get_palette

palette = get_palette("test")


@palette.register("AAA")
def func_1():
    print("func_1")
