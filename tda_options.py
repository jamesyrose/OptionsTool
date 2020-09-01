import requests
import os
import io
import pandas as pd
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
from PIL import Image


def get_data(symbol, apiKey):
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
    dft_list = dft.groupby("experiation")
    change_func = lambda x: (x.values[1] - x.values[0]) / x.values[0]
    results = []
    for k, v in dft_list:
        v["change"] = v[col].rolling(window=2).apply(change_func)
        results += [v[["strike",
                       "description",
                       "change",
                       "inTheMoney",
                       col]
                    ].rename(columns={col: "price"})
                    ]
    return results


def create_plot(dfp):
    dfp.dropna(inplace=True)
    plt.figure(figsize=(15, 15))
    fig, ax1 = plt.subplots(figsize=(15,15))
    ax2 = ax1.twinx()

    itm = dfp[dfp.inTheMoney == True].strike
    otm = dfp[dfp.inTheMoney == False].strike
    ax1.plot(dfp.strike, dfp.price)
    ax2.plot(dfp.strike, dfp.change  * 100, color="black")
    ax1.axvspan(itm.min(), itm.max(), color='green', alpha=0.25)
    ax1.axvspan(otm.min(), otm.max(), color='red', alpha=0.25)
    for i in dfp.index:
        ax2.text(dfp.loc[i, "strike"],
                 dfp.loc[i, "change"] * 100,
                 f"{round(dfp.loc[i, 'change'] * 100, 2)}%",
                 size=16
                 )
    plt.title(dfp.description.values[0],
              size=24
              )
    ax1.set_xlabel("strike price",
                   size=16
                   )
    ax1.set_ylabel("contract price",
                   size=16
                   )
    ax2.set_ylabel("% Change in Price",
                   size=16
                   )
    ax1.set_xlim((dfp.strike.min(),
                  dfp.strike.max())
                 )

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    im = Image.open(buf)
    return im


def option_main(symbol, apiKey, col="bid", rightLeft=True):
    content = get_data(symbol, apiKey)
    calls = content["callExpDateMap"]
    puts = content["putExpDateMap"]
    calldf = sub_frame_calc(create_dataframe(calls, rightLeft), col)
    putsdf = sub_frame_calc(create_dataframe(puts, rightLeft), col)
    call_plt = {}
    put_plt = {}
    for i in range(len(calldf)):
        dfp = calldf[i]
        descript = dfp.description.values[0]
        call_plt[descript] = create_plot(dfp)
    for i in range(len(putsdf)):
        dfp = putsdf[i]
        descript = dfp.description.values[0]
        put_plt[descript] = create_plot(dfp)
    return call_plt, put_plt