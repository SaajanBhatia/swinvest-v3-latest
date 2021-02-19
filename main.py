#################### Libraries ####################
from flask import Flask, render_template, request, session, logging, url_for, redirect, flash
import json 

# Libraries used to connect to the mysql server
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import mysql.connector 
 
# Libraries required for mathematical values, data organisation and datetime object manipulation
import pandas as pd 
import numpy as np 
import datetime
import math

#Password Hashing using SHA256_Crypt
from passlib.hash import sha256_crypt
import secrets

#Data retrieval Yahoo Finance API and formatting JSON information
import yfinance as yf 
from bs4 import BeautifulSoup

#Data retrieval from News API - News Scrape
from newsapi import NewsApiClient

#Environment Variables
import os
os.environ['DATABASE_PASSWORD'] = 'Password_123'


#################### Database Connection ####################
engine = create_engine(("mysql+pymysql://root:{}@localhost/swinvest").format(os.environ.get('DATABASE_PASSWORD')))
db = scoped_session(sessionmaker(bind=engine))

#################### Flask Web App Configuration ####################
app = Flask(__name__)


#################### News API Configuration ####################
newsapi = NewsApiClient(api_key='fad2fac5fb7648fd8ba779d926b84499')

def log(message):
    date = (datetime.datetime.today().strftime('%c'))
    ipAddress = (request.remote_addr)
    print(str('[') + str(date) + str(']') + str(' : ') + str('[') + ipAddress + str(']') + str(' : ') + str(message))

class Data(object):
    def __init__(self):
        self.ticker = None
        self._tickerName = None

    def setDefault(self):
        self.ticker = 'AMZN'
        self._tickerName = 'Amazon.com, Inc.'

    def getStock(self):
        stock = yf.Ticker(self.ticker.upper())
        return stock

    def getTickerName(self):
        return self.getStock().info['shortName']

    def formatDatestoString(self, dates):
        newDate = []
        for date in dates:
            newDate.append(date.strftime('"%b, %Y"'))
        return newDate

    def getCloseData(self):
        df = pd.DataFrame(self.getStock().history(period='max'))
        closeValues, closeDates = self.rollMean(list(df['Close']), list(df.index))
        #Format dates
        closeDates = self.formatDatestoString(closeDates)
        return closeValues, closeDates

    def getTopShareHolderData(self):
        topHolderDataFrame = pd.DataFrame(self.getStock().institutional_holders)
        holderDict = {
            'HOLDERS' : list(topHolderDataFrame['Holder']),
            'SHARES' : list(topHolderDataFrame['Shares'])
        }
        return holderDict

    def getStockInformation(self):
        marketInformation = {
		'regularMarketOpen' : self.getStock().info['regularMarketOpen'],
		'previousClose' : self.getStock().info['previousClose'],
		'exchangeTimezoneName' : self.getStock().info['exchangeTimezoneName'],
		'fiftyTwoWeekHigh' : self.getStock().info['fiftyTwoWeekHigh'],
		'shortName' : self.getStock().info['shortName'],
		'longBusinessSummary' : self.getStock().info['longBusinessSummary']
        }
        return (marketInformation)

    def rollMean(self, closeValues, closeDates):
        prevMonth = closeDates[0].strftime('%m')
        newCloseValues, newDateValues = [],[]
        toBeCompressed = []
        for val in range(1,len(closeValues)):
            if closeDates[val].strftime('%m') == prevMonth:
                toBeCompressed.append(closeValues[val])
                prevMonth = closeDates[val].strftime('%m')
            else:
                newDateValues.append(closeDates[val])
                newCloseValues.append(self.calculateAverageOfArr(toBeCompressed))
                toBeCompressed, prevMonth = [], closeDates[val].strftime('%m')
        return newCloseValues, newDateValues    

    @classmethod
    def calculateAverageOfArr(self, arr):
        if len(arr) == 1:  
            return arr[0]  
        else:  
            n = len(arr)
            return ((arr[0] + (n - 1) * (self.calculateAverageOfArr(arr[1:]))) / n  )




class Dashboard(Data):
    def requestTickers(self, searchRequest):
        found = False
        stock = yf.Ticker(str(searchRequest))
        try:
            stock.info['shortName']
        except (KeyError, ValueError, NameError) as error:
            found = False
        else:
            found = True
        finally:
            return found

    def tickerFormInput(self):
        return str(request.form.get('tickerQuery'))

    @app.route('/dashboard-data')
    def dashboardInput(self):
        valid = self.requestTickers(self.tickerFormInput())
        if valid:
            #Change the ticker info, and get data
            self.ticker = self.tickerFormInput().upper()
            log('TICKER REQUESTED: ' + self.ticker)
            self._tickerName = self.getTickerName()
            log('THE USER HAS REQUESTED ' + self._tickerName)

            #Close Price data
            self.closeValues, self.closeDates = self.getCloseData()
            log('CLOSE VALUES AND CORRESPONDING DATES RETRIEVED')
            
            #Top Shareholders
            self.holderDict = self.getTopShareHolderData()
            log('SHAREHOLDER DATA RETRIEVED')
            #Get Market Info
            self.marketInfoDict = self.getStockInformation()
            log('MARKET INFO RETRIEVED')

            #The data now needs to go to JSON form
            data = {
                'closeValues' : (self.closeValues),
                'closeDates' : (self.closeDates),
                'holderDict' : (self.holderDict),
                'marketInfoDict' : (self.marketInfoDict)
            }
            return (data)            
        else:
            #Return an error statement to the user, and reset the tickers to the default
            self.setDefault()        
            log('USER HAS ENTERED INVALID STOCK MARKET')
            flash('Invalid Stock Market','danger')
        
    def getTimePeriod(self):
        pass

    def truncateData(self, timePeriod):
        pass

    

class DatabaseRetrieval(Data):
    def getCurrentPreferences(self):
        pass

    def addPreference(self, newTicker, newPriority):
        pass

    def deletePreference(self, oldTicker, newPriority):
        pass

    def changePassword(self,newPassword):
        pass

    def getUserID(self):
        userID = db.execute('SELECT uid FROM accounts WHERE username=:username',{
            'username' : self.username
        }).fetchone()
        return userID

    def getPreferenceID(self):
        pass

    def getFirstName(self):
        firstName = db.execute('SELECT firstName FROM accounts WHERE username=:username',{
            'username' : self.username
        }).fetchone()
        return firstName

    def getLastName(self):
        lastName = db.execute('SELECT lastName FROM accounts WHERE username=:username',{
            'username' : self.username
        }).fetchone()
        return lastName

    def encryptPassword(self, password):
        return sha256_crypt.encrypt(str(password))

    def createAccount(self):
        userDetails = self.getSignUpFormInput()
        db.execute('INSERT INTO accounts(username, firstName, lastName, password) VALUES(:username,:firstName,:lastName,:password)',{
            'username' : userDetails['username'].upper(),
            'firstName' : userDetails['firstName'].lower().capitalize(),
            'lastName' : userDetails['lastName'].lower().capitalize(),
            'password' : self.encryptPassword(userDetails['password'])
        })
        db.commit()

    def validateLogin(self, username, password):
        allUsernames = self.getAllUsernames()
        print ('na ' + str(username))
        print (allUsernames)
        if username.upper() in allUsernames:
            passwordRequest = db.execute('SELECT password FROM accounts WHERE username=:username',{
                'username' : username.upper()
            }).fetchone()
            print (password)
            print (passwordRequest[0])
            if sha256_crypt.verify(password, passwordRequest[0]):
                return True
            else:
                self.flashError('Password entered is incorrect')
                return False
        else:
            self.flashError('Username entered is incorrect')
            return False

    def getAllUsernames(self):
        formattedUsernames = []
        usernames = db.execute('SELECT username FROM accounts').fetchall()
        for username in usernames:
            formattedUsernames.append(username[0])
        return formattedUsernames

    def getLoginFormInput(self):
        accountDetails = {
            'username' : request.form.get('username').upper(),
            'password' : request.form.get('password')
        }
        return accountDetails
    
    def confirmLogin(self):
        accountDetails = self.getLoginFormInput()
        print(accountDetails['username'])
        if accountDetails['username'] == '':
            self.flashError('Please fill in all the fields.')
            return False
        elif accountDetails['password'] == '':
            self.flashError('Please fill in all the fields.')
            return False
        if self.validateLogin(accountDetails['username'], accountDetails['password']):
            self.username = accountDetails['username'].upper()
            return True
       

    def strongPasswordCheck(self, password):
        required = ['!',"@","#","$","%","^","&","*","_","+","-","=","?","~",":","<",">"]
        valid = True
        if len(password) <=5:
            valid = False
        if len(password)>=61:
            valid = False
        if not any(char.isdigit() for char in password): 
            valid = False
        if not any(char.isupper() for char in password):
            valid = False
        if not any(char.islower() for char in password):
            valid = False
        if not any(char in required for char in password): 
            valid = False
        return valid

    def getSignUpFormInput(self):        
        userDetails = {
            'username' : request.form.get('username').upper(),
            'firstName' : request.form.get('firstName'),
            'lastName' : request.form.get('lastName'),
            'password' : request.form.get('password'),
            'confirmPassword' : request.form.get('confirmPassword')
        }
        print(userDetails['username'])
        return userDetails

    def confirmSignUp(self):
        userDetails = self.getSignUpFormInput()
        if userDetails['username'] == '' or userDetails['firstName'] == '' or userDetails['lastName'] == '' or userDetails['password'] == '':
            self.flashError('Please fill in all the fields.')
            return False
        if userDetails['confirmPassword'] != userDetails['password']:
            self.flashError('The passwords provided do not match.')
            return False
        elif not self.strongPasswordCheck(userDetails['password']):
            self.flashError('The password entered is not strong enough.')
            return False
        elif userDetails['username'].upper() in self.getAllUsernames():
            self.flashError('The account username already exists.')
            return False
        else:
            self.createAccount()
            return True
        
    def flashError(self, message):
        flash(message, 'sign_error')

    
class Projection(Data):
    def __init__(self,ticker,tickerName,timePeriod):
        super().__init__(self, ticker, tickerName)
        self.ticker = ticker
        self._tickerName = tickerName
        self._timePeriod = timePeriod

class Risk(Data):
    def __init__(self,ticker, tickerName):
        super().__init__(self, ticker, tickerName)
        self.ticker = ticker
        self._tickerName = tickerName

class News(Data):
    def __init__(self):
        super().__init__(self)
        self.ticker_arr = []
        self.tickerName_arr = []



#################### Web App ####################
@app.route('/layout')
def layout():
	return render_template('layout.html', pageName = 'Layout - Debug Page')


@app.route('/dashboard', methods = ['GET','POST'])
def dash():
    if session['SET']: 
        #Instantiation for the Dashboard class
        session = Dashboard()
        if session.ticker == None:
            session.setDefault()
        #If the user has entered information 
        if request.method == 'POST':
            #Method to process input
            session.dashboardInput()
            return render_template('index.html', pageName = 'Dashboard', session = session)
        return render_template('index.html',pageName = 'Dashboard', session = session)
    else:
        return ('Go Back')
    
@app.route('/', methods = ['GET','POST'])
def login():
    session = DatabaseRetrieval()
    if request.method == 'POST':
        if session.confirmLogin():
            return render_template('index.html',pageName = 'Dashboard', session = session)
    return render_template('authentication-login1.html', pageName = 'Sign In', session = session)

@app.route('/sign-up', methods = ['GET','POST'])
def register():
    session = DatabaseRetrieval()
    if request.method == 'POST':
        if session.confirmSignUp():
            return render_template('index.html',pageName = 'Dashboard', session = session)
    return render_template('authentication-register1.html', pageName = 'Sign Up', session = session)

@app.route('/sign-out')
def signOut():
	session.clear()
	return redirect('/')


#################### Run the application ####################
if __name__ == '__main__':

	#A secret key is required for sessions. This is generated randomly using the secrets library
    app.secret_key= secrets.token_hex(16)
    app.debug = True

	#Web Application - Running on port 7358
    app.run(port=7358, threaded=True)


