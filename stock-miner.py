import urllib
import urllib2
import httplib
import sys
import os
import time
import datetime
import calendar
import re
import csv
import math
import random
from numpy import genfromtxt

# JQuery To Get Stock Symbols
# var stockNames = "";
# $($('.jquery-tablesorter')[0]).find('td:first-child').each(function(){stockNames += "'" + $(this).text() + "', ";});

# Stock Tickers Array
stocks = genfromtxt('stock-list.txt', dtype = 'str', delimiter = '\n').tolist()
# Company Names Array
names = genfromtxt('name-list.txt', dtype = 'str', delimiter = '\n').tolist()
# Broken Stock Tickers
rep = genfromtxt('rep-list.txt', dtype = 'str', delimiter = '\n').tolist()
# Fixed Stocker Tickers
fix = genfromtxt('fix-list.txt', dtype = 'str', delimiter = '\n').tolist()

# Save Directory
directory = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'DATA/')
if not os.path.exists(directory):
    os.makedirs(directory)
    os.makedirs(directory + 'Historical')
    os.makedirs(directory + 'Daily')
    os.makedirs(directory + 'Intraday')
    os.makedirs(directory + 'Filings')
    os.makedirs(directory + 'Filings/10-K')
    os.makedirs(directory + 'Filings/10-Q')

# Remove Invalid Entries
def removeInvalid(original, name):
    # Remove Spaces
    original = [i.replace(' ', '') for i in original]

    # Collect Valid Stocks
    valid = [i for i in original if re.match("^[A-Za-z]+$", i)]

    # Collect Invalid Stocks
    invalid = [i for i in original if not re.match("^[A-Za-z]+$", i)]
    print '\n# Invalid entries removed from ' + name + ': ' + str(len(invalid))
    print '# Invalid stock symbols: ' + ', '.join(invalid)

    # Return Valid List
    return valid

# Clean Stocks
def cleanStocks():
    global stocks, addStocks, subStocks

    # Inform of Start
    print '\n# Cleaning stock list.'

    # Remove Invalid Stock Symbols
    '''for i in range(len(stocks)-1, -1, -1):
        if not re.match("^[A-Za-z]*$", stocks[i]):
            stocks.pop(i)
            names.pop(i)
        else:
            n = names[i]
            s = n.find(' ', n.find(' ') + 1)
            n = n[:s].strip()
            s = n.find('/')
            names[i] = n[:s].strip()'''
        
    # Inform of End
    print '\n# Cleaning finished.'
    
    # Wait To Continue
    if (raw_input('\n# See Clean List? (y/n): ') == 'y'):
        # Print Cleaned List
        print '\n# Clean List (' + str(len(stocks)) + '): ' + ', '.join(stocks)

    # Wait To Continue
    if (raw_input('\n# See Clean List of Names? (y/n): ') == 'y'):
        # Print Cleaned List
        print '\n# Clean Names List (' + str(len(stocks)) + '): ' + ', '.join(names)

# Standard Deviation
def stdv(x, y):
    mean = (x + y)/2
    agg = math.pow(x-mean, 2) + math.pow(y-mean, 2)
    return math.sqrt(agg)

# Create Variance
def variance(s):
    random.SystemRandom()
    return s*random.uniform(-1,1)

# Download Stocks
def download(stock, date, db, directory, intraday, ct, total, historical = False):

    if historical:
        if date['day'] > 1:
            date['startDay'] = date['day']
            date['endDay'] = date['day']
        else:
            date['startDay'] = date['day']
            date['endDay'] = date['day']
        date['startMonth'] = date['month']
        date['endMonth'] = date['month']
        date['startYear'] = date['year']
        date['endYear'] = date['year']

    # Pick the proper URL
    if db == 'yahoo':
        url = 'http://ichart.finance.yahoo.com/table.csv?s=' + stock + '&a=' + str(date['startMonth']-1) + '&b=' + str(date['startDay']) + '&c=' + str(date['startYear']) + '&d=' + str(date['endMonth']-1) + '&e=' + str(date['endDay']) + '&f=' + str(date['endYear']) + '&g=d&ignore=.csv'
    elif db == 'google':
        url = 'http://www.google.com/finance/historical?q=' + stock + '&startdate=' + str(date['startYear']) + '-' + str(date['startMonth']) + '-' + str(date['startDay']) + '&enddate=' + str(date['endYear']) + '-' + str(date['endMonth']) + '-' + str(date['endDay']) + '&output=csv'

    # Open URL
    response = urllib2.urlopen(url)
    # Download Data
    data = response.read()

    # Test Size
    if len(data) > 50:
        if not historical:
            # Write Data to CSV
            print '# (' + str(ct) + '/' + str(total) + ') Downloading Daily Data CSV.'
            path = directory + 'Daily/' + stock + '.csv'
            with open(path, 'w') as f: f.write(data)
            if intraday:
                print '# (' + str(ct) + '/' + str(total) + ') Reading Daily Data CSV.'
                ticks = []
                with open(path, 'r') as f:
                    reader = csv.reader(f)
                    s = []
                    count = 0
                    print '# (' + str(ct) + '/' + str(total) + ') Calculating Standard Deviations.'
                    for row in reader:
                        if count > 0:
                            s.append(stdv(float(row[2]), float(row[3]))/2)
                        count += 1
                    days = count
                with open(path, 'r') as f:
                    reader = csv.reader(f)
                    count = 0
                    print '# (' + str(ct) + '/' + str(total) + ') Creating Intraday Data.'
                    for row in reader:
                        if count > 0:
                            if db == 'yahoo':
                                struct = time.strptime(row[0], "%Y-%m-%d")
                            if db == 'google':
                                struct = time.strptime(row[0], "%d-%b-%y")
                            date = time.mktime(struct) * 1000
                            o = math.ceil(float(row[1])*100)/100
                            c = math.ceil(float(row[4])*100)/100
                            for i in range(days, 0, -1):
                                ms = int(math.floor(date + 23400000 * i / days))
                                if i == 0: ticks.append([ms, o])
                                elif i == days: ticks.append([ms, c])
                                else: ticks.append([ms, math.ceil((ticks[len(ticks)-1][1] + variance(s[i-i]))*100)/100])
                        count += 1
                with open(directory + 'Intraday/' + stock + '.csv', 'w') as f:
                    print '# (' + str(ct) + '/' + str(total) + ') Writing Intraday Data CSV.'
                    writer = csv.writer(f, delimiter=',')
                    writer.writerows(list(reversed(ticks)))
        else:
            print '# (' + str(ct) + '/' + str(total) + ') Downloading Historical Range Data CSV.'
            path = directory + 'temp/' + stock + '.csv'
            with open(path, 'w') as f: f.write(data)
            print '# (' + str(ct) + '/' + str(total) + ') Reading Historical Range Data CSV.'
            with open(path, 'r') as f:
                reader = csv.reader(f)
                h = []
                count = 0
                for row in reader:
                    if count > 0: h.append(row)
                    count += 1
                return h
                    
    else:
        raise Exception

# Historical Range
def downloadHistorical(stock, history, directory, count, total):
    h = []
    for date in history:
        try:
            print '# (' + str(count) + '/' + str(total) + ') Trying Yahoo.'
            for row in download(stock, date, 'yahoo', directory, False, count, total, True): h.append(row)
        except (urllib2.HTTPError, Exception):
            try:
                print '# (' + str(count) + '/' + str(total) + ') Trying Google.'
                for row in download(stock, date, 'google', directory, False, count, total, True): h.append(row)
            except (urllib2.HTTPError, Exception):
                print '# (' + str(count) + '/' + str(total) + ') Data does not exist.'

    if len(h):
        with open(directory + 'Historical/' + stock + '.csv', 'w') as f:
            print '# (' + str(count) + '/' + str(total) + ') Writing Historical Range Data CSV.'
            writer = csv.writer(f, delimiter=',')
            h.insert(0, ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close'])
            writer.writerows(h)

# Get CIK
def cik(stock, name, count, total):
    # Notify User
    print '# (' + str(count) + '/' + str(total) + ') Performing CIK Lookup for ' + stock + '. '

    # Search URL
    url = 'http://www.sec.gov/cgi-bin/cik.pl.c'
    # Post Data
    post = urllib.urlencode({ 'company' : name })
    # Search Request
    request = urllib2.Request(url, post)
    # Search Results
    data = urllib2.urlopen(request).read()

    # Number of Hits
    hStart = data.find('>', data.find('<strong>')) + 1
    hEnd = data.find('<', hStart)

    # Find the CIK
    cStart = data.find('>', data.find('<a href="browse-edgar')) + 1
    cEnd = data.find('<', cStart)

    # Return CIK
    return {'cik' : data[cStart:cEnd].strip(), 'hits' : data[hStart:hEnd].strip()}

# Censor Filings
def censor(f):
    return re.sub(r'19\d\d', '[YR]', f)

# Get 10-K and 10-Q Filings
def tenKQ(stock, name, cik, filing, directory, count, total, force = False):
    global rep, fix
    q = stock
    qType = True
    if not re.match("^[A-Za-z]*$", stock) or force:
        if len(cik):
            q = cik
            qType = False
        else:
            return { 'k' : False, 'q' : False, 'query' : False }
            
    print '# (' + str(count) + '/' + str(total) + ') Searching for Filings using ' + q + '.'
    url = 'http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=' + q + '&type=10&dateb=' + filing + '&owner=exclude&count=10'
    data = urllib2.urlopen(url).read()

    kFound = False
    kExists = data.find('10-K')
    if kExists != -1:
        kStart = data.find('<a', kExists) + 9
        kEnd = data.find('"', kStart)

        url = 'http://www.sec.gov' + data[kStart:kEnd]
        kData = urllib2.urlopen(url).read()

        kExists = kData.find('text file')
        if kExists != -1:
            kStart = kData.find('<a', kExists) + 9
            kEnd = kData.find('"', kStart)

            print '# (' + str(count) + '/' + str(total) + ') Downloading 10-K Data.'
            url = 'http://www.sec.gov' + kData[kStart:kEnd]
            try:
                kData = urllib2.urlopen(url).read()
            except httplib.IncompleteRead:
                return tenKQ(stock, name, cik, directory, count, total, force);
            name = stock
            if stock in rep: name = fix[rep.index(stock)]
            path = directory + 'Filings/10-K/' + name + '.txt'
            with open(path, 'w') as f: f.write(censor(kData))
            kFound = True

    qFound = False
    qExists = data.find('10-Q')
    if qExists != -1:
        qStart = data.find('<a', qExists) + 9
        qEnd = data.find('"', qStart)

        url = 'http://www.sec.gov' + data[qStart:qEnd]
        qData = urllib2.urlopen(url).read()

        qExists = qData.find('text file')
        if qExists != -1:
            qStart = qData.find('<a', qExists) + 9
            qEnd = qData.find('"', qStart)

            print '# (' + str(count) + '/' + str(total) + ') Downloading 10-Q Data.'
            url = 'http://www.sec.gov' + qData[qStart:qEnd]
            try:
                qData = urllib2.urlopen(url).read()
            except httplib.IncompleteRead:
                return tenKQ(stock, name, cik, directory, count, total, force);
            name = stock
            if stock in rep: name = fix[rep.index(stock)]
            path = directory + 'Filings/10-Q/' + name + '.txt'
            with open(path, 'w') as f: f.write(censor(qData))
            qFound = True

    if not kFound or not qFound:
        if not force:
            print '# (' + str(count) + '/' + str(total) + ') Query Failed.  Forcing CIK.'
            return tenKQ(stock, name, cik, directory, count, total, True)

    return { 'k' : kFound, 'q' : qFound, 'query' : qType, 'force' : force }

# Overall process for obtaining filings.
def filings(stock, name, filing, directory, count, total):
    print '\n# (' + str(count) + '/' + str(total) + ') Performing Filings Lookup for ' + stock + '. '
    query = cik(stock, name, count, total)
    c = query['cik']
    a = True
    if len(c):
        h = query['hits']
        if not h.isdigit(): h = 'Unknown'
        print '# (' + str(count) + '/' + str(total) + ') CIK: ' + query['cik'] + '. (' + h + ' Hits)'
        if not h.isdigit():
            print '# (' + str(count) + '/' + str(total) + ') CIK is QUESTIONABLE.'
            a = 'questionable'
        elif int(h) > 5:
            print '# (' + str(count) + '/' + str(total) + ') CIK is QUESTIONABLE.'
            a = 'questionable'
    else:
        print '# (' + str(count) + '/' + str(total) + ') CIK Lookup Failed. '
        a = False
    
    r = tenKQ(stock, name, c, filing, directory, count, total)
    r['certainty'] = a

    if not r['k'] and not r['q']:
        print '# (' + str(count) + '/' + str(total) + ') Query Completely Failed. '
    elif not r['k'] or not r['q']:
        print '# (' + str(count) + '/' + str(total) + ') Query Partially Failed. '

    return r


# Mine Data
def mine():
    # Grab Global Variables
    global stocks, addStocks, subStocks, directory

    # Clean Stocks
    cleanStocks()

    # Array for Successful Stocks
    found = []
    yahoo = []
    google = []
    # Array for non existing stocks
    lost = []
    # Array for failed CIK/Filing lookups
    badFilings = []
    badQFilings = []
    badKFilings = []
    uFilings = []

    # Wait To Continue
    if (raw_input('\n# Continue to downloading and creating data? (y/n): ') != 'y'):
        print '# Bye.'
        time.sleep(1)
        exit();

    # Catch Flags
    flags = raw_input('\n# Optional Flags: ')
    fFilings = False
    fHistorical = False
    fDownload = False
    fIntraday = False
    if '-f' in flags: fFilings = True
    if '-h' in flags: fHistorical = True
    if '-d' in flags: fDownload = True
    if '-i' in flags: fIntraday = True

    # Inform of Start
    print '# Starting data mining.'

    # Set Date Duration for Downloading Daily Data
    date = {
        'startDay'   : 1,
        'startMonth' : 9,
        'startYear'  : 1997,
        'endDay'     : 30,
        'endMonth'   : 11,
        'endYear'    : 1997
    }

    # Historical Date Range
    history = [
        { 'day' : 29, 'month' : 8, 'year' : 1997 },
        { 'day' : 1, 'month' : 8, 'year' : 1997 },
        { 'day' : 1, 'month' : 7, 'year' : 1997 },
        { 'day' : 2, 'month' : 6, 'year' : 1997 },
        { 'day' : 1, 'month' : 5, 'year' : 1997 },
        { 'day' : 1, 'month' : 4, 'year' : 1997 },
        { 'day' : 3, 'month' : 3, 'year' : 1997 },
        { 'day' : 3, 'month' : 2, 'year' : 1997 },
        { 'day' : 2, 'month' : 1, 'year' : 1997 },

        { 'day' : 1, 'month' : 11, 'year' : 1996 },
        { 'day' : 1, 'month' : 10, 'year' : 1996 },
        { 'day' : 3, 'month' : 9, 'year' : 1996 },

        { 'day' : 2, 'month' : 11, 'year' : 1992 },
        { 'day' : 1, 'month' : 10, 'year' : 1992 },
        { 'day' : 1, 'month' : 9, 'year' : 1992 }
    ]

    # Filings Date Threshold
    filing = "19970901"

    # Iterate through each stock
    count = 1
    total = len(stocks)
    for stock in stocks:
        l = False
        if fDownload:
            # Download CSV
            print '\n# (' + str(count) + '/' + str(total) + ') Downloading regular data for ' + stock + '. '
            try:
                print '# (' + str(count) + '/' + str(total) + ') Trying Yahoo.'
                download(stock, date, 'yahoo', directory, fIntraday, count, total)
                found.append(stock)
                yahoo.append(stock)
            except (urllib2.HTTPError, Exception):
                try:
                    print '# (' + str(count) + '/' + str(total) + ') Trying Google. '
                    download(stock, date, 'google', directory, fIntraday, count, total)
                    found.append(stock)
                    google.append(stock)
                except (urllib2.HTTPError, Exception):
                    print '# (' + str(count) + '/' + str(total) + ') Data does not exist. '
                    lost.append(stock)
                    l = True
            # Download CSV
            print '\n# (' + str(count) + '/' + str(total) + ') Downloading regular data for ' + stock + '. '

        if not l and fHistorical:
            downloadHistorical(stock, history, directory, count, total)
        if not l and fFilings:
            f = filings(stock, names[count-1], filing, directory, count, total)
            if not f['k'] and not f['q']:
                badFilings.append(stock)
            else:
                if not f['k']:
                    badKFilings.append(stock)
                if not f['q']:
                    badQFilings.append(stock)
            if not f['query'] or f['force']:
                if f['k'] and f['q']:
                    if f['certainty'] == 'questionable' or f['force']:
                        uFilings.append(stock)

        count += 1

    # Inform of End
    print '\n# End data mining.'
    # Downloads Statistics
    if fDownload:
        print '\n# Number of found stocks: ' + str(len(found))
        print '# Number of Yahoo stocks: ' + str(len(yahoo))
        print '# Number of Google stocks: ' + str(len(google))
        print '# Google stock symbols: ' + ', '.join(google)
        print '# Found stock symbols: ' + ', '.join(found)

        # Inform of Lost Stocks
        print '\n# Number of lost stocks: ' + str(len(lost))
        print '# Lost stock symbols: ' + ', '.join(lost)

    # Filings Statistics
    if fFilings:
        print '\n# Number of Both Filings Lost: ' + str(len(badFilings))
        print '# Both Lost Stock Symbols: ' + ', '.join(badFilings)
        print '\n# Number of Just 10-K Filings Lost: ' + str(len(badKFilings))
        print '# Just 10-K Lost Stock Symbols: ' + ', '.join(badKFilings)
        print '\n# Number of Just 10-Q Filings Lost: ' + str(len(badQFilings))
        print '# Just 10-Q Lost Stock Symbols: ' + ', '.join(badQFilings)
        print '\n# Number of Questionable Filings: ' + str(len(uFilings))
        print '# Questionable Stock Symbols: ' + ', '.join(uFilings)

    # Wait to Close
    print '\n'
    close = ''
    while close != 'y':
        close = raw_input('# Do you wish to quit? (y/N): ')

if __name__ == '__main__':
    print '\n**************************************************'
    print '**************************************************'
    print '***                                            ***'
    print '***   Welcome to the Bridge Stock Data Miner   ***'
    print '***         &  Intraday Data Simulator         ***'
    print '***   --------------------------------------   ***'
    print '***       Copyright Bridge USA, LLC 2013       ***'
    print '***          Author: Alexander Martin          ***'
    print '***                                            ***'
    print '**************************************************'
    print '**************************************************'
    
    # Wait To Continue
    if (raw_input('\n# Start Clean? (y/n): ') != 'y'):
        print '# Bye.'
        time.sleep(1)
        exit();
    
    # Start Mining
    mine()
