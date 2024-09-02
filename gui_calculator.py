import tkinter as tk
from tkinter import messagebox

class Calculator:
    def __init__(self, master):
        self.master = master
        master.title('Calculator')
        self.entry = tk.Entry(master, width=16, font=('Arial', 24), borderwidth=5)
        self.entry.grid(row=0, column=0, columnspan=4)
        self.create_buttons()

    def create_buttons(self):
        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', 'C', '=', '+'
        ]
        row_val = 1
        col_val = 0
        for button in buttons:
            self.create_button(button, row_val, col_val)
            col_val += 1
            if col_val > 3:
                col_val = 0
                row_val += 1

    def create_button(self, value, r, c):
        button = tk.Button(self.master, text=value, width=10, height=3, font=('Arial', 18),
                           command=lambda: self.on_button_click(value))
        button.grid(row=r, column=c, sticky='nswe')

    def on_button_click(self, value):
        if value == 'C':
            self.entry.delete(0, tk.END)
        elif value == '=':
            try:
                expression = self.entry.get()
                result = eval(expression)
                self.entry.delete(0, tk.END)
                self.entry.insert(0, result)
            except Exception as e:
                messagebox.showerror('Error', 'Invalid Input')
        else:
            self.entry.insert(tk.END, value)

if __name__ == '__main__':
    root = tk.Tk()
    calc = Calculator(root)
    root.mainloop()
