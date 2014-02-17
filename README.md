Stock Miner
===========

A Python script that can download historical stock data, 10-K &  10-Q filings,
and simulate intraday data.

# Introduction

This python script was used to download and simulate the data for the [Bridge
Jump Portfolio Management game](http://jump.bridge-usa.com).

Please feel free to request any features.  Code contributions are always welcome!

# Mirrors
[Bitbucket](https://bitbucket.org/bridge-usa/financier) |
[Github](https://github.com/bridge-usa/financier)

# Installation
```
$ git clone https://github.com/bridge-usa/financier.git
```

Included with the Python script are four example configuration files.

# Methodology

## Historical Stock Data
When looking for historical stock data, the script first looks at Yahoo Finance
data for the stock.  If that fails, it turns to Google Finance.  The data is then
saved as a CSV.

## Intraday Data
Intraday data is crudely randomized by taking the standard deviation of all the
returns and creating a variance out of that data.  The data is then applied to
create ticks that create some kind of a curve between the opening and closing for
each day.

## Filings
Filings are scraped directly from http://www.sec.gov.  The script first tries to
find documents by using the stock ticker.  If this fails, it uses the company name
to identify a (hopefully) matching CIK.  The documents are then located using CIK.

# Usage
```
$ python stock-miner.py
```

The script will then walk you through the steps for loading the list of stocks
to download data about, as well as "cleaning" the list and repairing old data.

All files are downloaded to a `DATA` directory and sorted into the subdirectories
`Historical`, `Daily`, `Intraday`, `Filings`.

## Flags
Before downloading, there are several flags that can be used to customize the
data mining:

* `-f` - Download 10-K & 10-Q filings.
* `-h` - Download specific historical dates.
* `-d` - Download a range of daily data.
* `-i` - Simulate intraday data from the daily data.

## Hard Coded Configuration
__GOAL:__ I hope to take out this hard coded configuration, and replace it with
its own configuration file.

### mine()
In the method `mine()` are three configuration variables:

#### date
The `date` dictionary determines the duration for which Daily data will be downloaded.
This will also affect the duration of the Intraday data.

The default `date` configuration:
```python
date = {
    'startDay'   : 1,
    'startMonth' : 9,
    'startYear'  : 1997,
    'endDay'     : 30,
    'endMonth'   : 11,
    'endYear'    : 1997
}
```

The keys in `date` correspond to the following range:

`startYear`-`startMonth`-`startDay` to `endDay`-`endMonth`-`endYear`

1997-09-01 to 1997-11-30

#### history
The `history` list is simply a list of historical dates that should be downloaded
as well as the dates in the `date` range.  Each date should be a dictionary
with `day`, `month`, and `year` keys.

The default `history` configuration:
```python
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
```

#### filing
The `filing` string should be the threshold date for finding 10-Ks and 10-Qs.
The formate should be "YYYYMMDD". Documents filed after this date will not be
downloaded.

The default `filing` configuration:
```python
filing = "19970901";
```

### censor(_String_ f);
In the method `censor()` is a regex substitution that replaces any designated
year format with "[YR]".

The default `censor()` configuration:
```python
def censor(f):
    return re.sub(r'19\d\d', '[YR'], f)
```

## Configuration Files

### stock-list.txt
This text file should include the tickers for any stocks you wish to download
information about.  Tickers should be separated by a carriage return (\r).  The
tickers should be in the same order as the company names in `name-list.txt`.

### name-list.txt
This file includes the list of official registered names for the companies.
The list should be in the same order as the ticker symbols in `stock-list.txt`.

### rep-list.txt
When pulling stocks from Bloomberg Terminals, stocks that no longer exist have
random ID numbers as opposed to their original tickers.  Include those ID numbers
in this list to be replaced with the old tickers.  This list should be in the
same order as the ticker symbols in `fix-list.txt`.

### fix-list.txt
This list should contain old stock tickers for no longer existing companies.  The
order of stock tickers should be in the same order as the ID numbers in
`rep-list.txt`.
