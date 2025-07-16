def calculate_dcf(base_revenue, forecast_years, ebit_margin, depreciation_pct, capex_pct,
                  interest_pct, wc_change_pct, tax_rate, shares, growth_rate_1_2,
                  growth_rate_3_4_5, growth_rate_6):

    discount_factors = [(1 + interest_pct / 100) ** year for year in range(1, forecast_years + 1)]
    fcf_data = []
    revenue = base_revenue
    ebit = base_revenue * (ebit_margin / 100)
    depreciation = base_revenue * (depreciation_pct / 100)
    tax = ebit * (tax_rate / 100)
    net_op_pat = ebit - tax
    fcf_data.append(["Year 0", base_revenue, ebit, tax, net_op_pat, depreciation, 0, 0, 0, 0])

    for year in range(1, forecast_years + 1):
        if year <= 2:
            revenue *= (1 + growth_rate_1_2 / 100)
        elif year <= 5:
            revenue *= (1 + growth_rate_3_4_5 / 100)
        else:
            revenue *= (1 + growth_rate_6 / 100)

        ebit = revenue * (ebit_margin / 100)
        depreciation = revenue * (depreciation_pct / 100)
        tax = ebit * (tax_rate / 100)
        net_op_pat = ebit - tax
        capex = revenue * (capex_pct / 100)
        wc_change = revenue * wc_change_pct / 100
        fcf = net_op_pat + depreciation - capex - wc_change
        pv_fcf = fcf / discount_factors[year - 1]
        fcf_data.append([f"Year {year}", revenue, ebit, tax, net_op_pat, depreciation, capex, wc_change, fcf, pv_fcf])

    return fcf_data


def calculate_terminal_value(fcf, g, r, n):
    tv = (fcf * (1 + g / 100)) / ((r / 100) - (g / 100))
    return tv / ((1 + r / 100) ** n), tv


def dcf_fair_value(base_revenue, forecast_years, ebit_margin, depreciation_pct, capex_pct, wc_change_pct,
    tax_rate, interest_pct, shares, growth_1_5, growth_3_5, growth_6, terminal_growth):
    revenue = base_revenue    
    total_pv_fcf = 0
    for year in range(1, forecast_years + 1):
        if year <= 2:
            revenue *= (1 + growth_1_5 / 100)
        elif year <= 5:
            revenue *= (1 + growth_3_5 / 100)
        else:
            revenue *= (1 + growth_6 / 100)
        ebit = revenue * (ebit_margin / 100)
        tax = ebit * (tax_rate / 100)
        dep = revenue * (depreciation_pct / 100)
        capex = revenue * (capex_pct / 100)
        wc = revenue * (wc_change_pct / 100)
        fcf = ebit - tax + dep - capex - wc
        pv_fcf = fcf / ((1 + interest_pct / 100) ** year)
        total_pv_fcf += pv_fcf

    final_fcf = fcf
    pv_terminal, terminal_val = calculate_terminal_value(final_fcf, terminal_growth, interest_pct, forecast_years)
    ev = total_pv_fcf + pv_terminal    
    fv_per_share = ev / shares if shares else 0
    terminal_weight = pv_terminal / ev * 100 if ev else 0
    return fv_per_share, terminal_weight
