# DashFinance
The gif WILL play if you give it long enough, its 32 Mb large.


![alt text](https://github.com/SterlingButters/DashFinance/blob/master/Example.gif)

or test it out on my first ever Heroku deployment:
https://dashfinance-test.herokuapp.com

# LOOKING for CONTRIBUTORS

### PreRequisites:
- [Poppler](http://macappstore.org/poppler/): For asset report pdf 

TODO List:
- Fix Heroku
- [Multi-Page App](https://dash.plot.ly/urls)
    File structure:
    ```
    - main.py
    - index.py
    - apps
       |-- __init__.py
       |-- bank-accounts.py
       |-- stock-portfolio.py
       |-- calculators.py
    ```
- `bank-accounts.py`: Institution balances, transactions, credit, etc
- `stock-portfolio.py`: Virtual portfolio & Market Research (RSS feeds, etc)
- `calculators.py`: Taxes, Mortgage/Loans, etc

- Store Data: `dcc.Store( )` prevents loading of all subsequent components in `stock-portfolio.py`

-   Wait for AlphaVantage to implement date specification for 
    data extraction which would significant reduce the time to retrieve data.
    
- Support for Sorting/Filtering all Tables

- Get Quotes (not yet implemented in https://github.com/RomelTorres/alpha_vantage) 
- Annualized Returns
- Biggest movers
- More Pie Graphs: *Fix current pie chart pull if possible... looks funny
    - Asset Distribution 
    - Est Gain as percentage of holdings
    - Est loss as percentage of holdings
- Reward Monitoring: see AwardWallet API & StoCard & Wallaby Alternatives
        
        https://awardwallet.com/api/loyalty#introduction 

- AuthLogin on `index.py`
    **Do last
