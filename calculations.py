def calculate_dcf(base_revenue, ebit_margin, depreciation_pct, capex_pct,
                  interest_pct, wc_change_pct, tax_rate, shares,
                  x_years, y_years, growth_rate_x, growth_rate_y, terminal_growth):

    if terminal_growth >= interest_pct:
        raise ValueError("❌ Terminal growth rate must be less than WACC.")

    discount_factors = [(1 + interest_pct / 100) ** year for year in range(1, y_years + 1)]
    fcf_data = []
    revenue = base_revenue
    total_pv_fcf = 0
    phase1_pv = 0
    phase2_pv = 0
    final_fcf = 0
    for year in range(1, y_years + 1):
        if year <= x_years:
            revenue *= (1 + growth_rate_x / 100)
        else:
            revenue *= (1 + growth_rate_y / 100)
        ebit = revenue * (ebit_margin / 100)
        tax = ebit * (tax_rate / 100)
        dep = revenue * (depreciation_pct / 100)
        capex = revenue * (capex_pct / 100)
        wc = revenue * (wc_change_pct / 100)
        fcf = ebit - tax + dep - capex - wc
        pv_fcf = fcf / ((1 + interest_pct / 100) ** year)
        total_pv_fcf += pv_fcf
        if year <= x_years:
            phase1_pv += pv_fcf
        else:
            phase2_pv += pv_fcf

    final_fcf = fcf
    pv_terminal, terminal_val = calculate_terminal_value(final_fcf, terminal_growth, interest_pct, y_years)
    ev = total_pv_fcf + pv_terminal    
    fv_per_share = ev / shares if shares else 0
    terminal_weight = pv_terminal / ev * 100 if ev else 0
    return fv_per_share, terminal_weight, phase1_pv, phase2_pv, pv_terminal


def dcf_fair_value(base_revenue, ebit_margin, depreciation_pct, capex_pct,
    wc_change_pct, tax_rate, interest_pct, shares,
    x_years, y_years, growth_rate_x, growth_rate_y, terminal_growth):

    if terminal_growth >= interest_pct:
        raise ValueError("❌ Terminal growth rate must be less than WACC.")

    revenue = base_revenue
    total_pv_fcf = 0
    phase1_pv = 0
    phase2_pv = 0

    for year in range(1, y_years + 1):
        if year <= x_years:
            revenue *= (1 + growth_rate_x / 100)
        else:
            revenue *= (1 + growth_rate_y / 100)

        ebit = revenue * (ebit_margin / 100)
        depreciation = revenue * (depreciation_pct / 100)
        tax = ebit * (tax_rate / 100)
        net_op_pat = ebit - tax
        capex = revenue * (capex_pct / 100)
        wc_change = revenue * (wc_change_pct / 100)
        fcf = net_op_pat + depreciation - capex - wc_change
        pv_fcf = fcf / ((1 + interest_pct / 100) ** year)

        total_pv_fcf += pv_fcf
        if year <= x_years:
            phase1_pv += pv_fcf
        else:
            phase2_pv += pv_fcf

    final_fcf = fcf
    terminal_value = (final_fcf * (1 + terminal_growth / 100)) / ((interest_pct / 100) - (terminal_growth / 100))
    pv_terminal = terminal_value / ((1 + interest_pct / 100) ** y_years)
    enterprise_value = total_pv_fcf + pv_terminal
    equity_value = enterprise_value
    fv_per_share = equity_value / shares if shares else 0
    terminal_weight = (pv_terminal / enterprise_value) * 100 if enterprise_value else 0

    return fv_per_share, terminal_weight, phase1_pv, phase2_pv, pv_terminal
