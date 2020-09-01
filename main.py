import tkinter as tk
from tkinter import ttk




class GUI:
    def __init__(self):
        gui = tk.Tk()
        gui.title('Options Map Graph')
        gui.geometry('800x500')
        # input symbol
        tk.Label(gui, text="Symbol").grid(row=0)
        self.symbol = tk.Entry(gui)
        self.symbol.grid(row=0, column=1)

        tk.Label(gui, text="API Key").grid(row=0, column=2)
        self.apiKey = tk.Entry(gui)
        self.apiKey.grid(row=0, column=3)

        # dropdowns
        tk.Label(gui, text="Call or Puts :").grid(row=1, column=0)
        n = tk.StringVar()
        self.putCall = ttk.Combobox(gui, width=10, textvariable=n, values=["call", "put"])
        self.putCall.grid(row=1, column=1)

        tk.Label(gui, text="Left or Right Calc :").grid(row=1, column=2)
        n = tk.StringVar()
        self.rightLeft = ttk.Combobox(gui, width=10, textvariable=n, values=["right", "left"])
        self.rightLeft.grid(row=1, column=3)

        tk.Label(gui, text="Column :").grid(row=1, column=4)
        n = tk.StringVar()
        self.colcalc = ttk.Combobox(gui, width=10, textvariable=n, values=["bid", "ask", 'mark', 'last'])
        self.colcalc.grid(row=1, column=5)
        # submit button
        tk.Button(gui, text="submit", command=self.query_data).grid(row=2, column=4, sticky=tk.W, pady=4)


        gui.mainloop()

    def query_data(self):
        """

        """

