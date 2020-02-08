import pandas as pd
psns = eng.get_positions()
mkts = psns['markets']

for m in mkts:
    m_df = pd.DataFrame(m).drop('marketContracts', axis=1)
    c_df = pd.DataFrame(m['marketContracts'])
    mc_df = pd.merge(m_df, c_df, 
                     left_index=True, right_index=True,
                     suffixes=('Market', 'Contract'))
    
# buy yes = 1
# buy no = 0
# sell no = 2
# sell yes = 3