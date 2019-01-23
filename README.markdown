# DashFinance
The gif WILL play if you give it long enough, its 32 Mb large.


![alt text](https://github.com/SterlingButters/DashFinance/blob/master/Example.gif)


TODO List:
- Store Data; `dcc.Store( )` prevents loading of all subsequent components
- AuthLogin; doesnt make sense to do until storage is implemented

- Support for correcting entered orders; current implementation only updates
in position table based on last entry i.e. if you delete an order entry that 
isn't that last one, the position table will then be incorrect. This was done 
to avoid too many API calls which REALLY slowed things down

        https://blog.rapidapi.com/best-finance-apis/
        https://rapidapi.com/collection/stock-market-apis

- Get Quotes (not yet implemented in https://github.com/RomelTorres/alpha_vantage) 
- Annualized Returns
- Biggest movers
- More Pie Graphs: *Fix current pie chart pull if possible... looks funny
    - Asset Distribution 
    - Est Gain as percentage of holdings
    - Est loss as percentage of holdings
- Activity Monitoring: see Finicity API https://www.finicity.com
- Reward Monitoring: see AwardWallet API & StoCard & Wallaby Alternatives
        
        https://awardwallet.com/api/loyalty#introduction 

- Place Order (RobinHood only)
- Finish Loan Calculator