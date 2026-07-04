import customtkinter as ctk

PINK_BG = "#ffe4ef"
PINK_DISPLAY = "#ffb6d5"
PINK_BUTTON = "#ff8fb3"
PINK_BUTTON_HOVER = "#ff6699"
PINK_OPERATOR = "#e0559c"
PINK_OPERATOR_HOVER = "#c93f85"
PINK_TEXT = "#4a002a"
PINK_TRAIL_TEXT = "#8a3a5c"

ctk.set_appearance_mode("light")

OPERATORS = ("+", "−", "×", "÷")  # +, minus sign, multiply sign, divide sign
KEY_TO_OPERATOR = {"-": "−", "*": "×", "/": "÷", "+": "+"}


def format_number(value):
    if value == int(value):
        return str(int(value))
    text = f"{value:.10f}".rstrip("0").rstrip(".")
    return text


class Calculator(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Pink Calculator")
        self.geometry("420x640")
        self.minsize(360, 540)
        self.resizable(True, True)
        self.configure(fg_color=PINK_BG)

        self.current = "0"
        self.stored = None
        self.operator = None
        self.reset_current = False
        self.trail = ""

        self.trail_label = ctk.CTkLabel(
            self,
            text="",
            font=("Segoe UI", 16),
            text_color=PINK_TRAIL_TEXT,
            anchor="e",
        )
        self.trail_label.pack(fill="x", padx=20, pady=(20, 0))

        self.display = ctk.CTkEntry(
            self,
            font=("Segoe UI", 40),
            justify="right",
            fg_color=PINK_DISPLAY,
            text_color=PINK_TEXT,
            border_color=PINK_OPERATOR,
            border_width=2,
            height=80,
        )
        self.display.pack(fill="x", padx=15, pady=(5, 20))

        buttons = [
            ["C", "⌫", "%", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "−"],
            ["1", "2", "3", "+"],
            ["0", ".", "="],
        ]

        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        for col in range(4):
            button_frame.grid_columnconfigure(col, weight=1)
        for row in range(len(buttons)):
            button_frame.grid_rowconfigure(row, weight=1)

        for row_index, row_values in enumerate(buttons):
            col_index = 0
            for value in row_values:
                is_operator = value in OPERATORS or value in ("C", "⌫", "%", "=")
                columnspan = 2 if value == "0" else 1

                btn = ctk.CTkButton(
                    button_frame,
                    text=value,
                    font=("Segoe UI", 20, "bold"),
                    fg_color=PINK_OPERATOR if is_operator else PINK_BUTTON,
                    hover_color=PINK_OPERATOR_HOVER if is_operator else PINK_BUTTON_HOVER,
                    text_color="white",
                    corner_radius=15,
                    command=lambda v=value: self.on_button_click(v),
                )
                btn.grid(
                    row=row_index,
                    column=col_index,
                    columnspan=columnspan,
                    sticky="nsew",
                    padx=5,
                    pady=5,
                )
                col_index += columnspan

        self.bind("<Key>", self.on_key_press)
        self.refresh()

    def on_button_click(self, value):
        if value == "C":
            self.clear()
        elif value == "⌫":
            self.backspace()
        elif value == "%":
            self.percent()
        elif value == ".":
            self.input_decimal()
        elif value in OPERATORS:
            self.input_operator(value)
        elif value == "=":
            self.equals()
        else:
            self.input_digit(value)

    def on_key_press(self, event):
        key = event.keysym
        if key == "Return":
            self.equals()
        elif key == "BackSpace":
            self.backspace()
        elif key == "Escape" or event.char.lower() == "c":
            self.clear()
        elif event.char == ".":
            self.input_decimal()
        elif event.char == "%":
            self.percent()
        elif event.char in KEY_TO_OPERATOR:
            self.input_operator(KEY_TO_OPERATOR[event.char])
        elif event.char in "0123456789":
            self.input_digit(event.char)

    def input_digit(self, digit):
        if self.current == "Error":
            self.clear()
        if self.reset_current or self.current == "0":
            self.current = digit
            self.reset_current = False
        else:
            self.current += digit
        self.refresh()

    def input_decimal(self):
        if self.current == "Error":
            self.clear()
        if self.reset_current:
            self.current = "0."
            self.reset_current = False
        elif "." not in self.current:
            self.current += "."
        self.refresh()

    def input_operator(self, op):
        if self.current == "Error":
            return
        if self.operator is not None and not self.reset_current:
            self._compute()
        else:
            self.stored = float(self.current)
        self.operator = op
        self.trail = f"{format_number(self.stored)} {op}"
        self.reset_current = True
        self.refresh()

    def equals(self):
        if self.operator is None or self.current == "Error":
            return
        self.trail = f"{format_number(self.stored)} {self.operator} {self.current} ="
        self._compute()
        self.operator = None
        self.reset_current = True
        self.refresh()

    def percent(self):
        if self.current == "Error":
            return
        self.current = format_number(float(self.current) / 100)
        self.refresh()

    def backspace(self):
        if self.current == "Error" or self.reset_current:
            self.clear()
            return
        self.current = self.current[:-1]
        if self.current in ("", "-"):
            self.current = "0"
        self.refresh()

    def clear(self):
        self.current = "0"
        self.stored = None
        self.operator = None
        self.reset_current = False
        self.trail = ""
        self.refresh()

    def _compute(self):
        a = self.stored
        b = float(self.current)
        try:
            if self.operator == "+":
                result = a + b
            elif self.operator == "−":
                result = a - b
            elif self.operator == "×":
                result = a * b
            elif self.operator == "÷":
                result = a / b
            else:
                return
        except ZeroDivisionError:
            self.current = "Error"
            self.stored = None
            self.operator = None
            self.trail = ""
            return
        self.stored = result
        self.current = format_number(result)

    def refresh(self):
        self.trail_label.configure(text=self.trail)
        self.display.delete(0, "end")
        self.display.insert(0, self.current)


if __name__ == "__main__":
    app = Calculator()
    app.mainloop()
