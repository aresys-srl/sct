# %%

from pathlib import Path

import numpy as np
import pandas as pd
import seaborn as sns

pd.set_option("display.max_rows", 500)
pd.set_option("display.max_columns", 500)
pd.set_option("display.width", 1000)
pd.set_option("display.max_colwidth", 100)

sns.set_style("darkgrid")
sns.set_context("notebook")

# %%

LINES_PER_BURST = {
    "IW1": 1497,
    "IW2": 1508,
    "IW3": 1513,
}
ROI_HALF_SIDE = 64

# %%

pta_results_path = Path(
    r"C:\ARESYS_PROJ\scripts\sct\20240417_sct_signs_etad_and_sct\S1A_IW_SLC__1SDV_20231218T084126_20231218T084153_051706_063E98_DBBD.SAFE\pert\pta_graphs\point_target_analysis_results_pert.csv"
)
df = pd.read_csv(pta_results_path, parse_dates=["peak_azimuth_time_[UTC]"])
df.drop_duplicates(inplace=True)

df["lines_per_burst"] = [LINES_PER_BURST[x] for x in df["swath"]]
# df["relative_azimuth_position"] = df["azimuth_position"] % df["lines_per_burst"]

valid_scr = df["scr_[dB]"] > 20
valid_azimuth_position = (df["peak_azimuth_from_burst_start"] > ROI_HALF_SIDE) & (
    df["peak_azimuth_from_burst_start"] < df["lines_per_burst"] - ROI_HALF_SIDE
)

print(f"{len(df)} measurements in the database")
print(f"{sum(~valid_scr)} measurements with invalid SCR, removing them")
print(f"{sum(~valid_azimuth_position)} measurements with invalid azimuth position, removing them")

df = df[valid_scr & valid_azimuth_position]

print(f"{len(df)} valid measurements remain")

df["squint_angle_[deg]"] = 180 / np.pi * df["squint_angle_[rad]"]
df["time_[days]"] = [
    (t - min(df["peak_azimuth_time_[UTC]"])).total_seconds() / 86400 for t in df["peak_azimuth_time_[UTC]"]
]
df["total_localization_error_[m]"] = np.sqrt(
    df["slant_range_localization_error_[m]"] ** 2 + df["azimuth_localization_error_[m]"] ** 2
)
df["target_number"] = [int(x[2:4]) for x in df["target_name"]]

swath_order = sorted(df["swath"].unique())


df = df[df["total_localization_error_[m]"] < 10]

df["rcs_meas_minus_theoretical_[dB]"] = df["rcs_[dB]"] - df["rcs_theoretical_[dB]"]

# %%

df["target_size_[m]"] = 1.5
df.loc[df["target_number"].isin((4, 8, 9)), "target_size_[m]"] = 2.0
df.loc[df["target_number"].isin((3, 5, 14)), "target_size_[m]"] = 2.5

# %%

x_axes = (
    ("peak_azimuth_time_[UTC]", "Peak azimuth time [UTC]"),
    ("target_number", "Target number"),
)

y_axes = (
    ("rcs_[dB]", "RCS measured [dB]"),
    ("rcs_theoretical_[dB]", "RCS theoretical [dB]"),
    ("rcs_meas_minus_theoretical_[dB]", "RCS error [dB]"),
)

for y_var, y_label in y_axes:
    for x_var, x_label in x_axes:
        sns.relplot(
            data=df.rename(columns={"swath": "Swath", "target_size_[m]": "Target size [m]"}),
            x=x_var,
            y=y_var,
            hue="Swath",
            hue_order=swath_order,
            size="Target size [m]",
            height=4,
            aspect=2,
        ).ax.set(xlabel=x_label, ylabel=y_label)


# %%

(
    "range_resolution_[m]",
    "azimuth_resolution_[m]",
    "range_pslr_[dB]",
    "azimuth_pslr_[dB]",
    "pslr_2d_[dB]",
    "range_islr_[dB]",
    "azimuth_islr_[dB]",
    "islr_2d_[dB]",
    "range_sslr_[dB]",
    "azimuth_sslr_[dB]",
    "sslr_2d_[dB]",
    "clutter_[dB]",
    "scr_[dB]",
)


for sr_var, az_var, sr_label, az_label in (
    ("range_resolution_[m]", "azimuth_resolution_[m]", "Range resolution [m]", "Azimuth resolution [m]"),
    ("range_pslr_[dB]", "azimuth_pslr_[dB]", "Range PSLR [dB]", "Azimuth PSLR [dB]"),
    ("range_islr_[dB]", "azimuth_islr_[dB]", "Range ISLR [dB]", "Azimuth ISLR [dB]"),
    ("range_sslr_[dB]", "azimuth_sslr_[dB]", "Range SSLR [dB]", "Azimuth SSLR [dB]"),
):
    g = sns.JointGrid(height=10)

    sns.scatterplot(
        x=sr_var,
        y=az_var,
        data=df,
        ax=g.ax_joint,
        hue="swath",
        hue_order=swath_order,
        alpha=0.75,
    )
    sns.kdeplot(
        x=sr_var,
        data=df,
        ax=g.ax_marg_x,
        hue="swath",
        hue_order=swath_order,
        legend=False,
    )
    sns.kdeplot(
        y=az_var,
        data=df,
        ax=g.ax_marg_y,
        hue="swath",
        hue_order=swath_order,
        legend=False,
    )
    g.ax_joint.set_xlabel(sr_label)
    g.ax_joint.set_ylabel(az_label)
# %%

g = sns.JointGrid(height=10)

sns.scatterplot(
    x="clutter_[dB]",
    y="rcs_[dB]",
    data=df,
    ax=g.ax_joint,
    hue="swath",
    hue_order=swath_order,
    size="target_size_[m]",
    alpha=0.75,
)
sns.kdeplot(
    x="clutter_[dB]",
    data=df,
    ax=g.ax_marg_x,
    hue="swath",
    hue_order=swath_order,
    legend=False,
)
sns.kdeplot(
    y="rcs_[dB]",
    data=df,
    ax=g.ax_marg_y,
    hue="swath",
    hue_order=swath_order,
    legend=False,
)
g.ax_joint.set_xlabel("Clutter [dB]")
g.ax_joint.set_ylabel("RCS [dB]")

# %%
