import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from dateutil.relativedelta import relativedelta
from datetime import datetime
import altair as alt

import japanize_matplotlib

sns.set_theme(style='whitegrid', font="IPAexGothic")


def convert_period(period:str):
    if period == "1w":
        return relativedelta(weeks=1)
    elif period == "1m":
        return relativedelta(month=1)
    elif period == "3m":
        return relativedelta(months=3)
    elif period == "12m":
        return relativedelta(years=1)
    else:
        raise TypeError("Unkown period.")


def plot_line_cases(url: str, prefec: str, period: str):
    df = pd.read_csv(url)
    df["Date"] = pd.to_datetime(df.Date)
    df_ = df[df.Date > datetime.today() - convert_period(period)]

    fig, ax = plt.subplots()
    sns.lineplot(data=df_, x="Date", y = "ALL", ax=ax)
    ax.fill_between(df_["Date"], df_[prefec], np.zeros(len(df_.Date)))
    ax.set_ylabel("")

    return fig

def plot_piramid(
    url = "https://covid19.mhlw.go.jp/public/opendata/newly_confirmed_cases_detail_weekly.csv",
    prefecture_n=1):

    def parse_weekly_data(df: pd.DataFrame, datarange: list):
        df_ = df.tail(1)\
            .iloc[:, datarange].reset_index().set_index("Week")\
            .iloc[:, 1:]\
            .stack().to_frame().reset_index()\
            .set_axis(["Week", "Generation", "N"], axis=1)

        df_["N"] = pd.to_numeric(df_["N"])

        s_gen = [s.split(" ") for s in df_["Generation"]]
        df_["Generation"] = [" ".join(s[1:]) for s in s_gen]

        return df_

    i = prefecture_n
    range_m = [0] + list(range(i, i+10, 1))
    range_f = [0] + list(range(i+11, i+20, 1))

    df = pd.read_csv(url, skiprows=2)
    df_male = parse_weekly_data(df, range_m)
    df_female = parse_weekly_data(df, range_f)

    fig, ax = plt.subplots(ncols=2, figsize=(14,6))

    sns.barplot(x="N", y="Generation",
                data=df_male[::-1], ax=ax[0], color = "#648cd8")
    sns.barplot(x="N", y="Generation",
                data=df_female[::-1], ax=ax[1], color="#d97d9b")
    ax[0].yaxis.tick_right()
    ax[1].yaxis.set_ticklabels([])
    ax[0].set_xlim([120000, 0])
    ax[1].set_xlim([0, 120000])
    ax[0].text(20000, -1, "男性", size=20)
    ax[1].text(20000, -1, "女性", size=20, ha="right")
    [axi.set_ylabel("") for axi in ax]

    return fig


##############

def filter_df_with_daterange(df: pd.DataFrame, plot_range: str):
    newest = df["Date"].iloc[-1]
    if plot_range == "12m":
        oldest = newest - relativedelta(days=365)
    elif plot_range == "3m":
        oldest = newest - relativedelta(days=93)
    elif plot_range == "1m":
        oldest = newest - relativedelta(days=31)
    elif plot_range == "1w":
        oldest = newest - relativedelta(days=7)
    else:
        raise TypeError("range must be in [year, 3months, month, week]")

    return df.query(f"Date >= '{oldest.strftime('%Y-%m-%d')}'")


def plot_new_cases(plot_range: str, url: str, ytick_space: int, color: str,
                   prefecture: str):
    df = pd.read_csv(url)
    df["Date"] = pd.to_datetime(df["Date"])
    df["col"] = color

    chart = alt.Chart(filter_df_with_daterange(df, plot_range)).mark_area(
    ).encode(
        alt.Y(prefecture, axis=alt.Axis(
            values=[i*ytick_space for i in range(1, 6, 1)])),
        x="Date",
        color=alt.Color("col", scale=None)
    )

    return chart
