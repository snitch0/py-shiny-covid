import tomli

from shiny.ui import p, span, div, br
import pandas as pd


def metrics_card_item(str_title: str, num_main: int, num_sub=0):

    num_main_str = f'{num_main:,}'
    arrow_char = "⬆︎" if num_sub > 0 else "⬇"

    if num_sub:
        num_sub_str = f'{num_sub:,}'
        card = div(
            div(
                p(str_title),
                p(
                    span(num_main_str, class_="col4-pattern1_num",
                         id="curSituNewCaseKPI"),
                    span("人", class_="fontSize3"),
                    br(),
                    span("前日比", class_="fontSize4"),
                    span(arrow_char,
                         class_="fontSize8",
                         id="curSituNewCaseArw",
                         style="color: rgb(204, 0, 0)"),
                    span(num_sub_str, class_="fontSize6", id="curSituNewCaseDB"),
                    span("人", class_="fontSize7")
                ),
                class_="col4-pattern1_sub"
            ), class_="col4-pattern1_item"
        )
    else:
        card = div(
            div(
                p(str_title),
                p(
                    span(num_main_str, class_="col4-pattern1_num",
                         id="curSituNewCaseKPI"),
                    span("人", class_="fontSize3"),
                    br(),
                ),
                class_="col4-pattern1_sub"
            ), class_="col4-pattern1_item"
        )
    return card


# metrics1
def metrics_get_diff(
    pref: str,
    url="https://covid19.mhlw.go.jp/public/opendata/newly_confirmed_cases_daily.csv"):
    df = pd.read_csv(url)
    num = df[pref]
    today_num = num.iloc[-1]
    diff = int(today_num) - int(num.iloc[-2])
    return int(today_num), diff

def metrics_cumulative_newly_cases(
    pref: str,
    url="https://covid19.mhlw.go.jp/public/opendata/newly_confirmed_cases_daily.csv"):
    df = pd.read_csv(url)
    return pd.to_numeric(df[pref]).sum()

def death_cases_cumulative(
    pref: str,
    url="https://covid19.mhlw.go.jp/public/opendata/deaths_cumulative_daily.csv"
):
    df = pd.read_csv(url)
    deaths = pd.to_numeric(df[pref])
    diff = deaths.iloc[-1] - deaths.iloc[-2]
    return deaths.iloc[-1], diff

def week_average(url: str, week_shift: int, pref: str) -> int:
    df = pd.read_csv(url)
    ave = df[pref].iloc[-8-(7*week_shift):-1-(7*week_shift)].mean()
    return int(ave)

def new_cases_p_10thousand(url: str, pref: str):
    df = pd.read_csv(url)
    return int(df["ALL"].iloc[-1]), int(df["ALL"].iloc[-2]) - int(df["ALL"].iloc[-1])
