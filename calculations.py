def calculate_dcf(base_revenue, ebit_margin, depreciation_pct, capex_pct,
                  interest_pct, wc_change_pct, tax_rate, shares,
                  x_years, y_years, growth_rate_x, growth_rate_y, terminal_growth, net_debt):

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

        fcf_data.append([
            f"Year {year}", revenue, ebit, tax, ebit - tax, dep, capex, wc, fcf, pv_fcf
        ])
        total_pv_fcf += pv_fcf
        if year <= x_years:
            phase1_pv += pv_fcf
        else:
            phase2_pv += pv_fcf

    final_fcf = fcf
    terminal_val = calculate_terminal_value(final_fcf, terminal_growth, interest_pct, y_years)
    terminal_pv = terminal_value / discount_factors[-1]
    enterprise_value = total_pv_fcf + terminal_pv
    equity_value = enterprise_value - net_debt
    fair_value_per_share = equity_value / shares if shares > 0 else 0
    
    terminal_weight = pv_terminal / equity_value * 100 if equity_value else 0
    return fcf_data, fair_value_per_share, terminal_weight, phase1_pv, phase2_pv, pv_terminal, enterprise_value, equity_value 


def calculate_terminal_value(fcf, g, r, n):
    tv = (fcf * (1 + g / 100)) / ((r / 100) - (g / 100))
    return tv


