# DashFinance
The gif WILL play if you give it long enough, its 32 Mb large.


![alt text](https://github.com/SterlingButters/DashFinance/blob/master/Example.gif)

or test it out on my first ever Heroku deployment:
https://dashfinance-test.herokuapp.com

### PreRequisites:
- [Poppler](http://macappstore.org/poppler/)

TODO List:
- Activity Monitoring: Plaid API; Figure out how to implement template into Dash App

- Store Data; `dcc.Store( )` prevents loading of all subsequent components
- AuthLogin; doesnt make sense to do until storage is implemented

- Support for correcting entered orders; current implementation only updates
in position table based on last entry i.e. if you delete an order entry that 
isn't that last one, the position table will then be incorrect. This was done 
to avoid too many API calls which REALLY slowed things down. Suggested solutions:
    1) Find a faster API:

            https://blog.rapidapi.com/best-finance-apis/
            https://rapidapi.com/collection/stock-market-apis
    
    2) Wait for AlphaVantage to implement date specification for 
    data extraction which would significant reduce the time to retreive data.
    
    3) Timestamped cell selection in Dash_Table
        

- Get Quotes (not yet implemented in https://github.com/RomelTorres/alpha_vantage) 
- Annualized Returns
- Biggest movers
- More Pie Graphs: *Fix current pie chart pull if possible... looks funny
    - Asset Distribution 
    - Est Gain as percentage of holdings
    - Est loss as percentage of holdings
- Reward Monitoring: see AwardWallet API & StoCard & Wallaby Alternatives
        
        https://awardwallet.com/api/loyalty#introduction 

- Place Order (RobinHood only)
- Finish Loan Calculator
