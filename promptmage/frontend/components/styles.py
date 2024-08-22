from nicegui import Tailwind, ui


textbox_style = "w-full max-w-3xl"  #  border-2 border-gray-300 rounded-lg ring focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"


def label_with_icon(label: str, icon: str):
    row = ui.row().classes("gap-2 items-center")
    with row:
        ui.icon(icon)
        ui.label(label)
    return row
