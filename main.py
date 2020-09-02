import os
import tkinter as tk
from tkinter import ttk
from PIL import Image
from tda_options import option_main


class GUI:
    def __init__(self):
        self.gui()
        self.symbol = None
        self.apiKey = None
        self.puts = None
        self.call = None
        self.put_options = None
        self.call_options = None
        self.colcalc = None
        self.rightLeft = None

    def gui(self):
        """
        GUI

        GUI Inputs:
        Symbol: ticker symbol of stock desired
        API Key: TDA API key
        Left or Right Calc: left is calculate descending strike prices
        Column: Column to perform the calculations on

        Call: Call chains
        Puts: Puts Chain

        :return:
        """
        gui = tk.Tk()
        gui.title('Options Map Graph')
        gui.geometry('870x200')
        # gui.configure(background='black')
        # input symbol
        tk.Label(gui,
                 text="Symbol: ",
                 anchor="e"
                 ).grid(row=0,
                        column=0,
                        padx=(50, 20),
                        pady=(10, 10)
                        )
        self.symbol = tk.Entry(gui)
        self.symbol.insert(0,
                           "AMD"
                           )
        self.symbol.grid(row=0,
                         column=1
                         )

        tk.Label(gui,
                 text="API Key: ",
                 anchor="e"
                 ).grid(row=0,
                        column=2
                        )
        self.apiKey = tk.Entry(gui)
        self.apiKey.grid(row=0,
                         column=3,
                         sticky=tk.W+tk.E,
                         columnspan=4
                         )

        # dropdowns
        tk.Label(gui,
                 text="Left or Right Calc :"
                 ).grid(row=1,
                        column=0,
                        padx=(50, 20),
                        pady=(10, 10)
                        )
        n = tk.StringVar()
        self.rightLeft = ttk.Combobox(gui,
                                      textvariable=n,
                                      values=["right", "left"]
                                      )
        self.rightLeft.grid(row=1,
                            column=1
                            )
        tk.Label(gui,
                 text="Column :"
                 ).grid(row=1,
                        column=2
                        )
        o = tk.StringVar()
        self.colcalc = ttk.Combobox(gui,
                                    textvariable=o,
                                    values=["bid", "ask", 'mark', 'last']
                                    )
        self.colcalc.grid(row=1,
                          column=3
                          )
        # submit button
        tk.Button(gui,
                  text="Run Query",
                  command=self.query_data
                  ).grid(row=2,
                         sticky=tk.W+tk.E,
                         columnspan=6
                         )
        # results
        tk.Label(gui,
                 text="Call:"
                 ).grid(row=3,
                        column=0,
                        padx=(50, 20),
                        pady=(10, 10)
                        )
        p = tk.StringVar()
        self.call_options = ttk.Combobox(gui,
                                         width=25,
                                         textvariable=p,
                                         values=[]
                                         )
        self.call_options.grid(row=3,
                               column=1
                               )
        tk.Button(gui,
                  text="Show Call",
                  command=self.show_call
                  ).grid(row=4,
                         sticky=tk.W+tk.E,
                         columnspan=3
                         )

        tk.Label(gui,
                 text="Puts:"
                 ).grid(row=3,
                        column=3
                        )
        q = tk.StringVar()
        self.put_options = ttk.Combobox(gui,
                                        width=25,
                                        textvariable=q,
                                        values=[]
                                        )
        self.put_options.grid(row=3,
                              column=4
                              )
        tk.Button(gui,
                  text="Show Put",
                  command=self.show_put
                  ).grid(row=4,
                         column=3,
                         sticky=tk.W+tk.E,
                         columnspan=3
                         )

        gui.mainloop()
        return self

    def query_data(self):
        """
        Requests data from TDA API.
        Formats them in  qualified dataframes and converts it to a PNG file
        Stored locally in a temporary folder
        Returns file paths ond option description
        """
        if self.rightLeft.get() == "right":
            rl = True
        else:
            rl = False
        self.call, self.puts = option_main(self.symbol.get(),
                                           self.apiKey.get(),
                                           col=self.colcalc.get(),
                                           rightLeft=rl
                                           )
        self.call_options['values'] = list(self.call.keys())
        self.put_options['values'] = list(self.puts.keys())
        return self

    def show_put(self):
        """
        Opens window containing the options graph for selected put
        :return:
        """
        tmp_dir = os.path.join(os.getcwd(), ".tmp")
        Image.open(os.path.join(tmp_dir,
                                self.puts[self.put_options.get()]
                                )
                   ).resize((1000, 1000),
                            Image.ANTIALIAS
                            ).show()

    def show_call(self):
        """
        Opens window containing the options graph for selected call
        :return:
        """
        tmp_dir = os.path.join(os.getcwd(), ".tmp")
        Image.open(os.path.join(tmp_dir,
                                self.call[self.call_options.get()]
                                )
                   ).resize((1000, 1000),
                            Image.ANTIALIAS
                            ).show()


if __name__ == "__main__":
    GUI()
