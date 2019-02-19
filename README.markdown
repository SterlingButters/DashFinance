# DashFinance
Test it out on my first ever Heroku deployment (down rn -> working on update):
https://dash-finance.herokuapp.com

- Heroku App 
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

TODO List:
- Support for Sorting/Filtering all Tables

- `main.py`: AuthLogin and pretty home page w/ RSS Feed Component
- `calculators.py`: Everything
- `bank_accounts.py`: DatePicker for transaction history
- `virtual_portfolio`: 
    - fix x axis datetime values to string in value graph 
    - Would like to get review/feedback on `virtual_portfolio` or do a complete code rewrite. Logic is 
    a bit confusing and results were obtained abstractly (by opinion)

- `market_research.py` & `virtual_portfolio.py`  
    - Wait for AlphaVantage to implement date specification for 
  data extraction which would significant reduce the time to retrieve data.
  
- `market_research.py`:
    -   Wait for `get_quotes` method (not yet implemented in https://github.com/RomelTorres/alpha_vantage) 
    - Annualized Returns
    - Biggest movers
   
- More Pie Graphs: *Fix current pie chart pull if possible... looks funny
    - Asset Distribution 
    - Est Gain as percentage of holdings
    - Est loss as percentage of holdings
    
- Other: AwardWallet API & StoCard & Wallaby Alternatives

Initialize Heroku, add files to Git, and deploy
$ heroku create my-dash-app # change my-dash-app to a unique name
$ git add . # add all files to git
$ git commit -m 'Initial app boilerplate'
$ git push heroku master # deploy code to heroku
$ heroku ps:scale web=1  # run the app with a 1 heroku "dyno"
$ git status # view the changes
$ git add .  # add all the changes
$ git commit -m 'a description of the changes'
$ git push heroku master
