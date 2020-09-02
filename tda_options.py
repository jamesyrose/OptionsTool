import os
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from dateutil.relativedelta import relativedelta



def get_data(symbol, apiKey):
    """
    Gets data from TDA API

    :param symbol: ticker symbol (str)
    :param apiKey: TDA API key (str)
    :return: option chains (dict)
    """
    endpoint = f"https://api.tdameritrade.com/v1/marketdata/chains?apikey={apiKey}"
    payload = {"symbol": symbol,
               "contractType": "ALL",
               "strikeCount": 20,
               "includeQuotes": False,
               "strategy": "SINGLE",
               "range": "ALL",
               "includeQuotes": True,
               "fromDate": datetime.now().strftime("%Y-%m-%d"),
               "toDate": (datetime.now() + relativedelta(years=1)).strftime("%Y-%m-%d")}
    content = requests.get(url=endpoint, params=payload)
    return content.json()


def create_dataframe(data, asc):
    """
    Extracts data from the TDA json dict.

    :param data: TDA options chain (dict)
    :param asc: True for oscending strike price (bool)
    :return:  pandas.DataFrame
    """
    df = pd.DataFrame()
    for data in data.values():
        for key in list(data.keys()):
            ind = len(df) + 1
            df.loc[ind, "strike"] = float(key)
            for key2 in list(data[key][0].keys()):
                if key2 in ["bid", "ask", "last", "mark", "bidSize", "askSize", "description", "inTheMoney", "symbol",
                            "putCall"]:
                    df.loc[ind, key2] = data[key][0][key2]
        df["experiation"] = df.symbol.apply(
            lambda x: datetime.strptime(x.split("_")[1].split("C")[0].split("P")[0], "%m%d%y"))
    df = df.sort_values(by="strike", axis=0, ascending=asc).reset_index(drop=True)
    return df


def sub_frame_calc(dft, col):
    """
    Calculating the change in price for options

    :param dft: single strike price option chain (pandas.DataFrame)
    :param col:  column that calc should be performed on (str)
    :return:  pandas.DataFrame
    """
    dft_list = dft.groupby("experiation")
    results = []
    for k, v in dft_list:
        v["change"] = (v[col] - v[col].shift(1)) / v[col].shift(1)
        results += [v[["strike",
                       "description",
                       "change",
                       "inTheMoney",
                       col]
                    ].rename(columns={col: "price"})
                    ]

    return results


def create_plot(dfp):
    """
    Converts data into plots for GUI use

    :param dfp: pandas.DataFrame
    :return: os.path
    """
    dfp.dropna(inplace=True)
    plt.figure(figsize=(30, 30))
    fig, ax1 = plt.subplots(figsize=(30, 30))
    ax2 = ax1.twinx()
    itm = dfp[dfp.inTheMoney == True].strike
    otm = dfp[dfp.inTheMoney == False].strike
    ax1.plot(dfp.strike, dfp.price)
    ax2.plot(dfp.strike, dfp.change * 100, color="black")
    ax1.axvspan(itm.min(), itm.max(), color='green', alpha=0.25)
    ax1.axvspan(otm.min(), otm.max(), color='red', alpha=0.25)
    for i in dfp.index:
        ax2.text(dfp.loc[i, "strike"],
                 dfp.loc[i, "change"] * 100,
                 f"{round(dfp.loc[i, 'change'] * 100, 2)}%",
                 size=32
                 )
    plt.title(dfp.description.values[0],
              size=48
              )
    ax1.set_xlabel("strike price",
                   size=32
                   )
    ax1.set_ylabel("contract price",
                   size=32
                   )
    ax2.set_ylabel("% Change in Price",
                   size=32
                   )
    ax1.set_xlim((dfp.strike.min(),
                  dfp.strike.max())
                 )
    ax1.tick_params(axis='both', which='major', labelsize=32)
    ax2.tick_params(axis='both', which='major', labelsize=32)

    save_dir = os.path.join(os.getcwd(),
                            ".tmp",
                            f"{np.random.randint(1e15)}.png")
    plt.savefig(save_dir, format='png')
    plt.close()
    return save_dir


def option_main(symbol, apiKey, col="bid", rightLeft=True):
    """
    Queries data and calculates option chains change in price and plots it

    :param symbol: ticker symbol (str)
    :param apiKey:  TDA API key (str)
    :param col:  column for calculation (str)
    :param rightLeft:  right is ascending strike price (bool)
    :return: dict
    """
    tmp_dir = os.path.join(os.getcwd(), '.tmp')
    os.system(f"rm -rf {tmp_dir}; mkdir {tmp_dir}")
    content = get_data(symbol, apiKey)
    calls = content["callExpDateMap"]
    puts = content["putExpDateMap"]
    calldf = sub_frame_calc(create_dataframe(calls, rightLeft), col)
    putsdf = sub_frame_calc(create_dataframe(puts, rightLeft), col)

    call_plt = {}
    put_plt = {}
    for call in calldf:
        call_plt[call.description.values[0]] = create_plot(call)
    for put in putsdf:
        put_plt[put.description.values[0]] = [create_plot(put)]
    return call_plt, put_plt