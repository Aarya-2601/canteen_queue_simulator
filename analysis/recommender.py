def generate_recommendation(comp_df, config=None):
    if comp_df is None or comp_df.empty:
        return "No simulation data available for recommendations."
    
    cost_per_staff = 300  # Rs 300 wage for lunch shift

    best_scen = comp_df["Avg Wait"].idxmin()
    base_rev = comp_df.iloc[0]["Revenue"]
    base_wait = comp_df.iloc[0]["Avg Wait"]

    text = f"Best overall scenario for wait time: '{best_scen}' ({comp_df.loc[best_scen, 'Avg Wait']} mins avg)."

    # check extra staff scenario ROI if present
    staff_scens = [s for s in comp_df.index if "Staff" in s]
    if staff_scens:
        s = staff_scens[0]
        gain = comp_df.loc[s, "Revenue"] - base_rev
        net = gain - cost_per_staff
        saved_mins = base_wait - comp_df.loc[s, "Avg Wait"]

        if net > 0:
            text += f"\n\nROI: Extra staff recovers Rs {gain:.0f} in lost sales for Rs {cost_per_staff} cost (Net: +Rs {net:.0f}/day, cuts wait by {saved_mins:.1f} mins)."
        else:
            text += f"\n\nROI: Extra staff saves {saved_mins:.1f} mins, but revenue gained (Rs {gain:.0f}) is less than labor cost (Rs {cost_per_staff})."

    return text