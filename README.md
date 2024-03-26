### Overview

In this project I build 2 classes that can be used to get data from a WEB API and fit the mode[ to data then predict asset volatility.

The first class can be used to get data from web API by making HTTP requests, it then transforms the data then load it into an SQLite database.

The second module is a GarchModel class that can be fitted into the data for a chosen ticker symbol and then make predictions. The 2 classes are accompanied by the server to serve predictions for the chosen ticker symbol. 
