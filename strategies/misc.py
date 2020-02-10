# MAIN #######################################################################


def get_low_risk(threshold=.99, contracts=None, export=False):
    """
    Return a DataFrame of lower-risk contract opportunities.
    """
    if contracts is None:
        contracts = get_contracts()
    low_risk = contracts[(contracts['yes'] >= threshold) |
                         (contracts['no'] >= threshold)]
    low_risk = low_risk.sort_values('dateEnd')
    low_risk = low_risk.reset_index(drop=True)
    if export:
        low_risk.to_excel(os.path.join(DESKTOP, 'low risk.xlsx'), index=False)
    return low_risk


def get_neg_risk(contracts=None, export=False):
    """
    Return a DataFrame with negative-risk calculations.
    """
    if contracts is None:
        contracts = get_contracts()
    risk = contracts.copy()
    risk_grp = risk.groupby('marketId')
    risk['no payout'] = 1 - risk['no']
    risk['risk'] = risk_grp['no payout'].transform('sum')
    risk = risk.sort_values(['risk', 'marketId'], ascending=[False, True])
    risk = risk.reset_index(drop=True)
    if export:
        risk.to_excel(os.path.join(DESKTOP, 'negative risk.xlsx'),
                      index=False)
    return risk
