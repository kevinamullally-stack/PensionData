#!/usr/bin/env python3
"""Build the benchmark-research worklist from the Public Plans Database (PPD) source file.

Reads the raw PPD plan-level Stata file, writes:
  - data/source/ppd_plan_level_index.csv : trimmed identifying/context columns for every plan-year
  - data/worklist.csv                    : one row per plan-year needing benchmark research,
                                            with a size-based priority rank (largest plans first)

Usage:
    python3 scripts/build_worklist.py /path/to/ppd_plan_level_clean.dta
"""
import sys
import pandas as pd

INDEX_COLS = [
    "ppd_id", "PlanName", "PlanFullName", "StateAbbrev", "StateName", "GovtName",
    "PlanType", "fy", "fye", "MktAssets_net", "InvestmentReturn_1yr",
    "ActFundedRatio_GASB",
]


def main(src_path: str) -> None:
    df = pd.read_stata(src_path, convert_categoricals=False)

    index_cols = [c for c in INDEX_COLS if c in df.columns]
    index_df = df[index_cols].copy()
    index_df.to_csv("data/source/ppd_plan_level_index.csv", index=False)

    # Rank plans by their most recent reported market value of assets, largest first.
    latest_assets = (
        df.sort_values("fy")
        .groupby("ppd_id")["MktAssets_net"]
        .last()
        .rename("latest_MktAssets_net")
    )
    size_rank = latest_assets.rank(ascending=False, method="min").rename("size_rank")

    worklist = df[["ppd_id", "PlanName", "StateAbbrev", "fy"]].copy()
    worklist = worklist.merge(size_rank, left_on="ppd_id", right_index=True, how="left")
    worklist = worklist.merge(latest_assets, left_on="ppd_id", right_index=True, how="left")
    worklist["status"] = "pending"
    worklist["batch"] = ""
    worklist = worklist.sort_values(["size_rank", "ppd_id", "fy"]).reset_index(drop=True)
    worklist.to_csv("data/worklist.csv", index=False)

    print(f"Wrote data/source/ppd_plan_level_index.csv ({len(index_df)} rows)")
    print(f"Wrote data/worklist.csv ({len(worklist)} rows, {worklist['ppd_id'].nunique()} plans)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1])
