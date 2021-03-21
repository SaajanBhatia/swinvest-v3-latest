'''
Swinvest - Statistical Machine Learning Stock Price Forecasting with other features assisting investors
Saajan Singh Bhatia 13H1 Ilford County High School
AQA Advanced Level Coursework
<---------------------------------------------------------->
    www.swinvest.co.uk
        Demonstrator Login: 
            Username:
                teacher@swinvest.co.uk
            Password:
                Password_123
<---------------------------------------------------------->
            OBJECTIVES                                                                   Functions/ Class Line Number              Routing Line Number

1. Provide the user with a forecasted closing price using statistical and machine                   986                                     1192
    learning methods

2. Making algorithms work efficiently such as cleaning data                                         412                                     N/A

3. Provide the user with information about the stock market, such as Market Cap,                    540                                     572
    Company Short Name, Fifty Two Week High, etc

4. User Friendly Interface - easy to navigate with correct color schemes                            N/A                                     N/A

5. Interactive Graph functions with responsive display view port                                    N/A                                     N/A

6. Providing a priority queue with the news feed, allowing users to control the order               820                                     1200
    of what stocks they want to view

7. Mean Data Rolling to allow graph data to display web pages quicker (recursive)                   430                                     N/A

8. Give the user a risk evaluation using the Normal Distribution - calculates the                   1066                                    1192
    probability of returns, losses and volatility with a volatility ranking

9. Account Settings - Allow the user to change details held about them                              141                                     1245

10. Responsive HTML site for mobile, tablet and desktop application                                 N/A                                     N/A

11. Tables page - allow the users to see the front end page linking corporation names and           1269                                    N/A
    their associated ticker names
'''

#################### Libraries ####################
# Flask library for web functions
from flask import Flask, render_template, request, session, url_for, redirect, flash, jsonify
import logging
# JSON for data storage and API request handling
import json 

# Libraries used to connect to the mysql server
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import mysql.connector 
 
# Libraries required for mathematical values, data organisation and datetime object manipulation
import pandas as pd 
import numpy as np 
import math
# Date handling functions
import datetime as datetime
# Password Hashing using SHA256_Crypt
from passlib.hash import sha256_crypt
# Generates a secret key for sessions
import secrets

# Data retrieval Yahoo Finance API and formatting JSON information
import yfinance as yf 

# API handling 
from bs4 import BeautifulSoup

# Data retrieval from News API - News Scrape
from newsapi import NewsApiClient

# Environment Variables
import os
os.environ['DATABASE_PASSWORD'] = 'Password_123' ## Set to the password of local database.

# HTML Files (templates)
pageTemplates = {
    'DASHBOARD_PAGE' : 'index.html',
    'SIGN_IN_PAGE' : 'authentication-login1.html',
    'SIGN_UP_PAGE' : 'authentication-register1.html',
    'NEWS_PAGE' : 'informationFeed.html',
    '404_PAGE' : '404.html',
    'ACCOUNT_SETTINGS' : 'profile.html'
}

#Database Connection and Session Declaration
## For Local Operation keep the IP Address to the IP address of the local MYSQL Server!! 
# Development IP Address - 172.31.2.42

## Local Dev
#engine = create_engine(("mysql+pymysql://root:{}@localhost/swinvest").format(os.environ.get('DATABASE_PASSWORD')), pool_recycle=1800)

## Production Environment
engine = create_engine(("mysql+pymysql://root:{}@172.31.2.42/swinvest").format(os.environ.get('DATABASE_PASSWORD')), pool_recycle=1800)
db = scoped_session(sessionmaker(bind=engine))

#Web App (Flask) Declaration
app = Flask(__name__)

#News API Declaration
newsapi = NewsApiClient(api_key='9764ee4bef1d4af6b4a25153841b1d81')
#### API Original: fad2fac5fb7648fd8ba779d926b84499
#### API New: 9764ee4bef1d4af6b4a25153841b1d81
# The News API has a request limit, therefore there are two api_keys to switch between

#Line 100

########################################## Start of Code ##########################################

# Logging messages for server side monitoring and debugging
def log(message):
    date = ('['+datetime.datetime.today().strftime('%c')+']') ## Finds and formats date
    ipAddress = ('[' + str(request.remote_addr) + ']') ## Finds and formats user IP address
    logging.warning('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<************************************************************')
    logging.warning('* IP ADDRESS OF USER: ' + ipAddress )
    logging.warning('* DATETIME REQUESTED: ' + date)
    logging.warning('* ' + message ) 
    logging.warning('**************************************************>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')

#Redirect for Error Page (404) when session times out
@app.route('/404/<typeOfError>/')
def errorPage(typeOfError):
    if typeOfError == 'sessionExpiration':
        message='Your session has expired, please return to sign in'
    else:
        message  ='Apologies, please return to sign in'
    return render_template(pageTemplates['404_PAGE'], message=message, pageName = '404')

#This is a 404 page handler, if an invalid address is entered
@app.errorhandler(404)
def page_not_found(error):
   return render_template(pageTemplates['404_PAGE'], pageName = '404', message='Please go back or return to sign in'), 404

# Class 1 - Database Methods (no inheritance - parent class)
class databaseConnection(object):

    #Gets all usernames
    def getAllUsernames(self):
        formattedUsernames = []
        usernames = db.execute('SELECT username FROM accounts').fetchall()
        for username in usernames:
            formattedUsernames.append(username[0]) ## Correctly formats usernames from database retrieval
        return formattedUsernames

    #Sets Session FirstName
    def setSessionFirstName(self):
        session['firstName'] = db.execute('SELECT firstName FROM accounts WHERE username=:username',{
            'username' : session['username'].upper()
        }).fetchone() 
        session['firstName'] = session['firstName'][0] ## Identifies first name from db and sets Session first name

    #Sets Session LastName
    def setSessionLastName(self):
        session['lastName'] = db.execute('SELECT lastName FROM accounts WHERE username=:username',{
            'username' : session['username'].upper()
        }).fetchone()
        session['lastName'] = session['lastName'][0] ## Identifies last name from db and sets Session last name

    #Sets Session ID
    def setSessionID(self):
        session['id'] = db.execute('SELECT uid FROM accounts WHERE username=:username',{
            'username' : session['username'].upper()
        }).fetchone()
        session['id'] = session['id'][0] ## Identifies and sets session id.

    #Gets the preference ID from another table
    def getPreferenceID(self):
        #Preference ID is directly mapped to the User ID (PID=UID)
        return session['id']

    #Create Preference record when account is created
    def createPreferenceDb(self, userId):
        # The record contains all None Values and will change dynamically depening on user input
        db.execute('UPDATE preferences SET one =:one, two =:two, three =:three, four =:four, five =:five WHERE pid =:pid',{
            'one' : 'NONE',
            'two' : 'NONE',
            'three' : 'NONE',
            'four' : 'NONE',
            'five' : 'NONE',
            'pid' : userId
        })
        db.commit()

    #Updates Preference table
    def updateDbPreference(self, selections, priority):
        formatArr = [] ## Array items to be saved in db
        selections, priority = selections, priority
        while len(selections)!=5:
            selections.append('NONE')
            # Fills in the gaps where no stocks have been chosen as None
        
        for i in range(len(selections)):
            if selections[i] == 'NONE':
                formatArr.append('NONE')
            else:
                formatArr.append(self.convertToJson(selections[i],priority[i])) ## Puts the data into JSON format
        db.execute('UPDATE preferences SET one =:one, two =:two, three =:three, four =:four, five =:five WHERE pid =:pid',{
            'one' : formatArr[0],
            'two' : formatArr[1],
            'three' : formatArr[2],
            'four' : formatArr[3],
            'five' : formatArr[4],
            'pid' : session['id']
        })
        db.commit() ## Commits database changes

#Line 200

    #Read Preference table
    def readDbPreference(self):
      
        data = db.execute('SELECT one, two, three, four, five FROM preferences WHERE pid =:pid',{
            'pid' : session['id']
        }).fetchone()
        for item in data:
            
            if item != 'NONE':
                ticker, priority = self.convertFromJson(item) ## If the item read is not empty, then the data needs to be converted from JSON to a Python format
                session['selections'].append(ticker)
                session['priority'].append(priority)
        

    #Set aggregate session details
    def sessionDetails(self): 
        self.setSessionFirstName()
        self.setSessionLastName()
        self.setSessionID()
        session['selections'] = [] ## News Feed Selection array
        session['priority'] = [] ## News Feed Priority array

    #Declare Session
    def setSession(self, userDetails):
        session['username'] = userDetails['username'].upper()
        self.sessionDetails()

    #Create an account with userDetails
    def createAccount(self, userDetails):
        db.execute('INSERT INTO accounts(username, firstName, lastName, password) VALUES(:username, :firstName, :lastName, :password)',{
            'username' : userDetails['username'].upper(), ## Saves username as uppercase
            'firstName' : userDetails['firstName'].lower().capitalize(), ## Puts firstname in correct format
            'lastName' : userDetails['lastName'].lower().capitalize(), ## Puts lastname in correct format
            'password' : sha256_crypt.hash(userDetails['password']) ## Encrypts password
        })
        db.commit() ## Commits changes to database
        db.execute('INSERT INTO preferences(pid) VALUES(:pid)',{
            'pid' : db.execute('SELECT uid FROM accounts WHERE username =:username',{'username':userDetails['username'].upper()}).fetchone()[0]
        }) ## Updates the preference database with the user id (uid=pid)
        db.commit()
        
    #Confirms Sign in Of User
    def confirmSignIn(self):
        userDetails = self.getSignInFormInput()
        if userDetails['username'] == '' or userDetails['password'] == '': ## Identifies empty fields
            self.flashError('Please fill in all fields','sign-in-danger')
            return False
        elif 'username' in session: ## If the user is already signed in (data in session) on the same device
            ## The user can sign in from multiple devices and it should handle the data concurrently.
            self.flashError('The user is already signed in','sign-in-danger')
            return False
        else:
            return self.validateSignIn(userDetails) ## Validates details with database and correct properties

    #Confirms Sign Up Of User
    def confirmSignUp(self):
        userDetails = self.getSignUpFormInput()
        ## First identify empty fields
        if userDetails['username'] == '' or userDetails['firstName'] == '' or userDetails['lastName'] == '' or userDetails['password'] == '' or userDetails['confirmPassword'] == '':
            self.flashError('Please fill in all fields','sign-up-danger')
            return False
        ## Check if confirmed password is equal to the password entered
        elif userDetails['password'] != userDetails['confirmPassword']:
            self.flashError('The passwords entered do not match', 'sign-up-danger')
            return False#
        ## Checks if password is valid (has correct properties)
        elif not self.validPassword(userDetails['password']):
            self.flashError('The password provided is not strong enough', 'sign-up-danger')
            return False
        else:
            return self.validateSignUp(userDetails) ## Goes to database stage

    #Get details from HTML Form on Sign Up
    def getSignUpFormInput(self):
        userInput = {
            'username' : request.form.get('username'),
            'firstName' : request.form.get('firstName'),
            'lastName' : request.form.get('lastName'),
            'password' : request.form.get('password'),
            'confirmPassword' : request.form.get('confirmPassword')
        }
        return userInput ## returns dict with all values

    #Get details from HTML Form on Sign In
    def getSignInFormInput(self):
        userInput = {
            'username' : request.form.get('username'),
            'password' : request.form.get('password')
        }
        return userInput ## returns dict with all values

#Line 300

    #Validates User Sign In
    def validateSignIn(self, userDetails):
        usernameRequest = db.execute('SELECT username FROM accounts WHERE username=:username',{
            'username' : userDetails['username'].upper()
        }).fetchone()
        if usernameRequest == None: ## Checks if the username is in the database
            self.flashError('The account entered does not exist', 'sign-in-danger')
            return False
        else:
            passwordRequest = db.execute('SELECT password FROM accounts WHERE username=:username',{
                'username' : userDetails['username']
            }).fetchone()
            ## Verifies the user input password and the encrypted password in database
            if sha256_crypt.verify(userDetails['password'],passwordRequest[0]): 
                self.setSession(userDetails)
                return True
            else:
                self.flashError('The password entered is incorrect','sign-in-danger')
                return False

    #Validates User Sign Up
    def validateSignUp(self, userDetails):
        allUsernames = self.getAllUsernames()
        if userDetails['username'].upper() in allUsernames: 
            ## Identifies if the username is unique
            self.flashError('The account username already exists', 'sign-up-danger')
            return False
        else:
            ## Account created
            self.createAccount(userDetails)
            ## Session Declared
            self.setSession(userDetails)
            ## Preferce Record created
            self.createPreferenceDb(session['id'])
            return True

    #Validates User Password (password verification/ sanitation)
    def validPassword(self, password):
        required = ['!',"@","#","$","%","^","&","*","_","+","-","=","?","~",":","<",">"]
        valid = True
        if len(password) <=5: ## Min length 6
            valid = False
        if len(password)>=61: ## Max length 61 (db purpose)
            valid = False
        if not any(char.isdigit() for char in password): ## checks if password contains number
            valid = False
        if not any(char.isupper() for char in password): ## check if password contains an uppercase letter
            valid = False
        if not any(char.islower() for char in password): ## checks if password contains a lowercase letter
            valid = False
        if not any(char in required for char in password): ## checks if a special character from the above array is contained
            valid = False
        return valid

    #Gets HTML Form input for any element on the User Account Settings Page
    def getProfileInput(self,element):
        query = request.form.get(element)
        return query

    #Change First Name
    def changeFirstName(self):
        newFirstName = self.getProfileInput('firstName')
        db.execute('UPDATE accounts SET firstName = :newFirstName WHERE uid = :userID',{
            'newFirstName' : newFirstName,
            'userID' : session['id']
        })
        db.commit() ## changes commited
        self.setSessionFirstName()
        self.flashError('Change Made!', 'accountSettingSuccess') ## Success message displayed

    #Change Last Name
    def changeLastName(self):
        newLastName = self.getProfileInput('lastName')
        db.execute('UPDATE accounts SET lastName = :newLastName WHERE uid = :userID',{
            'newLastName' : newLastName,
            'userID' : session['id']
        })
        db.commit() ## changse commited
        self.setSessionLastName()
        self.flashError('Change Made!', 'accountSettingSuccess') ## Success message displayed

    #Change Password
    def changePassword(self):
        currentUsername = self.getProfileInput('confirmUsername')
        currentPassword = self.getProfileInput('currentPassword')
        newPassword = self.getProfileInput('newPassword')
        confirmNewPassword = self.getProfileInput('confirmNewPassword')
        if currentUsername.upper() != session['username'].upper():
            # check if username confirmation is correct
            self.flashError('The username entered does not match', 'accountSettingError')
        elif newPassword != confirmNewPassword:
            # check if new passwords match
            self.flashError('The passwords entered do not match', 'accountSettingError')
        elif not self.validPassword(newPassword):
            # checks if new password is correct
            self.flashError('The new password is not strong enough', 'accountSettingError')
        else:
            db.execute('UPDATE accounts SET password = :newPassword WHERE uid = :userID',{
                'newPassword' : sha256_crypt.hash(newPassword), ## encrypts new password
                'userID' : session['id']
            })
            db.commit() ## commits changes
            self.flashError('Password Changed!', 'accountSettingSuccess')
    
#Line 400

    #Function to flash errors or successes to the user - usually a confirmation of input/ request
    def flashError(self, message, category):
        flash(message, category)

#Class 2 - Data (parent Class)
class data(object):
    def __init__(self):
        #Error handling the attributes from other classes
        try:
            self.ticker = self.ticker
            self._tickerName = self._tickerName
        except (AttributeError, TypeError):
            self.ticker = None
            self._tickerName = None

    #Gets stock details in plain format from Yahoo Finance
    def getStock(self):
        stock = yf.Ticker(self.ticker.upper())
        return stock

    def getMean(self, arr):
        return sum(arr)/len(arr) ## Simple function to get the mean of the data
                                 ## This function is needed as there is a maximum recursion length on Python
    
    #Get Stock Data (also in plain format) from above method
    def getStockData(self):
        return self.getStock().history(period='max')
        
    #Recursive method to calculate the average of an array
    #Used Many times for formulae
    @classmethod
    def calculateAverageOfArr(self, arr):
        if len(arr) == 1:  
            return arr[0]  
        else:  
            n = len(arr)
            return ((arr[0] + (n - 1) * (self.calculateAverageOfArr(arr[1:]))) / n)
    
    #Set tickerName attribute (private)
    def setTickerName(self):
        tickerName = self.getStock().info['shortName']
        self._tickerName = tickerName

    #Function to validate whether or not the ticker request is valid
    def validateTickerSearch(self, searchRequest):
        found = False
        stock = yf.Ticker(str(searchRequest))
        ## Error handling
        try:
            stock.info['shortName']
        except (KeyError, ValueError, NameError) as error:
            found = False
        else:
            found = True
        finally:
            return found 

    #Formats the dateTime data on graphs
    def formatDateVal(self, dateTimeValue):
        return dateTimeValue.strftime("%b %Y")

    #Truncates the data to 20% (recent data) - used for functions that need recent data
    def getShortTermData(self, data):
        return data[math.ceil(0.8*(len(data))):]

    #Mathematically makes data stationary
    def cleanData(self,data):
        closeVal, dates = list(data['Close']), list(data.index)
        statData = []
        for value in closeVal:
            ## log data with base 10
            statData.append(math.log(value, 10))
        closeVal = statData
        newCv, newDates, toBeCompr = [],[],[]
        lastMonth = dates[0].month
        for i in range(len(dates)):
            if dates[i].month == lastMonth:
                toBeCompr.append(closeVal[i])
            else:
                newDates.append(dates[i])
                newCv.append(round(self.calculateAverageOfArr(toBeCompr),4))
                toBeCompr = []
                lastMonth = dates[i].month
        return {
            'newDates' : newDates,
            'newCv' : newCv
        }
        ## formatted dictionary returned

    #Mathematically returns data to unstationary format
    def unCleanData(self, df, col):
        if col == 'Close':
            length = len(df['Close'])-12
        else:
            length = len(df['Forecast'])
        for i in range(0,length):
            ## power of base
            df.loc[i,col] = 10**df.loc[i,col]
        return df

#Line 500

    #Formats Data to be read by graphing library (Candlestick/Risk Chart)
    def formatData(self):
        tickerArray = []
        for i in range(len(self.newData['Dates'])):
            tickerArray.append(
            [
                ## Data needs to rounded to two decimal places for readability
                round(self.newData['Open'][i],2),
                round(self.newData['High'][i],2),
                round(self.newData['Low'][i],2),
                round(self.newData['Close'][i],2)
            ])
        tickerNestedArray = []
        for i in range(len(self.newData['Dates'])):
            ## data has to be put in correct JSON format for graph to read the data.
            tickerNestedArray.append({
                "x":self.formatDateVal(self.newData['Dates'][i]),
                "y":tickerArray[i]
            })

        return tickerNestedArray
 
    #Formats data for graphing library (Line Chart)
    def formatDataLineGraph(self, values, dates):
        tickerArray = []
        for i in range(len(values)):
            tickerArray.append(round(values[i],4))
        tickerNestedArray = []
        for i in range(len(dates)):
            tickerNestedArray.append({
                "x":(self.formatDateVal(dates[i])),
                "y":(tickerArray[i])
            })

        return tickerNestedArray
            

#Class 3 - Dashboard Functions (inheritance from Data Class)
class dashboardFunctions(data):
    def __init__(self):
        self._timePreview = 'TWO' ## Default (initial) time preview
        super().__init__() ## Inheritance

    #Formats top shareholders Barre chart
    def formatTopShareHolders(self, shareHolders):
        nestedArr = []
        for i in range(len(shareHolders['Holder'])):
            nestedArr.append({
                "x":shareHolders['Holder'][i],
                "y":shareHolders['Shares'][i]
            })
        return nestedArr
    
    #Gets top share holder information
    def getTopShareHolders(self):
        majorHolderDf = pd.DataFrame(self.getStock().institutional_holders)
        shareHolders = {
            'Holder' : list(majorHolderDf['Holder']),
			'Shares' : list(majorHolderDf['Shares'])
        }
        return self.formatTopShareHolders(shareHolders)
    
    #Gets informaton about market from API
    def getMarketInformation(self):
        self.setTickerName()
        ## Gets the available information for the market
        info = self.getStock().info

        #Picks out the specific details of what is needed
        marketFacts = {
            'regularMarketOpen' : info['regularMarketOpen'],
            'previousClose' : info['previousClose'],
            'exchangeTimezoneName' : info['exchangeTimezoneName'],
            'fiftyTwoWeekHigh' : info['fiftyTwoWeekHigh'],
            'shortName' : info['shortName'],
            'longBusinessSummary' : info['longBusinessSummary'],
            'regularMarketVolume' : info['regularMarketVolume'],
            'marketCap' : info['marketCap'],
            'dividendRate' : info['dividendRate'],
            'industry' : info['industry'],
            'stockTickerName' : self._tickerName ## Taken from protected attr
        }
        return marketFacts

    #Updates ticker query
    def tickerSearchInput(self):
        tickerRequest = request.form.get('tickerQuery')
        self._timePreview = request.form.get('timePreview')
        session['tickerQuery'] = tickerRequest.upper()
        return session['tickerQuery']
        
    #Rolls mean over month time period    
    def rollMonthDataMean(self, data):
        prevMonth = int(data.index[0].strftime('%m'))
        toBeCompressed = {
            'Open' : [],
            'High' : [],
            'Low' : [],
            'Close' : [],
            'Dates' : []
        }
#Line 600
        for val in range(0,len(data.index.values)):
           
            if int(data.index[val].strftime('%m')) == prevMonth: ## Compares the months
                toBeCompressed['Open'].append(data['Open'][val])
                toBeCompressed['High'].append(data['High'][val])
                toBeCompressed['Low'].append(data['Low'][val])
                toBeCompressed['Close'].append(data['Close'][val])
                ## prevMonth = int(data.index[val].strftime('%m'))
            else:
               
                self.newData['Dates'].append(data.index[val])
                # Once the month changes, the averages are calculated and added to an aggregate array
                self.newData['Open'].append(self.getMean(toBeCompressed['Open']))
                self.newData['High'].append(self.getMean(toBeCompressed['High']))
                self.newData['Low'].append(self.getMean(toBeCompressed['Low']))
                self.newData['Close'].append(self.getMean(toBeCompressed['Close']))
                toBeCompressed = {
                    'Open' : [],
                    'High' : [],
                    'Low' : [],
                    'Close' : [],
                    'Dates' : []
                }
                # Updates the prev month local variable
                prevMonth = int(data.index[val].strftime('%m'))

    #Takes recent data (last 100 values) relevant to current stock price
    def recentCompression(self, data):
        data = data[len(data)-100:]
        self.newData['Open'] = list(data['Open'])
        self.newData['High'] = list(data['High'])
        self.newData['Low'] = list(data['Low'])
        self.newData['Close'] = list(data['Close'])
        self.newData['Dates'] = list(data.index)

    #Parent function for time preview
    def timePreviewSort(self, data):
        self.newData = {
            'Open' : [],
            'High' : [],
            'Low' : [],
            'Close' : [],
            'Dates' : []
        }
     
        if self._timePreview == 'ONE': ## Recent Data
            self.recentCompression(data)

        elif self._timePreview == 'TWO': ## Two year data
            self.getTwoYear(data)

        elif self._timePreview == 'THREE': ## Three year data
            self.getThreeYearData(data)

        elif self._timePreview == 'ALL': ## All data
            self.getAllData(data)

    #Gets the time range of current data
    def getTimeRangeOfData(self, data, years):
        data = data.iloc[::-1]
        mostRecentYear = int(data.index[0].strftime('%Y'))
        startYear = mostRecentYear - years
        newData = []
        while startYear != (mostRecentYear+1):
            mask = data.index.year == startYear
            newData.append(data[mask][::-1])
            startYear += 1
        return pd.concat(newData)

    #Refine month of Data
    def refineMonth(self,intervals, month):
        if intervals == int(4): ## Takes 4 intervals
            periodOne = math.ceil(len(month['Dates'])/5)
            periodTwo = math.ceil((len(month['Dates'])/5)*2)
            periodThree = math.ceil((len(month['Dates'])/5)*3)
            periodFour = math.ceil((len(month['Dates'])/5)*4)
            periodFive = len(month['Dates'])-1
            #Need to add 4th period
            self.newData['Dates'].extend((month['Dates'][periodOne], month['Dates'][periodTwo], month['Dates'][periodThree], month['Dates'][periodFour], month['Dates'][periodFive]))

            toBeCompressed = {
                'Open' : [],
                'High' : [],
                'Low' : [],
                'Close' : [],
                'Dates' : []
            }
            for j in range(0, len(month['Dates'])):
                if (j) == periodOne or (j) == periodTwo or (j) == periodThree or (j) == periodFour or (j) == periodFive:
                    ## Same method as month roller, calculates average of interval data, adds to aggregate data and updates
                    self.newData['Open'].append(self.calculateAverageOfArr(toBeCompressed['Open']))
                    self.newData['High'].append(self.calculateAverageOfArr(toBeCompressed['High']))
                    self.newData['Low'].append(self.calculateAverageOfArr(toBeCompressed['Low']))
                    self.newData['Close'].append(self.calculateAverageOfArr(toBeCompressed['Close']))
                    toBeCompressed = {
                        'Open' : [],
                        'High' : [],
                        'Low' : [],
                        'Close' : [],
                        'Dates' : []
                    }
#Line 700
                else:
                    toBeCompressed['Open'].append(month['Open'][j])
                    toBeCompressed['High'].append(month['High'][j])
                    toBeCompressed['Low'].append(month['Low'][j])
                    toBeCompressed['Close'].append(month['Close'][j])
            
        elif intervals == int(3): ## Takes 3 intervals
            periodOne = math.ceil((len(month['Dates'])/3))
            periodTwo = math.ceil((len(month['Dates'])/3)*2)
            periodThree = len(month['Dates'])-1
            self.newData['Dates'].extend((month['Dates'][periodOne], month['Dates'][periodTwo], month['Dates'][periodThree]))

            toBeCompressed = {
                'Open' : [],
                'High' : [],
                'Low' : [],
                'Close' : [],
                'Dates' : []
            }
            for j in range(0, len(month['Dates'])):
                if (j) == periodOne or (j) == periodTwo or (j) == periodThree:
                    self.newData['Open'].append(self.calculateAverageOfArr(toBeCompressed['Open']))
                    self.newData['High'].append(self.calculateAverageOfArr(toBeCompressed['High']))
                    self.newData['Low'].append(self.calculateAverageOfArr(toBeCompressed['Low']))
                    self.newData['Close'].append(self.calculateAverageOfArr(toBeCompressed['Close']))
                    toBeCompressed = {
                        'Open' : [],
                        'High' : [],
                        'Low' : [],
                        'Close' : [],
                        'Dates' : []
                    }
                else:
                    toBeCompressed['Open'].append(month['Open'][j])
                    toBeCompressed['High'].append(month['High'][j])
                    toBeCompressed['Low'].append(month['Low'][j])
                    toBeCompressed['Close'].append(month['Close'][j])


    def getTwoYear(self,data):
        data = self.getTimeRangeOfData(data, 2)
        #Gets 4 values for each month
        currMonth = int(data.index[0].strftime('%m'))
        month = {
            'Open' : [],
            'High' : [],
            'Low' : [],
            'Close' : [],
            'Dates' : []
        }
        for i in range(1,len(data.index)): ## Gets formatted data and appends
            if int(data.index[i].strftime('%m')) == currMonth:
                month['Open'].append(data['Open'][i])
                month['High'].append(data['High'][i])
                month['Low'].append(data['Low'][i])
                month['Close'].append(data['Close'][i])
                month['Dates'].append(data.index[i])
            else:
                self.refineMonth(4, month) ## interval 4
                ## Month data will reset after every round
                month = {
                    'Open' : [],
                    'High' : [],
                    'Low' : [],
                    'Close' : [],
                    'Dates' : []
                }
                currMonth = int(data.index[i].strftime('%m'))

    def getThreeYearData(self, data):
        data = self.getTimeRangeOfData(data, 3)
        #Gets 4 values for each month
        currMonth = int(data.index[0].strftime('%m'))
        month = {
            'Open' : [],
            'High' : [],
            'Low' : [],
            'Close' : [],
            'Dates' : []
        }
        for i in range(1,len(data.index)): ## Gets formatted data and appends
            if int(data.index[i].strftime('%m')) == currMonth:
                month['Open'].append(data['Open'][i])
                month['High'].append(data['High'][i])
                month['Low'].append(data['Low'][i])
                month['Close'].append(data['Close'][i])
                month['Dates'].append(data.index[i])
            else:
                self.refineMonth(3, month) ## interval 3
                ## Month data will reset after every round

                month = {
                    'Open' : [],
                    'High' : [],
                    'Low' : [],
                    'Close' : [],
                    'Dates' : []
                }
                currMonth = int(data.index[i].strftime('%m'))
#Line 800

    def getAllData(self, data):
        ## rolls monthly data for ALL data 
        self.rollMonthDataMean(data)
        


    def dashboardInput(self):
        if self.validateTickerSearch(self.tickerSearchInput()):
            self.ticker = self.tickerSearchInput() ## Gets ticker input
            self.setTickerName() ## Sets protected attr's
            self.timePreviewSort(self.getStockData()) ## Sorts the data
            return (True, self.formatData()) ## Returns valid stock and formatted data
            
        else:
            self.ticker, self._tickerName = None, None ## Remains as nothing
            return (False, None) ## Trigger invalid stock error and returns nothing


# Class news feed inherits functions from data and database connection
class newsFeedFunctions(data,databaseConnection): 
    
    def __init__(self):
        self.username = session['username'] ## sets username attr as session username
        self.id = session['id'] ## sets attr as session id
        ## Max size is 5

    @classmethod ## Allows recursion within class
    def mergeSortTwo(self,alist,blist): ## Two arrays - ticker names and priorites
        if len(alist)>1:
            mid = len(alist)//2 ## Integer division to calculate mid index
            ## This is used to determine the different halves of the merge sort
            lefthalf = alist[:mid]
            leftb = blist[:mid]
            righthalf = alist[mid:]
            rightb = blist[mid:]

            # Function called recursively to get lenth to length one.
            self.mergeSortTwo(lefthalf,leftb)
            self.mergeSortTwo(righthalf,rightb)

            # Pointers
            i=0
            j=0
            k=0
            while i < len(lefthalf) and j < len(righthalf):
                if lefthalf[i] <= righthalf[j]:
                    alist[k]=lefthalf[i]
                    blist[k]=leftb[i]
                    i=i+1
                else:
                    alist[k]=righthalf[j]
                    blist[k]=rightb[j]
                    j=j+1
                k=k+1

            while i < len(lefthalf):
                alist[k]=lefthalf[i]
                blist[k] = leftb[i]
                i=i+1
                k=k+1

            while j < len(righthalf):
                alist[k]=righthalf[j]
                blist[k] = rightb[j]
                j=j+1
                k=k+1

        return alist, blist

    def formatNewsArr(self, ticker):
        #Requesting data from the API
        topHeadlines = newsapi.get_everything(q=ticker, language='en', sort_by='relevancy') 
        headlines, links, dates = [],[],[]

        ## Takes the top 4 items
        for news in topHeadlines['articles'][0:4]:
            headlines.append(news['title'])
            dates.append(news['publishedAt'])
            links.append(news['url'])

        newDates = []
        
        ## Formats date of items
        for date in dates:
            newDate = date[0:10]
            newDate = datetime.datetime.strptime(newDate, '%Y-%m-%d')
            newDate = newDate.strftime("%A %d %b")
            newDates.append(newDate)

        newsDict = {
            'ticker' : str(ticker).upper(),
            'headlines' : headlines,
            'dates' : newDates,
            'links' : links
        }
        ## Dict containing all the data from the news feed

#Line 900

        return newsDict

    def getUserNewsInput(self):
        tickerQuery = request.form.get('tickerQueryNews').upper()
        priorityQuery = request.form.get('tickerqueryPriority')
        ## Get the ticker and priority from the front end form
        ## The front end form converts the words to values (e.g., high to 1), reducing processing and allowing faster requests.
        return tickerQuery,(int(priorityQuery)) ## Return the ticker and integer form of priority (ready for comparison and analysis)


    ## adds a news selection to the session selections and pri arrays
    def addNewsTicker(self, tickerQuery, priorityQuery):
        session['selections'].append(tickerQuery)
        session['priority'].append(priorityQuery)
       

    ## Updats the news priority
    def updateNewsPreference(self):
        self.updateDbPreference(session['selections'],session['priority'])
        session['selections'], session['priority'], session['wordPri'] = [],[], []
        # reads the database preferences
        self.readDbPreference()

    def newsFeedProtocol(self):
        session['selections'], session['priority'], session['wordPri'] = [],[],[]
        ## first reads database before triggering page request
        self.readDbPreference()
        # If the user submits a post request (i.e. enters a ticker and/or priority)
        if request.method == 'POST':

            if request.form['infoFeed'] == 'addPref': ## addpref signifies the user adding a preference
                ## Retrieve ticker and priority queury 
                tickerQuery, priorityQuery = self.getUserNewsInput()
                if len(session['selections']) == 5: ## Checks if max is reached
                    self.flashError('Too many selections, please delete a ticker and try again','newsError')
                elif not self.validateTickerSearch(tickerQuery): ## Checks for a valid ticker 
                    self.flashError('The ticker request is invalid. Please try a different ticker','newsError')
                elif tickerQuery in session['selections']: ## Checks if the ticker is already in the queue (selection)
                    self.flashError('Already exists', 'newsError')
                else:
                    self.addNewsTicker(tickerQuery, priorityQuery)
                    if len(session['selections']) != 1: ## Only mergesort if list is greater than one (increase efficiency)
                        session['priority'],session['selections'] = self.mergeSortTwo(session['priority'],session['selections'])
                    self.updateNewsPreference() ##Update the news preference
                    self.flashError('Added ' + str(tickerQuery), 'newsSuccess') ## Display Success Message

            elif request.form['infoFeed'] in session['selections']: ## User requesting to delete a stock market selection
                tickerToDelete = request.form['infoFeed'] ## Get ticker to delete
                deletedIndex = session['selections'].index(request.form['infoFeed']) ## Get index from queue
                session['selections'].remove(request.form['infoFeed']) ## Remove from selections
                session['priority'].remove(session['priority'][deletedIndex]) ## Remove from priority
                
                self.flashError('Deleted ' + str(tickerToDelete), 'newsSuccess') ## Message to alert user
                self.updateNewsPreference() ## Update database

        self.newsDataArr = [] ## If there is no post request then keep the array empty
       
        for ticker in session['selections']:
            self.newsDataArr.append(self.formatNewsArr(ticker)) ## Update the array with the session selections

        for pri in session['priority']:
            session['wordPri'].append(self.getPriority(pri)) ## Update the array with the session priorities
        session['selectionsLength'] = len(session['selections'])

    def getPriority(self, pri): ## For front end, converts the priorities into High, Medium or Low.
        if pri == 1:
            return 'High'
        elif pri == 2:
            return 'Medium'
        else:
            return 'Low'
        

    def convertFromJson(self, data): 
        ## Takes JSON data and converts into two variables (to be returned)
        x = json.loads(data)
        return x['Ticker'], int(x['Priority'])

    def convertToJson(self, ticker, pri): ##Takes dictionary and converts to JSON
        dict = {
            'Ticker' : ticker,
            'Priority' : pri 
        }
        return json.dumps(dict)
            

## Project Data Class, inherits data class
class projectData(data):
    def __init__(self, ticker):
        super().__init__() ## Inheritance
        self.ticker = ticker ## Ticker inheritance

        ## Holt Winter Method Parameters (in this case attributes/ variables - they are parameters to a formula)
        self.alpha = 0.416 
        self.beta = 0.029
        self.gamma = 0.493

#Line 1000

    def createSmoothDf(self, data):
        #Creates the initial database
        smoothDf = pd.DataFrame({
            'Close' : data['newCv'],
            'Date' : data['newDates'], ## Next items are the three different measures of the formulae
            'Trend' : 0,
            'Seasonal' : 0,
            'Base Level' : 0,
            'Forecast' : data['newCv']
        })
        return smoothDf

    ## This function is the main bulk of the formula
    def forecastHoltWinterMethod(self, smoothDf):
        for dataPoint in range(12,len(smoothDf)):
            
            ## Each equation is broken into blocks and then combined and added at the end
            l1 = self.alpha*((smoothDf.loc[dataPoint,'Close'])-(smoothDf.loc[dataPoint-12,'Seasonal']))
            l2 = (1-self.alpha)
            l3 = ((smoothDf.loc[dataPoint-1,'Base Level'])+(smoothDf.loc[dataPoint-1,'Trend']))
            smoothDf.loc[dataPoint,'Base Level'] = l1+(l2*l3)
            
            k1 = self.beta*((smoothDf.loc[dataPoint,'Base Level'])-smoothDf.loc[dataPoint-1,'Base Level'])
            k2 = (1-self.beta)
            k3 = smoothDf.loc[dataPoint-1,'Trend']
            smoothDf.loc[dataPoint, 'Trend'] = k1+(k2*k3)
            
            j1 = self.gamma*((smoothDf.loc[dataPoint,'Close'])-(smoothDf.loc[dataPoint,'Close']))
            j2 = (1-self.gamma)
            j3 = smoothDf.loc[dataPoint-12,'Seasonal']
            smoothDf.loc[dataPoint, 'Seasonal'] = j1+(j2*j3)

        return smoothDf


    ## Formula to forecast data from processing above
    def forecastData(self, smoothDf):
        mProj = 12
        tProj = len(smoothDf)-1
        sProj = 12
        for i in range(1, mProj+1):
            s1 = smoothDf.loc[tProj,'Base Level']
            s2 = smoothDf.loc[tProj,'Trend'] * i
            s3 = smoothDf.loc[tProj+i-sProj,'Seasonal']
            smoothDf.loc[tProj+i,'Forecast'] = s1+s2+s3
        return smoothDf
    
    ## Function for generating future dates
    def generateDates(self, lastDate, periods, freq):
        return list(pd.date_range(lastDate, periods=periods, freq=freq))

    def projectCloseFunction(self): ## Formula function
        smoothDf = self.createSmoothDf(self.cleanData(self.getStockData()))
        closingMean = round(smoothDf['Close'].mean(),4)
        for cell in range(0,12):
            smoothDf.loc[cell,'Seasonal'] = smoothDf.loc[cell,'Close'] - closingMean
        smoothDf.loc[11,'Base Level'] = smoothDf.loc[11,'Close'] - smoothDf.loc[11,'Seasonal']
        smoothDf = self.forecastHoltWinterMethod(smoothDf)
        smoothDf = self.forecastData(smoothDf)
        times = self.generateDates(smoothDf.loc[len(smoothDf)-13,'Date'], 12, 'M')
        for i in range(0,12):
            smoothDf.loc[len(smoothDf)-12+i,'Date'] = times[i]

        smoothDf = self.unCleanData(smoothDf,'Close')
        smoothDf = self.unCleanData(smoothDf,'Forecast')
        return smoothDf

        

## Class to project Risk (inherits from data class)
class projectRisk(data):
    def __init__(self, ticker):
        super().__init__()
        self.ticker = ticker
        # Ranking Range for volatility percentage
        self.volatilityRange = {
            'Low' : 20,
            'Medium' : 80,
            'High' : 100
        }
        

    ## Subroutine for Normal Distribution
    def normalDist(self,x, comparison):
        z = (x - self.mean)/self.std
        a = 0.647-(0.021*(z))
        mod = 1 - (np.e**( (-1)*(a)*(z**2) ))
        if comparison == 'GREATER': ## If on the other side of the distribution it is dealt differently
            val = (1-(0.5*(1+math.sqrt(mod)))) 
        else:
            val = (0.5*(1+math.sqrt(mod)))
        return round(val*100,2)

    ## Function for finding the differences between data points
    def getDifferencesArr(self, data):
        differences = []
        for i in range(1, len(data)-1):
            diff = data[i]-data[i-1]
            differences.append(diff**2) ## The datapoints are squared to eliminate all negative values
        return differences
#Line 1100

            
    def getStd(self,arr): ### Get Standard Deviation
        total = []
        for value in arr:
            total.append( (value-self.mean)**2 )
        mod = sum(total)/len(total)
        return math.sqrt(mod) ## Square Root
            
        
    def projectRiskFunction(self): ## Main Function
        data = self.getShortTermData(self.getStockData()) 
        differences = self.getDifferencesArr(list(data['Close']))
        self.lengthOfDiff = len(differences)
        self.mean = self.getMean(differences) # Get mean of data
        self.std = self.getStd(differences) # Get std of data

        self.volatility = self.normalDist(3, 'GREATER') * 2 ## Get volatility
        self.returnAtPoint5 = self.normalDist(0.5, 'GREATER') * 2 ## Get Probability of return at 0.5%
        self.returnAt3 = self.normalDist(3,'GREATER') ## Get Probability of return at 3%
        self.lossAtPoint5 = self.normalDist(0.5,'LESS') ## Get Probability of loss at 0.5% 


        ## Categorise the volatility percentage depending on the attr rates
        if self.volatility < self.volatilityRange['High']:
            if self.volatility < self.volatilityRange['Medium']:
                if self.volatility < self.volatilityRange['Low']:
                    self.volatilityRating = 'Low'
                else:
                    self.volatilityRating = 'Medium'
            else:
                self.volatilityRating = 'High'
        else:
            self.volatilityRating = 'Dangerous'

######################################################## Start Routing ##########################################

#API 1 - get all data closing price
@app.route('/data', methods=['GET','POST'])
def getData():
    currentUser = dashboardFunctions()
    valid, data = currentUser.dashboardInput()
    if valid: 
        log('-- USER REQUESTED DATA ON: ' + str(currentUser.ticker))
        return jsonify(success=1, data=data)
    else:
        return jsonify(success=0, error_msg=str('The market does not exist.'))

#API 2 - get the market facts and top shareholders
@app.route('/marketData', methods=['GET','POST'])
def getMarketData():
    currentUser = dashboardFunctions()
    if session['tickerQuery']:
        currentUser.ticker = session['tickerQuery']
        marketData = {
            'topShareHolders' : currentUser.getTopShareHolders(),
            'marketFacts' : currentUser.getMarketInformation(),
        }
        return jsonify(marketData)
    else:
        pass

#API 3 - get projected risk data
@app.route('/projectionData/<ticker>', methods=['GET','POST'])
def getProjectionData(ticker):
    currentUser = projectRisk(ticker)
    currentUser.projectRiskFunction()
    riskProjection = {
        'A. volatility' : currentUser.volatility,
        'B. returnAtPoint5' : currentUser.returnAtPoint5,
        'C. lossAtPoint5' : currentUser.lossAtPoint5,
        'D. returnAt3' : currentUser.returnAt3,
        'E. mean' : currentUser.mean,
        'F. std' : currentUser.std,
        'G. volaRating' : currentUser.volatilityRating
    }
    log('USER HAS REQUESTED RISK DATA')
    return jsonify(riskProjection)

#API 4 - get projected close data
@app.route('/projectionCloseData/<ticker>', methods=['GET','POST'])
def getProjectionCloseData(ticker):
    currentUser = projectData(ticker)  
    smoothDf = currentUser.projectCloseFunction()
    log('USER HAS REQUESTED PROJECTION DATA')
    return jsonify({
        'Close':currentUser.formatDataLineGraph(list(smoothDf['Close']),list(smoothDf['Date'][:-12])),
        'Forecast':currentUser.formatDataLineGraph(list(smoothDf['Forecast']),list(smoothDf['Date']))
    })

#Dashboard page
@app.route('/Dashboard/<firstName><lastName>/<id>', methods=['GET','POST']) ## Permalink takes first name and last name, also ID to avoid collisions
def dashboard(firstName, lastName, id):
    currentUser = dashboardFunctions() ## Instantiation
    if 'certificate' in session: ## Check if user is signed in (if data is in session)
        return render_template(pageTemplates['DASHBOARD_PAGE'], pageName='Dashboard')
    else:
        return redirect(url_for('errorPage',typeOfError = 'sessionExpiration')) ## Session Expiration, return to 404 page
#Line 1200

#News Feed (Priority Queue)
@app.route('/news', methods=['GET','POST']) ## News permalink
def news():
    if 'certificate' in session: ## Check if user is signed in
        currentUser = newsFeedFunctions()
        currentUser.newsFeedProtocol() ## Takes input and deals with functions
        return render_template(pageTemplates['NEWS_PAGE'], pageName = 'News Feed', data = currentUser.newsDataArr, length=len(currentUser.newsDataArr)) ## Return length for front end purpose
    else:
        return redirect(url_for('errorPage',typeOfError = 'sessionExpiration'))

#Sign up Page
@app.route('/sign-up', methods=['GET','POST'])
def signUp():
    if 'username' in session: ## If the user is already signed in, they can't go to the Sign up page, they are redirected to the dashboard
        return redirect(url_for('dashboard', firstName=session['firstName'], lastName=session['lastName'], id=session['id'])) 
    else:
        ## Sign in functions
        currentUser = databaseConnection()
        if request.method == 'POST':
            if currentUser.confirmSignUp():
                session['certificate'] = True ## Set Session Certificate
                session.permanent = True
                ## If no activity for 20 mins, user get signed out for security purpose
                app.permanent_session_lifetime = datetime.timedelta (minutes = 20) 
                ## Redirect to dashboard with permalink variables
                return redirect(url_for('dashboard', firstName=session['firstName'], lastName=session['lastName'], id=session['id'])) 
        return render_template(pageTemplates['SIGN_UP_PAGE'], pageName = 'Sign Up')

#Sign in Page
@app.route('/', methods=['GET','POST'])
def signIn():
    if 'username' in session: ## Again, if they are signed in they shouldn't be able to go to the Sign in page
        return redirect(url_for('dashboard', firstName=session['firstName'], lastName=session['lastName'], id=session['id'])) 
    else:
        currentUser = databaseConnection()
        if request.method == 'POST':
            if currentUser.confirmSignIn():
                session['certificate'] = True ## Set Session Certificate
                log('THE USER: ' + str(session['username']) + ' HAS REQUESTED SIGN IN')
                session.permanent = True
                ## If no activity for 20 mins, user get signed out for security purpose
                app.permanent_session_lifetime = datetime.timedelta (minutes = 20)
                ## Redirect to dashboard with permalink variables
                return redirect(url_for('dashboard', firstName=session['firstName'], lastName=session['lastName'], id=session['id']))
        return render_template(pageTemplates['SIGN_IN_PAGE'], pageName = 'Sign In')

#Account Settings Page
@app.route('/profile/<firstName>-<lastName>/<id>', methods=['GET','POST'])
def profile(firstName, lastName, id):
    if 'certificate' in session:
        currentUser = databaseConnection()
        ## If the user submits a post request
        if request.method == 'POST':
            ## Change first name
            if request.form['accSettings'] == 'changeFirstName':
                currentUser.changeFirstName()
            ## Change last name    
            if request.form['accSettings'] == 'changeLastName':
                currentUser.changeLastName()
            ## Change password
            if request.form['accSettings'] == 'changePassword':
                currentUser.changePassword()
        
        return render_template(pageTemplates['ACCOUNT_SETTINGS'], pageName='Account Settings')
    else:
        ## If they are not logged in, return for 404 page
        return redirect(url_for('errorPage', typeOfError = 'sessionExpiration'))

## Shows the user the ticker names for some common stocks
@app.route('/tableData')
def tableData():
    if 'certificate' in session: ## Verify they are signed in to the application
        return render_template('dataTable.html', pageName='Tables') ## Simple front end page, no backend function needed
    else:
        ## Return to 404 page if they are not signed in
        return redirect(url_for('errorPage',typeOfError = 'sessionExpiration'))

@app.route('/about')
def about(): ## About Page
    ## Verify user is signed in
    if 'certificate' in session:
        return render_template('about.html', pageName="About Swinvest") ## Simple front end page, no backend function needed
    else:
        return redirect(url_for('errorPage',typeOfError = 'sessionExpiration'))
    
#Signs the User out
@app.route('/sign-out')
def signOut():
    ## Clear all session variables and cookies (takes username and certificate out of session)
    session.clear()
    ## Return to sign in page (landing page)
    return redirect('/')

#Line 1300

app.config['SQLALCHEMY_POOL_RECYCLE'] = 28000 - 1

if __name__ == '__main__':
	## A secret key is required for sessions. This is generated randomly using the secrets library
    app.secret_key= secrets.token_hex(16)
    ## Allow debug page for test purposes however set to false for production purposes
    app.debug = True
	## Web Application - Running on port 8090 local host (0.0.0.0:8090)
    app.run(port=8090, threaded=True, host='0.0.0.0')

    
########################################## End of Code ##########################################
