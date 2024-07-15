# %%

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

pd.set_option("display.max_rows", 500)
pd.set_option("display.max_columns", 500)
pd.set_option("display.width", 1000)
pd.options.display.max_colwidth = 100

sns.set_style("darkgrid")

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

# %%

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

# %%

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

# %%

df["target_size_[m]"] = 1.5
df.loc[df["target_number"].isin((4, 8, 9)), "target_size_[m]"] = 2.0
df.loc[df["target_number"].isin((3, 5, 14)), "target_size_[m]"] = 2.5


# %%

# print(f"Num. products with valid points: {len(df['product_name'].unique())}")
print(f"Num. valid measurements: {len(df)}")

sns.displot(
    data=df.sort_values(by="swath"),
    x="swath",
    aspect=2,
)

sns.displot(
    data=df,
    x="target_number",
    discrete=True,
    aspect=2,
    hue="swath",
    hue_order=swath_order,
    multiple="stack",
)

sns.displot(
    data=df,
    x="peak_azimuth_time_[UTC]",
    aspect=2,
    bins=50,
    hue="swath",
    hue_order=swath_order,
    multiple="stack",
)


# %%

print("subswath, slant range localization error [m], azimuth localization error [m]")
for swath in sorted(df["swath"].unique()):
    df1 = df[df["swath"] == swath]
    print(
        "{}, {:.3f} +/- {:.3f}, {:.3f} +/- {:.3f}".format(
            swath,
            df1["slant_range_localization_error_[m]"].mean(),
            df1["slant_range_localization_error_[m]"].std(),
            df1["azimuth_localization_error_[m]"].mean(),
            df1["azimuth_localization_error_[m]"].std(),
        )
    )

print()

print("subswath, slant range localization error [m], azimuth localization error [m]")
for swath in sorted(df["swath"].unique()):
    df1 = df[df["swath"] == swath]
    print(
        "{}, {:.3f} +/- {:.3f}, {:.3f} +/- {:.3f}".format(
            swath,
            df1["revised_ale_range_[m]"].mean(),
            df1["revised_ale_range_[m]"].std(),
            df1["revised_ale_azimuth_[m]"].mean(),
            df1["revised_ale_azimuth_[m]"].std(),
        )
    )

# %%

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 6))

sns.scatterplot(
    x="target_number",
    y="scr_[dB]",
    data=df.rename(columns={"total_localization_error_[m]": "Total ALE [m]", "target_size_[m]": "Target size [m]"}),
    ax=ax,
    hue="Total ALE [m]",
    palette="mako",
    size="Target size [m]",
)
ax.axhline(y=20, color="k", alpha=0.25)
ax.set_xlabel("CR ID")
ax.set_ylabel("SCR [dB]")
ax.legend(loc="center left", bbox_to_anchor=(1, 0.5), markerscale=2)


# %%

for slant_range, azimuth, sr_label, az_label in (
    ("slant_range_localization_error_[m]", "azimuth_localization_error_[m]", "Slant range ALE [m]", "Azimuth ALE [m]"),
    ("revised_ale_range_[m]", "revised_ale_azimuth_[m]", "Slant range ALE revised [m]", "Azimuth ALE revised [m]"),
):

    g = sns.JointGrid(height=10)

    sns.scatterplot(
        x=slant_range,
        y=azimuth,
        data=df,
        ax=g.ax_joint,
        hue="swath",
        hue_order=swath_order,
        alpha=0.75,
    )
    sns.kdeplot(
        x=slant_range,
        data=df,
        ax=g.ax_marg_x,
        hue="swath",
        hue_order=swath_order,
        legend=False,
    )
    sns.kdeplot(
        y=azimuth,
        data=df,
        ax=g.ax_marg_y,
        hue="swath",
        hue_order=swath_order,
        legend=False,
    )

    g.ax_joint.set_xlabel(sr_label)
    g.ax_joint.set_ylabel(az_label)


# %%

x_axes = (
    ("peak_azimuth_time_[UTC]", "Peak azimuth time [UTC]"),
    ("target_number", "Target number"),
    ("incidence_angle_[deg]", "Incidence angle [deg]"),
)

for variable, label in (
    (
        "slant_range_localization_error_[m]",
        "Slant range ALE [m]",
    ),
    (
        "revised_ale_range_[m]",
        "Slant range ALE revised [m]",
    ),
    ("azimuth_localization_error_[m]", "Azimuth ALE [m]"),
    ("revised_ale_azimuth_[m]", "Azimuth ALE revised [m]"),
):

    for x_var, x_label in x_axes:

        g = sns.JointGrid(marginal_ticks=True)
        g.fig.set_figwidth(10)
        g.fig.set_figheight(4)
        sns.scatterplot(
            x=x_var,
            y=variable,
            data=df,
            ax=g.ax_joint,
            hue="swath",
            hue_order=swath_order,
            alpha=0.75,
        )
        sns.move_legend(g.ax_joint, "upper left", bbox_to_anchor=(1.25, 0.7))
        g.ax_marg_x.remove()
        sns.kdeplot(
            y=variable,
            data=df,
            ax=g.ax_marg_y,
            hue="swath",
            hue_order=swath_order,
            legend=False,
        )
        g.ax_joint.set_xlabel(x_label)
        g.ax_joint.set_ylabel(label)
# %%
