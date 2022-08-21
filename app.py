from pathlib import Path

from htmltools import head_content
from shiny import App, reactive, render, ui
from shinywidgets import output_widget, render_widget

import metrics_box
import prefecture_dictionary
import plot_figure
import plot_func

CSV_URL = "https://covid19.mhlw.go.jp/public/opendata/newly_confirmed_cases_daily.csv"
pref = prefecture_dictionary.create_pref_dict()


def col_plot_block(title: str, plot_id: str, radio_id: str = ""):
    if radio_id:
        block = ui.column(4,
                          ui.markdown(f"#### {title}"),
                          ui.input_radio_buttons(
                              radio_id,
                              "グラフ表示期間",
                              {
                                  "week": "1週間",
                                  "month": "1か月",
                                  "3months": "3か月",
                                  "year": "1年"
                              },
                              selected="year"
                          ),
                          output_widget(plot_id)),
    else:
        block = ui.column(4,
                          ui.markdown(f"#### {title}"),
                          output_widget(plot_id)),
    return block


def tab1_contents():
    contents = ui.row(
        col_plot_block("新規陽性者数の推移(日別)", "plot1_1", "rb1"),
        col_plot_block("人口10万人当たり新規陽性者数", "plot1_2", "rb2"),
        col_plot_block("性別・年代別新規陽性者数(週別)", "plot1_3")
    )
    return contents


def tab2_contents():
    contents = ui.row(
        col_plot_block("新規感染者報告数", "plot2_1"),
        col_plot_block("検査状況", "plot2_2"),
        col_plot_block("陽性率", "plot2_3")
    )
    return contents


app_ui = ui.page_fluid(
    # head
    head_content(
        ui.tags.meta(charset="UTF-8"),
        ui.tags.style((Path(__file__).parent / "style.css").read_text()
                      ),
        ui.tags.link(rel="stylesheet",
                     href="https://cdnjs.cloudflare.com/ajax/libs/normalize/5.0.0/normalize.min.css"),
        ui.tags.link(rel="stylesheet",
                     href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"),
    ),
    ui.navset_pill(
        ui.nav(
            "感染者動向",
            ui.markdown("----"),
            ui.output_ui("metricsCards"),
            ui.markdown("---"),
            tab1_contents()
        ),
        ui.nav(
            "レベルの判断で参考とされる指標関連データ",
            tab2_contents()
        ),
        header=ui.input_select(
            id="prefecture",
            label="都道府県ごとに閲覧できます。",
            choices=list(pref.keys()),
        )
    ),
)


def server(input, output, session):
    @output
    @render.ui
    @reactive.event(input.prefecture)
    def metricsCards():
        prefecID = pref[input.prefecture()]
        # metrics
        metrics1_1, metrics1_2 = metrics_box.metrics_get_diff(pref=prefecID[0])
        metrics2 = metrics_box.metrics_cumulative_newly_cases(pref=prefecID[0])
        metrics3_1, metrics3_2 = metrics_box.metrics_get_diff(
            pref=prefecID[0],
            url="https://covid19.mhlw.go.jp/public/opendata/severe_cases_daily.csv"
        )
        metrics4_1, metrics4_2 = metrics_box.death_cases_cumulative(
            pref=prefecID[0],
            url="https://covid19.mhlw.go.jp/public/opendata/deaths_cumulative_daily.csv"
        )

        tags = ui.div(
            ui.div(
                metrics_box.metrics_card_item(
                    str_title="新規の陽性者数",
                    num_main=metrics1_1,
                    num_sub=metrics1_2),
                metrics_box.metrics_card_item(
                    str_title="陽性者の累積",
                    num_main=metrics2),
                metrics_box.metrics_card_item(
                    str_title="現在の重症者数",
                    num_main=metrics3_1,
                    num_sub=metrics3_2),
                metrics_box.metrics_card_item(
                    str_title="死亡者の累積",
                    num_main=metrics4_1,
                    num_sub=metrics4_2),
                class_="col4-pattern1_left"
            ),
            class_="col4-pattern1"
        )
        return tags

    @output
    @render.plot
    def my_plot():
        plot = plot_func.plot_line_cases(
            url="https://covid19.mhlw.go.jp/public/opendata/newly_confirmed_cases_daily.csv",
            prefec=pref[input.prefecture()][0],
            period=input.rb1()
        )
        return plot

    @output
    @render_widget
    def plot1_1():
        return plot_figure.plot_new_cases(
            url="https://covid19.mhlw.go.jp/public/opendata/newly_confirmed_cases_daily.csv",
            plot_range=input.rb1(),
            ytick_space=50000,
            color="#fd6262",
            prefecture=pref[input.prefecture()][0]
        )

    @output
    @render_widget
    def plot1_2():
        return plot_figure.plot_new_cases(
            url="https://covid19.mhlw.go.jp/public/opendata/newly_confirmed_cases_per_100_thousand_population_daily.csv",
            plot_range=input.rb2(),
            ytick_space=40,
            color="#a1b8e8",
            prefecture=pref[input.prefecture()][0]
        )

    @output
    @render_widget
    def plot1_3():
        return plot_figure.plot_generation_severe_cases(
            url="https://covid19.mhlw.go.jp/public/opendata/newly_confirmed_cases_detail_weekly.csv",
            prefec_order=pref[input.prefecture()][1]
        )

    @output
    @render_widget
    def plot2_1():
        return plot_figure.plot_newly_cases_stack(
            url="https://covid19.mhlw.go.jp/public/opendata/newly_confirmed_cases_detail_weekly.csv",
            pref_n=pref[input.prefecture()][1]
        )

    @output
    @render_widget
    def plot2_2():
        return plot_figure.plot_pcr_org(
            url="https://www.mhlw.go.jp/content/pcr_case_daily.csv"
        )

    @output
    @render_widget
    def plot2_3():
        return plot_figure.plot_positive_rate(
            url_pcr="https://www.mhlw.go.jp/content/pcr_tested_daily.csv",
            url_detected="https://covid19.mhlw.go.jp/public/opendata/newly_confirmed_cases_daily.csv"
        )


app = App(app_ui, server)
