## Swinvest V3
Welcome to Swinvest, a site dedicated to aiding financial institutions upon decisions made in trading. 

Main features of Swinvest include;
- Forecasting the Closing Price of NASDAQ Markets
- Live News Feed with Priority Integration
- Risk Evaluation 
- Graphical features of past data
- Analysis of top Share Holders

Please check out the site;
https://www.swinvest.co.uk/

# How to Deploy locally
1. Download the pip requirements
```
## Python 2
pip install -r requirements.txt

## Python 3 (recommended)
pip3 install -r requirements.txt 
```

2. Set up the local MySQL Server
Make sure a MySQL Server is running on port 3306. Make sure the username and password have been correctly input into the python app (top of file)
Scripts for setting up the MySQL database;
```
CREATE DATABASE swivnest;
CREATE TABLE `accounts` (
  `uid` int NOT NULL AUTO_INCREMENT,
  `username` varchar(300) DEFAULT NULL,
  `firstName` varchar(450) DEFAULT NULL,
  `lastName` varchar(450) DEFAULT NULL,
  `password` varchar(700) DEFAULT NULL,
  PRIMARY KEY (`uid`)
);
CREATE TABLE `preferences` (
  `pid` int NOT NULL,
  `one` varchar(50) DEFAULT NULL,
  `two` varchar(50) DEFAULT NULL,
  `three` varchar(50) DEFAULT NULL,
  `four` varchar(50) DEFAULT NULL,
  `five` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`pid`)
);
```

3. Run the application 
```
## Python 2
python app.py

## Python 3
python3 app.py
```

4. Navigate to the correct browser IP address
By default, you should be able to navigate to '0.0.0.0:8080' ~ this depends on the config of running the app.

## How to use the application
Once an account has been made, type a ticker into the search bar and press search. To use the projection features simply press 'project' next to the correct graphs.
