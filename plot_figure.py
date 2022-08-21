import pandas as pd
import numpy as np
import altair as alt
import shiny.ui as ui

from datetime import timedelta


def filter_df_with_daterange(df: pd.DataFrame, plot_range: str):
    newest = df["Date"].iloc[-1]
    print(plot_range)
    if plot_range == "year":
        oldest = newest - timedelta(days=365)
    elif plot_range == "3months":
        oldest = newest - timedelta(days=93)
    elif plot_range == "month":
        oldest = newest - timedelta(days=31)
    elif plot_range == "week":
        oldest = newest - timedelta(days=7)
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


def plot_generation_severe_cases(url: str, prefec_order: int):
    df = pd.read_csv(url, skiprows=1)

    # fetch refresh date
    string_daterange = str(df.iloc[-1, 0])
    dt_daterefresh = pd.to_datetime(string_daterange.split("~")[1])
    ui.markdown(f"情報更新日(週次): {dt_daterefresh.strftime('%Y年%m月%d日')}")

    # plot
    def prep_gen(df: pd.DataFrame, color: str):
        dfc = df.copy()
        dfc = dfc\
            .stack()\
            .to_frame()\
            .reset_index()\
            .set_axis(["Week", "Generation", "N"], axis=1)\
            .assign(N=lambda x: pd.to_numeric(x.N))

        s_gen = [s.split(" ") for s in dfc["Generation"]]
        dfc["Generation"] = [" ".join(s[1:]) for s in s_gen]
        dfc["color"] = color
        dfc["count"] = range(dfc.shape[0])
        return dfc

    df_male = prep_gen(
        df.tail(1)
        .set_index("Week")
        .iloc[:, 0+(20*prefec_order):10+(20*prefec_order)],
        color="#5c81c7")
    df_female = prep_gen(
        df.tail(1)
        .set_index("Week")
        .iloc[:, 10+(20*prefec_order):20+(20*prefec_order)], color="#cf7794")

    plt_left = alt.Chart(df_male).mark_bar().encode(
        x=alt.X("N",
                scale=alt.Scale(reverse=True)),
        y=alt.Y("Generation",
                sort=df_male["Generation"].to_list()[::-1]),
        color=alt.Color("color", scale=None)
    ).properties(
        width=180,
        height=350
    )
    plt_right = alt.Chart(df_female).mark_bar().encode(
        x=alt.X("N",),
        y=alt.Y("Generation",
                sort=df_male["Generation"].to_list()[::-1]),
        color=alt.Color("color", scale=None)
    ).properties(
        width=180,
        height=350
    )

    return alt.hconcat(plt_left, plt_right)


def plot_newly_cases_stack(url: str, pref_n: int = 0):
    import toolz
    from altair import limit_rows, to_values
    t = lambda data: toolz.curried.pipe(data, limit_rows(max_rows=10000), to_values)
    alt.data_transformers.register('custom', t)
    alt.data_transformers.enable('custom')

    df = pd.read_csv(url, skiprows=1)
    df = df.iloc[:, [0] + list(range(1 + 20*pref_n, 20 + 20*pref_n, 1))]\
        .set_index("Week")\
        .stack()\
        .to_frame()\
        .reset_index()
    df.columns = ["Week", "Generation", "N"]
    df["Generation"] = df.Generation.str.split(" ", expand=True)\
        .iloc[:, 1]\
        .to_list()

    df_merge = pd.merge(
        df,
        pd.DataFrame(
            {"Generation": ["Under", "10s", "20s", "30s", "40s", "50s", "60s", "70s", "80s", "Over"],
             "Group": ["19歳以下", "19歳以下", "20~59歳", "20~59歳", "20~59歳", "20~59歳", "60歳以上", "60歳以上", "60歳以上", "60歳以上"]}
        )
    ).drop("Generation", axis=1)\
        .replace("*", "0")
    df_merge["N"] = pd.to_numeric(df_merge.N)
    df_merge = df_merge\
        .groupby(["Week", "Group"])\
        .agg(sum)\
        .reset_index()

    df_ = df_merge.Week.str.split("~", expand=True)
    df_.columns = ["week_start", "week_end"]
    df_merge["week_start"] = pd.to_datetime(df_.week_start)
    df_merge["week_end"] = pd.to_datetime(df_.week_end)

    chart = alt.Chart(df_merge.iloc[-60:-1, :]).mark_bar(
        width=10).encode(
        x=alt.X("week_end"),
        y="N",
        color=alt.Color("Group",
                        scale=alt.Scale(
                            domain=["19歳以下", "20~59歳", "60歳以上"],
                            range=["#A6B8CE", "#83BB48", "#863130"]
                        ))
    )
    return chart


def plot_pcr_org(url: str):
    df = pd.read_csv(url).iloc[:, :-3]\
        .set_index("日付")\
        .stack()\
        .to_frame()\
        .reset_index()
    df.columns = ["Date", "Organization", "N"]
    df["Date"] = pd.to_datetime(df.Date)

    import toolz
    from altair import limit_rows, to_values
    t = lambda data: toolz.curried.pipe(data, limit_rows(max_rows=10000), to_values)
    alt.data_transformers.register('custom', t)
    alt.data_transformers.enable('custom')

    chart = alt.Chart(df).mark_area(size=10).encode(
        x="Date",
        y="N",
        color=alt.Color("Organization",
                        legend=alt.Legend(
                            legendX=120, legendY=-40,
                            orient="top",
                            # direction="horizontal",
                            titleAnchor="middle"
                        ))
    ).properties(
        width=1000
    )

    return chart


def plot_positive_rate(url_pcr: str, url_detected: str):
    df_pcr = pd.read_csv(url_pcr)\
        .set_axis(["Date", "PCR"], axis=1)
    df_det = pd.read_csv(url_detected)\
        .iloc[:, :2]\
        .set_axis(["Date", "Detection"], axis=1)
    df_merge = pd.merge(df_pcr, df_det)\
        .assign(positive_rate=lambda x: x["Detection"] * 100 / x["PCR"])\
        .assign(positive_rate=lambda x: x["positive_rate"].round(1))\
        .assign(Date=lambda x: pd.to_datetime(x["Date"]))\
        .assign(PCR=lambda x: x["PCR"] / 100000)

    week_l: list[int] = sum([[i] * 7 for i in range(df_merge.shape[0] // 7)], [])
    week_l = week_l + [int(week_l[-1]) + 1] * (df_merge.shape[0] % 7 )
    df_merge["week_n"] = week_l[::-1]

    df_sum = df_merge.groupby("week_n").agg("sum")
    df_mean = df_merge.groupby("week_n").agg("mean")
    df_sum["week"] = list(df_merge.Date[::7])[::-1]
    df_sum["positive_rate"] = df_mean.positive_rate


    base = alt.Chart(df_sum.iloc[:-30, :]).encode(
        alt.X("week", axis=alt.Axis(title=None))
    )

    bar = base.mark_bar(color="#5276A7").encode(
        alt.Y("PCR",
            axis=alt.Axis(title="PCR検査数(万人)",
                            titleColor="#5276A7"))
    )

    line = base.mark_line(color='#ff841f').encode(
        alt.Y("positive_rate",
            axis=alt.Axis(title="陽性率(%)",
                            titleColor='#ff841f'))
    )

    chart = alt.layer(bar, line).resolve_scale(
        y="independent"
    )

    return chart
