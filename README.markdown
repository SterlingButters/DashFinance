# DashFinance
This project serves as a showcase for several software development resources optimal 
for financial evaluation. The resources include the AlphaVantage API, Plaid API, and 
Plot.ly Dash framework which the structure upon which the app operates. For now, and 
until feedback is given that suggests the app is of use to an audience, I am going to 
shift focus to developing Dash components that will provide a much friendlier UI with a 
professional feel. 

Test it out on my first ever Heroku deployment:
https://dash-finance.herokuapp.com

- Heroku App 
Heroku hints:
    ```
    $ git push heroku master # deploy code to heroku
    $ heroku ps:scale web=1  # run the app with a 1 heroku "dyno"
    $ git push heroku master
    ```
    File structure:
    ```
    - main.py
    - app.py
    - apps
       |-- __init__.py
       |-- bank_accounts.py
       |-- market_research.py
       |-- virtual_portfolio.py
       |-- calculators.py
    ```
- `bank-accounts.py`: Institution balances, transactions, credit, etc
- `market_research.py`: Plots of Tickers
- `virtual-portfolio.py`: Virtual portfolio & Market Research (RSS feeds, etc)
- `calculators.py`: Taxes, Mortgage/Loans, etc

# LOOKING for CONTRIBUTORS

### PreRequisites:
- [Poppler](http://macappstore.org/poppler/): For asset report pdf 

### Known Issues
- Heroku Virtual Portfolio app does not make an evaluation. The reason for this 
is presumed to be caused by the lag of the callback which depends on retrieving
an unnecessarily large amount of data which heroku eventually recognizes as a 
request timeout. However, if you run `main.py` locally, this will not be an issue.

## TODO List:
- Support for Sorting/Filtering all Tables
- Styling Everywhere

- `main.py`: AuthLogin and pretty home page w/ RSS Market Feed Component
- `calculators.py`: Loan parameters + Amortization Schedule in DashTable
    https://www.bankrate.com/calculators/mortgages/loan-calculator.aspx
- `bank_accounts.py`: 
- `market_research.py`: Rest of tech-indicators, sector performance
- `virtual_portfolio`: 
    - Focus x-axis to only contain meaningful values 
    - Would like to get review/feedback on `virtual_portfolio` or do a complete code rewrite. Logic is 
    a bit confusing and results were obtained abstractly (by opinion)

- `market_research.py` & `virtual_portfolio.py`  
    - Wait for AlphaVantage to implement date specification for 
  data extraction which would significant reduce the time to retrieve data.
  
- `market_research.py`:
    - Wait for `get_quotes` method (not yet implemented in [AlphaVantage for python](https://github.com/RomelTorres/alpha_vantage)) 
    - Annualized Returns
    - Biggest movers
   
- More Pie Graphs: *Fix current pie chart pull if possible... looks funny
    - Asset Distribution 
    - Est Gain as percentage of holdings
    - Est loss as percentage of holdings
    
- Other: AwardWallet API & StoCard & Wallaby Alternatives

