# DashFinance
The gif WILL play if you give it long enough, its 32 Mb large.


![alt text](https://github.com/SterlingButters/DashFinance/blob/master/Example.gif)


TODO List:
- File upload support for Orders
- Store Data
- Support for correcting entered orders; current implementation only updates
in position table based on last entry i.e. if you delete an order entry that 
isn't that last one, the position table will then be incorrect. This was done 
to avoid too many API calls which REALLY slowed things down
- Get Quotes 
- Annualized Returns
- Biggest movers
- More Pie Graphs: *Fix current pie chart pull if possible... looks funny
    - Asset Distribution 
    - Est Gain as percentage of holdings
    - Est loss as percentage of holdings
- Activity Monitoring: see Finicity API https://www.finicity.com
- Reward Monitoring: see AwardWallet API & StoCard & Wallaby Alternatives
- Place Order (RobinHood only)
- Finish Loan Calculator