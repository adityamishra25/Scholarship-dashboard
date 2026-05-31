import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, dash_table
import warnings
import gdown
import os
warnings.filterwarnings("ignore")

# ── Load & preprocess ──────────────────────────────────────────────────────────
DATA_PATH = "master_dataset.csv"

if not os.path.exists(DATA_PATH):
    gdown.download(
        "https://drive.google.com/uc?id=1qfqIGGDKBfrBo0sEN1AwiyOFSFvk6iYN",
        DATA_PATH, quiet=False, fuzzy=True
    )

df = pd.read_csv(DATA_PATH)

df["registration_date"] = pd.to_datetime(df["registration_date"], dayfirst=True, errors="coerce")
df["payment_date"]      = pd.to_datetime(df["payment_date"],      dayfirst=True, errors="coerce")
df["reg_month"]         = df["registration_date"].dt.to_period("M").astype(str)
df["amount"]            = pd.to_numeric(df["amount"], errors="coerce")

# ── Colour palette ─────────────────────────────────────────────────────────────
C = dict(
    bg="#0d1117", card="#161b22", border="#30363d",
    text="#e6edf3", muted="#8b949e",
    green="#3fb950", red="#f85149", yellow="#d29922",
    blue="#388bfd", purple="#bc8cff", cyan="#39d5f5",
    accent="#1f6feb",
)

CARD_STYLE = {
    "background": C["card"], "border": f"1px solid {C['border']}",
    "borderRadius": "10px", "padding": "20px",
}

# ── Precompute aggregates ──────────────────────────────────────────────────────
total_students  = len(df)
total_amount    = df["amount"].sum()
neg_amount_count = (df["amount"] < 0).sum()
verified_pct    = (df["status"] == "Verified").sum() / total_students * 100
rejected_pct    = (df["status"] == "Rejected").sum() / total_students * 100
pending_pct     = (df["status"] == "Pending").sum()  / total_students * 100
failed_pct      = (df["payment_status"] == "Failed").sum() / total_students * 100
bounced_pct     = (df["payment_status"] == "Bounced").sum() / total_students * 100
unknown_status  = (df["status"] == "Unknown").sum()

dist_summary = df.groupby("district").agg(
    Total=("student_id", "count"),
    Verified=("status",   lambda x: (x == "Verified").sum()),
    Rejected=("status",   lambda x: (x == "Rejected").sum()),
    Pending=("status",    lambda x: (x == "Pending").sum()),
    Unknown=("status",    lambda x: (x == "Unknown").sum()),
    Disbursed=("amount",  lambda x: x[x > 0].sum()),
    Failed_Payments=("payment_status", lambda x: (x == "Failed").sum()),
    Bounced_Payments=("payment_status",lambda x: (x == "Bounced").sum()),
    Neg_Amounts=("amount", lambda x: (x < 0).sum()),
).reset_index()
dist_summary["Rejection_Rate"] = (dist_summary["Rejected"] / dist_summary["Total"] * 100).round(1)
dist_summary["Payment_Failure_Rate"] = (
    (dist_summary["Failed_Payments"] + dist_summary["Bounced_Payments"]) / dist_summary["Total"] * 100
).round(1)

office_summary = df.groupby("office_code").agg(
    Total=("student_id", "count"),
    Verified=("status",  lambda x: (x == "Verified").sum()),
    Rejected=("status",  lambda x: (x == "Rejected").sum()),
    Pending=("status",   lambda x: (x == "Pending").sum()),
    Unknown=("status",   lambda x: (x == "Unknown").sum()),
).reset_index()
office_summary["Rejection_Rate"] = (office_summary["Rejected"] / office_summary["Total"] * 100).round(1)
office_summary["Unknown_Rate"]   = (office_summary["Unknown"]  / office_summary["Total"] * 100).round(1)

monthly = df.groupby("reg_month").agg(
    Registrations=("student_id", "count"),
    Verified=("status", lambda x: (x == "Verified").sum()),
    Pending=("status",  lambda x: (x == "Pending").sum()),
).reset_index().sort_values("reg_month")

cat_status = df.groupby(["category", "status"]).size().reset_index(name="Count")

# ── Helper builders ────────────────────────────────────────────────────────────

def kpi_card(title, value, subtitle="", color=C["blue"], flag=False):
    border_color = C["red"] if flag else C["border"]
    flag_badge = html.Span(
        "⚠ Alert", style={
            "background": C["red"], "color": "white",
            "fontSize": "10px", "padding": "2px 7px",
            "borderRadius": "4px", "marginLeft": "8px", "fontWeight": "700",
        }
    ) if flag else ""
    return html.Div([
        html.P(title, style={"color": C["muted"], "fontSize": "12px",
                              "marginBottom": "4px", "textTransform": "uppercase",
                              "letterSpacing": "1px"}),
        html.Div([
            html.H2(value, style={"color": color, "margin": "0",
                                  "fontSize": "28px", "fontWeight": "700"}),
            flag_badge,
        ], style={"display": "flex", "alignItems": "center"}),
        html.P(subtitle, style={"color": C["muted"], "fontSize": "11px",
                                 "marginTop": "4px", "marginBottom": "0"}),
    ], style={**CARD_STYLE, "border": f"1px solid {border_color}",
              "borderLeft": f"4px solid {color}"})


def section_header(text):
    return html.H3(text, style={
        "color": C["text"], "fontSize": "14px", "fontWeight": "700",
        "textTransform": "uppercase", "letterSpacing": "1.5px",
        "borderBottom": f"1px solid {C['border']}",
        "paddingBottom": "8px", "marginBottom": "16px", "marginTop": "0",
    })


# ── Figures ────────────────────────────────────────────────────────────────────

def fig_district_bar():
    fig = go.Figure()
    colors = [C["green"], C["red"], C["yellow"], C["muted"]]
    for col, clr in zip(["Verified","Rejected","Pending","Unknown"], colors):
        fig.add_trace(go.Bar(
            name=col, x=dist_summary["district"], y=dist_summary[col],
            marker_color=clr, hovertemplate=f"<b>%{{x}}</b><br>{col}: %{{y:,}}<extra></extra>",
        ))
    fig.update_layout(
        barmode="stack", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color=C["text"], legend=dict(orientation="h", y=-0.2),
        margin=dict(l=0, r=0, t=10, b=40),
        xaxis=dict(showgrid=False, linecolor=C["border"]),
        yaxis=dict(showgrid=True, gridcolor=C["border"], linecolor=C["border"]),
        hoverlabel=dict(bgcolor=C["card"]),
    )
    return fig


def fig_payment_donut():
    ps = df["payment_status"].value_counts()
    clr = {"Success": C["green"], "Processing": C["blue"],
           "Failed": C["red"], "Bounced": C["yellow"]}
    fig = go.Figure(go.Pie(
        labels=ps.index, values=ps.values,
        hole=0.55, marker_colors=[clr.get(l, C["muted"]) for l in ps.index],
        textinfo="percent+label", textfont_size=11,
        hovertemplate="<b>%{label}</b><br>Count: %{value:,}<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", font_color=C["text"],
        showlegend=False, margin=dict(l=0, r=0, t=10, b=10),
        annotations=[dict(text=f"<b>{total_students/1e6:.1f}M</b><br>Students",
                          x=0.5, y=0.5, font_size=14, showarrow=False,
                          font_color=C["text"])],
    )
    return fig


def fig_monthly_trend():
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly["reg_month"], y=monthly["Registrations"],
        name="Registrations", line=dict(color=C["blue"], width=2),
        fill="tozeroy", fillcolor="rgba(56,139,253,0.1)",
    ))
    fig.add_trace(go.Scatter(
        x=monthly["reg_month"], y=monthly["Verified"],
        name="Verified", line=dict(color=C["green"], width=2, dash="dot"),
    ))
    fig.add_trace(go.Scatter(
        x=monthly["reg_month"], y=monthly["Pending"],
        name="Pending", line=dict(color=C["yellow"], width=2, dash="dot"),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color=C["text"], margin=dict(l=0, r=0, t=10, b=40),
        xaxis=dict(showgrid=False, linecolor=C["border"]),
        yaxis=dict(showgrid=True, gridcolor=C["border"], linecolor=C["border"],
                   tickformat=","),
        legend=dict(orientation="h", y=-0.25),
        hoverlabel=dict(bgcolor=C["card"]),
    )
    return fig


def fig_category_bar():
    clr = {"Verified": C["green"], "Rejected": C["red"],
           "Pending": C["yellow"], "Unknown": C["muted"]}
    fig = px.bar(cat_status, x="category", y="Count", color="status",
                 color_discrete_map=clr, barmode="group",
                 labels={"Count": "Students", "category": "Category", "status": "Status"})
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color=C["text"], margin=dict(l=0, r=0, t=10, b=40),
        xaxis=dict(showgrid=False, linecolor=C["border"]),
        yaxis=dict(showgrid=True, gridcolor=C["border"]),
        legend=dict(orientation="h", y=-0.25),
    )
    return fig


def fig_office_heatmap():
    top15 = office_summary.sort_values("Total", ascending=False).head(15)
    fig = go.Figure(go.Bar(
        y=top15["office_code"], x=top15["Rejection_Rate"],
        orientation="h",
        marker=dict(
            color=top15["Rejection_Rate"],
            colorscale=[[0, C["green"]], [0.5, C["yellow"]], [1, C["red"]]],
            showscale=True,
            colorbar=dict(title="Rejection %", tickfont=dict(color=C["muted"])),
        ),
        hovertemplate="<b>%{y}</b><br>Rejection Rate: %{x:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color=C["text"], margin=dict(l=0, r=0, t=10, b=10),
        xaxis=dict(showgrid=True, gridcolor=C["border"], title="Rejection Rate (%)"),
        yaxis=dict(showgrid=False),
    )
    return fig


def fig_amount_dist():
    valid = df[df["amount"].notna() & (df["amount"] >= 0)]["amount"]
    fig = go.Figure(go.Histogram(
        x=valid, nbinsx=40,
        marker_color=C["purple"], opacity=0.8,
        hovertemplate="Amount: ₹%{x}<br>Count: %{y:,}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color=C["text"], margin=dict(l=0, r=0, t=10, b=40),
        xaxis=dict(showgrid=False, linecolor=C["border"], title="Amount (₹)"),
        yaxis=dict(showgrid=True, gridcolor=C["border"], title="Count"),
    )
    return fig


# ── District table ─────────────────────────────────────────────────────────────
dist_table_data = dist_summary.copy()
dist_table_data["Disbursed"] = dist_table_data["Disbursed"].apply(lambda x: f"₹{x/1e7:.1f}Cr")
dist_table_data["Rejection_Rate"] = dist_table_data["Rejection_Rate"].apply(lambda x: f"{x}%")
dist_table_data["Payment_Failure_Rate"] = dist_table_data["Payment_Failure_Rate"].apply(lambda x: f"{x}%")
dist_table_cols = ["district","Total","Verified","Rejected","Pending",
                   "Unknown","Disbursed","Rejection_Rate","Payment_Failure_Rate","Neg_Amounts"]

TABLE_STYLE = dict(
    style_table={"overflowX": "auto"},
    style_header={"backgroundColor": C["accent"], "color": "white",
                  "fontWeight": "700", "fontSize": "12px", "border": "none"},
    style_cell={"backgroundColor": C["card"], "color": C["text"],
                "border": f"1px solid {C['border']}", "fontSize": "12px",
                "padding": "8px 12px", "textAlign": "center"},
    style_data_conditional=[
        {"if": {"filter_query": '{Rejection_Rate} contains "25"',
                "column_id": "Rejection_Rate"},
         "color": C["red"], "fontWeight": "700"},
        {"if": {"filter_query": '{Neg_Amounts} > 1000',
                "column_id": "Neg_Amounts"},
         "color": C["red"]},
    ],
)

# ── App layout ─────────────────────────────────────────────────────────────────
app = Dash(__name__, title="Student Welfare Dashboard")
app.layout = html.Div(style={"backgroundColor": C["bg"], "minHeight": "100vh",
                              "fontFamily": "'Inter', 'Segoe UI', sans-serif",
                              "color": C["text"], "padding": "24px"}, children=[

    # ── Header ──────────────────────────────────────────────────────────────────
    html.Div([
        html.Div([
            html.H1("Student Welfare Scholarship Dashboard",
                    style={"margin": "0", "fontSize": "22px", "fontWeight": "700",
                           "color": C["text"]}),
            html.P("Senior Official Overview · FY 2024 · All Districts",
                   style={"margin": "4px 0 0", "color": C["muted"], "fontSize": "13px"}),
        ]),
        html.Div([
            html.Span("LIVE", style={
                "background": C["green"], "color": "black", "padding": "3px 10px",
                "borderRadius": "20px", "fontSize": "11px", "fontWeight": "800",
                "marginRight": "12px",
            }),
            html.Span("Total Records: 1,919,976",
                      style={"color": C["muted"], "fontSize": "13px"}),
        ], style={"display": "flex", "alignItems": "center"}),
    ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "flex-start",
              "marginBottom": "24px",
              "borderBottom": f"1px solid {C['border']}", "paddingBottom": "16px"}),

    # ── Critical Alerts Banner ───────────────────────────────────────────────────
    html.Div([
        html.Div("🚨 CRITICAL ATTENTION REQUIRED", style={
            "color": C["red"], "fontWeight": "800", "fontSize": "12px",
            "letterSpacing": "1px", "marginBottom": "8px",
        }),
        html.Div([
            html.Span(f"⚠ {neg_amount_count:,} negative-amount transactions detected",
                      style={"marginRight": "24px", "fontSize": "12px"}),
            html.Span(f"⚠ {unknown_status:,} applications with 'Unknown' status ({unknown_status/total_students*100:.1f}%)",
                      style={"marginRight": "24px", "fontSize": "12px"}),
            html.Span(f"⚠ ~{failed_pct+bounced_pct:.1f}% payments failed or bounced",
                      style={"fontSize": "12px"}),
        ], style={"color": C["yellow"]}),
    ], style={
        "background": "rgba(248,81,73,0.08)", "border": f"1px solid {C['red']}",
        "borderRadius": "8px", "padding": "14px 20px", "marginBottom": "24px",
    }),

    # ── KPI Row ──────────────────────────────────────────────────────────────────
    html.Div([
        html.Div(kpi_card("Total Students", f"{total_students/1e6:.2f}M",
                           "Across 5 districts", C["blue"]),
                 style={"flex": "1", "minWidth": "160px"}),
        html.Div(kpi_card("Total Disbursed", f"₹{total_amount/1e7:.1f} Cr",
                           "Positive transactions only", C["green"]),
                 style={"flex": "1", "minWidth": "160px"}),
        html.Div(kpi_card("Verified", f"{verified_pct:.1f}%",
                           f"{(df['status']=='Verified').sum():,} students", C["green"]),
                 style={"flex": "1", "minWidth": "160px"}),
        html.Div(kpi_card("Rejection Rate", f"{rejected_pct:.1f}%",
                           f"{(df['status']=='Rejected').sum():,} rejected", C["red"], flag=True),
                 style={"flex": "1", "minWidth": "160px"}),
        html.Div(kpi_card("Pending Review", f"{pending_pct:.1f}%",
                           f"{(df['status']=='Pending').sum():,} awaiting", C["yellow"], flag=True),
                 style={"flex": "1", "minWidth": "160px"}),
        html.Div(kpi_card("Payment Failures", f"{(failed_pct+bounced_pct):.1f}%",
                           "Failed + Bounced combined", C["red"], flag=True),
                 style={"flex": "1", "minWidth": "160px"}),
        html.Div(kpi_card("Anomalous Txns", f"{neg_amount_count:,}",
                           "Negative amount records", C["purple"], flag=True),
                 style={"flex": "1", "minWidth": "160px"}),
    ], style={"display": "flex", "gap": "12px", "flexWrap": "wrap", "marginBottom": "20px"}),

    # ── Row 2: District Bar + Payment Donut ───────────────────────────────────────
    html.Div([
        html.Div([
            CARD_STYLE and None,
            html.Div([
                section_header("Application Status by District"),
                dcc.Graph(figure=fig_district_bar(), config={"displayModeBar": False},
                          style={"height": "300px"}),
            ], style=CARD_STYLE),
        ], style={"flex": "2", "minWidth": "300px"}),

        html.Div([
            html.Div([
                section_header("Payment Status Distribution"),
                dcc.Graph(figure=fig_payment_donut(), config={"displayModeBar": False},
                          style={"height": "300px"}),
            ], style=CARD_STYLE),
        ], style={"flex": "1", "minWidth": "240px"}),
    ], style={"display": "flex", "gap": "16px", "marginBottom": "16px"}),

    # ── Row 3: Monthly Trend + Category ───────────────────────────────────────────
    html.Div([
        html.Div([
            html.Div([
                section_header("Monthly Registration Trend (2024)"),
                dcc.Graph(figure=fig_monthly_trend(), config={"displayModeBar": False},
                          style={"height": "260px"}),
            ], style=CARD_STYLE),
        ], style={"flex": "1", "minWidth": "300px"}),

        html.Div([
            html.Div([
                section_header("Status by Category (General / SC / ST)"),
                dcc.Graph(figure=fig_category_bar(), config={"displayModeBar": False},
                          style={"height": "260px"}),
            ], style=CARD_STYLE),
        ], style={"flex": "1", "minWidth": "300px"}),
    ], style={"display": "flex", "gap": "16px", "marginBottom": "16px"}),

    # ── Row 4: Office Rejection Rate + Amount Distribution ─────────────────────
    html.Div([
        html.Div([
            html.Div([
                section_header("Office-wise Rejection Rate (Top 15 Offices)"),
                dcc.Graph(figure=fig_office_heatmap(), config={"displayModeBar": False},
                          style={"height": "340px"}),
            ], style=CARD_STYLE),
        ], style={"flex": "1", "minWidth": "300px"}),

        html.Div([
            html.Div([
                section_header("Disbursement Amount Distribution"),
                dcc.Graph(figure=fig_amount_dist(), config={"displayModeBar": False},
                          style={"height": "340px"}),
            ], style=CARD_STYLE),
        ], style={"flex": "1", "minWidth": "300px"}),
    ], style={"display": "flex", "gap": "16px", "marginBottom": "16px"}),

    # ── Row 5: District Summary Table ─────────────────────────────────────────
    html.Div([
        section_header("District-level Summary Table"),
        dash_table.DataTable(
            data=dist_table_data[dist_table_cols].to_dict("records"),
            columns=[{"name": c.replace("_", " "), "id": c} for c in dist_table_cols],
            **TABLE_STYLE,
            sort_action="native",
        ),
    ], style=CARD_STYLE),

    # ── Footer ────────────────────────────────────────────────────────────────
    html.Div([
        html.P("Data source: master_dataset.csv · Dashboard auto-generated · "
               "All figures in Indian numbering system",
               style={"color": C["muted"], "fontSize": "11px",
                      "textAlign": "center", "margin": "16px 0 0"}),
    ]),
])

if __name__ == "__main__":
    app.run(debug=True, port=8050)
