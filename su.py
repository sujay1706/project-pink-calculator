import math

import customtkinter as ctk

BLACK_BG = "#000000"
DISPLAY_BG = "#111111"
DISPLAY_TEXT = "#ffe600"
TRAIL_TEXT = "#8a7a00"
BORDER_YELLOW = "#ffd400"

NUMBER_BG = "#2b2b2b"
NUMBER_HOVER = "#3a3a3a"

FUNCTION_BG = "#1c1c1c"
FUNCTION_HOVER = "#333300"

OPERATOR_BG = "#ffd400"
OPERATOR_HOVER = "#e6c200"

ctk.set_appearance_mode("dark")

DIGITS = set("0123456789")
OPERATORS = {"+", "−", "×", "÷", "="}
PY_OP = {"+": "+", "−": "-", "×": "*", "÷": "/"}
KEY_TO_OPERATOR = {"-": "−", "*": "×", "/": "÷", "+": "+"}


def dsin(x):
    return math.sin(math.radians(x))


def dcos(x):
    return math.cos(math.radians(x))


def dtan(x):
    return math.tan(math.radians(x))


EVAL_GLOBALS = {
    "__builtins__": {"int": int},
    "math": math,
    "dsin": dsin,
    "dcos": dcos,
    "dtan": dtan,
}


def format_number(value):
    if isinstance(value, complex):
        raise ValueError("complex result")
    if value == int(value) and abs(value) < 1e15:
        return str(int(value))
    text = f"{value:.10g}"
    return text


class Calculator(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Scientific Calculator")
        self.geometry("480x760")
        self.minsize(440, 700)
        self.resizable(True, True)
        self.configure(fg_color=BLACK_BG)

        self.display_expr = ""
        self.eval_expr = ""
        self.just_evaluated = False
        self.history_stack = []

        self.trail_label = ctk.CTkLabel(
            self,
            text="",
            font=("Consolas", 16),
            text_color=TRAIL_TEXT,
            anchor="e",
        )
        self.trail_label.pack(fill="x", padx=20, pady=(20, 0))

        self.display = ctk.CTkEntry(
            self,
            font=("Consolas", 36),
            justify="right",
            fg_color=DISPLAY_BG,
            text_color=DISPLAY_TEXT,
            border_color=BORDER_YELLOW,
            border_width=2,
            height=80,
        )
        self.display.pack(fill="x", padx=15, pady=(5, 20))

        buttons = [
            ["(", ")", "π", "e", "C"],
            ["x²", "√", "x^y", "1/x", "⌫"],
            ["sin", "cos", "tan", "log", "ln"],
            ["7", "8", "9", "÷", "n!"],
            ["4", "5", "6", "×", "%"],
            ["1", "2", "3", "−", "±"],
            ["0", ".", "EXP", "+", "="],
        ]

        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        for col in range(5):
            button_frame.grid_columnconfigure(col, weight=1)
        for row in range(len(buttons)):
            button_frame.grid_rowconfigure(row, weight=1)

        for row_index, row_values in enumerate(buttons):
            for col_index, value in enumerate(row_values):
                fg, hover, text_color = self._button_style(value)

                btn = ctk.CTkButton(
                    button_frame,
                    text=value,
                    font=("Segoe UI", 18, "bold"),
                    fg_color=fg,
                    hover_color=hover,
                    text_color=text_color,
                    corner_radius=12,
                    command=lambda v=value: self.on_button_click(v),
                )
                btn.grid(row=row_index, column=col_index, sticky="nsew", padx=4, pady=4)

        self.bind("<Key>", self.on_key_press)
        self.refresh()

    def _button_style(self, value):
        if value in DIGITS or value == ".":
            return NUMBER_BG, NUMBER_HOVER, DISPLAY_TEXT
        if value in OPERATORS:
            return OPERATOR_BG, OPERATOR_HOVER, "#000000"
        return FUNCTION_BG, FUNCTION_HOVER, DISPLAY_TEXT

    # ---- input dispatch ----

    def on_button_click(self, value):
        if value == "C":
            self.clear()
        elif value == "⌫":
            self.backspace()
        elif value == "=":
            self.equals()
        elif value == "±":
            self.apply_sign()
        elif value == "x²":
            self.apply_postfix(lambda o: f"({o})**2", lambda o: f"{o}²")
        elif value == "1/x":
            self.apply_postfix(lambda o: f"(1/({o}))", lambda o: f"(1/{o})")
        elif value == "n!":
            self.apply_postfix(lambda o: f"math.factorial(int({o}))", lambda o: f"{o}!")
        elif value == "%":
            self.apply_postfix(lambda o: f"({o}/100)", lambda o: f"{o}%")
        elif value == "√":
            self.insert_token("√(", "math.sqrt(")
        elif value == "sin":
            self.insert_token("sin(", "dsin(")
        elif value == "cos":
            self.insert_token("cos(", "dcos(")
        elif value == "tan":
            self.insert_token("tan(", "dtan(")
        elif value == "log":
            self.insert_token("log(", "math.log10(")
        elif value == "ln":
            self.insert_token("ln(", "math.log(")
        elif value == "π":
            self.insert_token("π", "math.pi")
        elif value == "e":
            self.insert_token("e", "math.e")
        elif value == "(":
            self.insert_token("(", "(")
        elif value == ")":
            self.insert_token(")", ")")
        elif value == "x^y":
            self.insert_operator("^", "**")
        elif value == "EXP":
            self.insert_token("×10^", "*10**")
        elif value in ("+", "−", "×", "÷"):
            self.insert_operator(value, PY_OP[value])
        elif value == ".":
            self.insert_decimal()
        else:
            self.insert_digit(value)

    def on_key_press(self, event):
        key = event.keysym
        if key == "Return":
            self.equals()
        elif key == "BackSpace":
            self.backspace()
        elif key == "Escape" or event.char.lower() == "c":
            self.clear()
        elif event.char == ".":
            self.insert_decimal()
        elif event.char == "(":
            self.insert_token("(", "(")
        elif event.char == ")":
            self.insert_token(")", ")")
        elif event.char == "^":
            self.insert_operator("^", "**")
        elif event.char in KEY_TO_OPERATOR:
            self.insert_operator(KEY_TO_OPERATOR[event.char], PY_OP[KEY_TO_OPERATOR[event.char]])
        elif event.char in "0123456789":
            self.insert_digit(event.char)

    # ---- expression building ----

    def _push_history(self):
        self.history_stack.append((self.display_expr, self.eval_expr, self.just_evaluated))

    def _prepare_for_input(self, is_operator):
        self._push_history()
        if self.display_expr == "Error" or (self.just_evaluated and not is_operator):
            self.display_expr = ""
            self.eval_expr = ""
        self.just_evaluated = False

    def insert_digit(self, digit):
        self._prepare_for_input(is_operator=False)
        self.display_expr += digit
        self.eval_expr += digit
        self.refresh()

    def insert_decimal(self):
        self._prepare_for_input(is_operator=False)
        self.display_expr += "."
        self.eval_expr += "."
        self.refresh()

    def insert_token(self, display_tok, eval_tok):
        self._prepare_for_input(is_operator=False)
        self.display_expr += display_tok
        self.eval_expr += eval_tok
        self.refresh()

    def insert_operator(self, display_op, py_op):
        self._prepare_for_input(is_operator=True)
        self.display_expr += f" {display_op} "
        self.eval_expr += f" {py_op} "
        self.refresh()

    def _find_trailing_operand(self, expr):
        if not expr:
            return 0
        i = len(expr)
        if expr[-1] == ")":
            depth = 0
            j = i - 1
            while j >= 0:
                if expr[j] == ")":
                    depth += 1
                elif expr[j] == "(":
                    depth -= 1
                    if depth == 0:
                        break
                j -= 1
            k = j
            while k > 0 and (expr[k - 1].isalnum() or expr[k - 1] in "._"):
                k -= 1
            return k
        j = i
        while j > 0 and (expr[j - 1].isalnum() or expr[j - 1] == "."):
            j -= 1
        if j > 0 and expr[j - 1] == "-":
            prev = expr[j - 2] if j - 2 >= 0 else None
            if prev is None or prev in "+-*/(,":
                j -= 1
        return j

    def apply_postfix(self, eval_wrap, display_wrap):
        if not self.eval_expr or self.display_expr == "Error":
            return
        self._push_history()
        if self.just_evaluated:
            start_e, start_d = 0, 0
        else:
            start_e = self._find_trailing_operand(self.eval_expr)
            start_d = self._find_trailing_operand(self.display_expr)
        operand_e = self.eval_expr[start_e:]
        operand_d = self.display_expr[start_d:]
        if not operand_e:
            return
        self.eval_expr = self.eval_expr[:start_e] + eval_wrap(operand_e)
        self.display_expr = self.display_expr[:start_d] + display_wrap(operand_d)
        self.just_evaluated = False
        self.refresh()

    def apply_sign(self):
        if not self.eval_expr or self.display_expr == "Error":
            return
        self._push_history()
        if self.just_evaluated:
            start_e, start_d = 0, 0
        else:
            start_e = self._find_trailing_operand(self.eval_expr)
            start_d = self._find_trailing_operand(self.display_expr)
        operand_e = self.eval_expr[start_e:]
        operand_d = self.display_expr[start_d:]
        if not operand_e:
            return
        if operand_e.startswith("-"):
            new_e, new_d = operand_e[1:], operand_d[1:]
        else:
            new_e, new_d = f"-({operand_e})", f"-{operand_d}"
        self.eval_expr = self.eval_expr[:start_e] + new_e
        self.display_expr = self.display_expr[:start_d] + new_d
        self.just_evaluated = False
        self.refresh()

    def equals(self):
        if not self.eval_expr or self.display_expr == "Error":
            return
        self._push_history()
        try:
            value = eval(self.eval_expr, EVAL_GLOBALS, {})
            text = format_number(value)
            self.display_expr = text
            self.eval_expr = text
        except Exception:
            self.display_expr = "Error"
            self.eval_expr = ""
        self.just_evaluated = True
        self.refresh()

    def backspace(self):
        if self.history_stack:
            self.display_expr, self.eval_expr, self.just_evaluated = self.history_stack.pop()
        else:
            self.display_expr = ""
            self.eval_expr = ""
            self.just_evaluated = False
        self.refresh()

    def clear(self):
        self._push_history()
        self.display_expr = ""
        self.eval_expr = ""
        self.just_evaluated = False
        self.refresh()

    def refresh(self):
        shown = self.display_expr if self.display_expr else "0"
        self.display.delete(0, "end")
        self.display.insert(0, shown)


if __name__ == "__main__":
    app = Calculator()
    app.mainloop()
