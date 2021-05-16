# Overview

This script is a simple tool to export detailed exchange transactions (deposits, withdrawals, fills, etc.) from a growing set of cryptocurrency exchanges in order to simplify analysis for portfolio management and tax calculations. Specifically, it creates a set of uniform comma-separated value (CSV) files which can be imported into the CoinTracking website (shameless affiliate link below):

https://cointracking.info?ref=J533603

CoinTracking is a phenomenal tool which I use daily, but it has some odd quirks when it comes to exchange imports--not to mention the fact that API-based imports require a paid account with them. No hard feelings on that front, and I actually have a paid account, but I've found the API imports lacking when they really don't need to be. For example, Coinbase and Coinbase Pro provide API-based methods to get all the data you could ever want, but CoinTracking doesn't seem to use it all. Alas.

Furthermore, the CSV exports from many exchanges (when they are available at all) often leave out important information, or format the data very strangely, or take a ridiculous amount of effort to accomplish. YES, I'M LOOKING AT YOU, COINBASE PRO. Seriously, Like 50 clicks and 10 emails just to get all of the CSV data for a common variety of trading pair transactions? Ugh.

However, it's not hard to work around these limitations by writing a "bridge" script, so that's what I've done. As a bonus, you can use the CSV data that this script exports in any way you choose, even if you don't use CoinTracking at all. It gives you an easy way to gather transaction details from multiple sources into a collection of files that all have exactly the same format, readable in Excel or Python or anything else that can handle comma-separated values.

# Quick Start

Read the sections below for detail, but if you're familiar with Python, modules, APIs, etc., here's the high-level overview:

1. Install Python (I use [WinPython 3.6](https://winpython.github.io/))
2. Install the `coinbase` and `cbp` modules using `pip install`
3. Clone/download the `crypto_export.py` script from this repo
4. Modify and rename the `crypto_export.conf.sample` file with your API credentials
5. Run `python crypto_export.py` to perform the export
6. Import each exchange's records into CoinTracking using custom CSV rules (see last section)

Done!

# Installation

Installing the Crypto Export script is simple: just clone or download (zip) the repository, or even copy and paste the raw script content into a new .py file on your computer.

You will also need a suitable Python environment available, and for this I recommend WinPython if you're using Windows, as I am:

https://winpython.github.io/

WinPython is nice (on Windows) since you can easily install multiple versions of Python side-by-side without any compatibility issues. For instance, I have a set of 2.x and 3.x versions all residing in the main `C:\Python` folder.

The export script is developed using Python 3.6.4.1, specifically 64-bit edition, but the architecture should be irrelevant. It runs in a console, not with a GUI, so no special GUI libraries or add-ons are needed.

However, you do need a couple of 3rd-party Python libraries for exchange API communication, and these are most easily installed with the `pip` tool that comes with WinPython (and, I believe, most Python environments on any OS). If you are using WinPython, perform the following steps **after** installing the main WinPython application:

1. Navigate to the installation folder that you chose, e.g. `C:\Python\WinPython-64bit-3.5.4.1Qt5`
2. Run the `WinPython Command Prompt.exe` application to enter the command line environment
3. Type `pip install coinbase cbp` to install the libraries from official sources

Now you're all set. The export script will be able to use those libraries when you run it.

# Configuration

To use the script, you first need to supply API credentials in a configuration file for the exchange(s) that you want to use. At the moment, the only supported exchanges are Coinbase and Coinbase Pro. Configuration is done using an INI-like format that is pretty self-explanatory. You can refer to the `crypto_export.conf.sample` file for reference, but here's what it looks like:

```
[files]
prefix = mypf_

[coinbase]
key = COINBASE_API_KEY
secret = COINBASE_API_SECRET

[Coinbase Pro]
passphrase = Coinbase Pro_API_PASSPHRASE
key = Coinbase Pro_API_KEY
secret = Coinbase Pro_API_SECRET
```

All of these sections and configuration items are optional, strictly speaking, but generally you will need to define all of the values for any exchange that you want to use.

**The export script looks for a configuration file named `crypto_export.conf` by default, but you can specify an alternate name with the `-c` or `--config` command line argument.** Make sure that you keep track of whatever name your give to your modified configuration file.

#### [files]

The `[files]` section supports a single `prefix` key which controls the filename prefix used for any generated cache or output CSV files. This is handy if you use the same script with multiple configuration files to track more than one portfolio, using different API credentials. With the example value of `mypf_`, output files will be named `mypf_Coinbase Pro_fills.json`, `mypf_Coinbase Pro_transactions.csv`, etc. If you omit this section, then you will simply get files like `Coinbase Pro_fills.json` and `Coinbase Pro_transactions.csv`.

#### [coinbase]

For Coinbase support, you need to supply the API key and secret values. You should create a dedicated API key for exporting data, and **ONLY GRANT READ PERMISSIONS.** The script does not need (and should not have access to) any other permissions. Once you generate the key from the **Settings -> API Access** area of your account, enter the key and secret values in their respective configuration entries.

![Coinbase API key creation](https://raw.githubusercontent.com/jrowberg/crypto-export/master/screenshots/coinbase_api_key_read_only.png)

#### [Coinbase Pro]

For Coinbase Pro support, you need to supply the API passphrase, key, and secret values. As with Coinbase, **do not grant anything other than VIEW permissions for this key since nothing else is needed.** You can create a new key under the **API** area of your Coinbase Pro account (icon/menu in the upper right corner of the website after logging in).

![Coinbase Pro API key creation](https://raw.githubusercontent.com/jrowberg/crypto-export/master/screenshots/Coinbase Pro_api_key_read_only.png)

# Usage

Using the export script is straightforward once you have completed the above steps. You will need to be in the correct Python environment, which for WinPython most likely means starting the `WinPython Command Prompt.exe` application mentioned in the **Installation** section above. Then navigate to wherever you have cloned/extracted/pasted the `crypto_export.py` script, and run the following command:

```
python crypto_export.py -h
```

This will show you the possible command line options:

```
-------------------------------
Crypto Export Script 20180215.0
-------------------------------

usage: crypto_export.py [-h] [-c CONFIG] [-i INCLUDE [INCLUDE ...]]
                        [-x EXCLUDE [EXCLUDE ...]] [-l]

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Configuration file, default is crypto_export.conf
  -i INCLUDE [INCLUDE ...], --include INCLUDE [INCLUDE ...]
                        List of exchanges to include (whitelist) for this job
  -x EXCLUDE [EXCLUDE ...], --exclude EXCLUDE [EXCLUDE ...]
                        List of exchanges to exclude (blacklist) for this job
  -l, --local           Use locally stored cache files if present
```

Most likely, you won't need any of the command line options unless you are using multiple configuration files for more than one portfolio. However, if you only want or need to export data from a subset of defined exchanges, you can either whitelist (include) or blacklist (exclude) specific exchanges. Currently supported options here are `coinbase` and `Coinbase Pro`. Here is part of an example run output from real accounts:

![Running export](https://raw.githubusercontent.com/jrowberg/crypto-export/master/screenshots/running_export.png)

If you **include** any exchanges, then anything *not* in the list will be excluded by default. If you **exclude** any exchanges, then the script will export from anything defined in the configuration file *except* what you specify for that option.

For example, assume the common use case of having both `[coinbase]` and `[Coinbase Pro]` sections defined in the configuration file, but you only need to update Coinbase since a recurring auto-buy just triggered. In this case, you could use the following command:

```
python crypto_export.py -i coinbase
```

This would skip Coinbase Pro and only pull the latest Coinbase data.

# Limitations

At the moment, you cannot limit the export process based on time or other criteria. Feel free to modify the script to taste if you absolute need to. However, even a pretty comprehensive export runs pretty quickly--much less than a minute even for hundreds of transactions.

# CoinTracking Import

Here's the fun part, particularly if you've had to enter transactions manually or use CoinTracking's internal CSV imports or even some of their API imports. First, you will have to set up custom rules once to start with, but then the process becomes buttery smooth and oh so pleasant.

### STEP 1 (every time):

Log into CoinTracking and go to **Enter Coins -> Bulk Import -> Custom Exchange Import**.

### STEP 2 (every time):

Browse to or drag the CSV file of your choice (e.g. `coinbase_transactions.csv`) into the CoinTracking import target area, and click the orange `Continue to Import` button when the upload completes.

### STEP 3A (only one time per exchange):

Modify the import settings as follows:

1. Set `Fee amount` to "Column 6"
2. Set `Fee currency` to "Column 7"
3. Set `Trade ID` to "Column 8"
4. Set `Comment` to "Column 9"
5. Set `Set Exchange` to whatever you are currently importing (e.g. "Coinbase" or "Coinbase Pro")
6. Set `Parameter 1` as: `Declare as Deposit` if `Column 10` `is exactly (=)` `deposit`
7. Set `Parameter 2` as: `Declare as Withdrawal` if `Column 10` `is exactly (=)` `withdrawal`

I designed the export to otherwise follow CoinTracking's default "custom" column arrangement for file formatting and trade-related date, so no other modifications are required.

Now, to avoid having to do this again for the same exchange later: under `Save / load settings:` choose "Save import settings as:" and supply a suitable name like "Python Coinbase" or whatever, and click the `save` button.

### STEP 3B (every time ONLY IF you've done 3A already):

Select the appropriate saved settings from the `Save / load settings:` dropdown, based on the exchange you are currently importing from.

### STEP 4 (every time):

Click the orange `start import` button to perform the import. Note that the export script defines unique IDs to every transaction based on the information available from the exchange, so you will not get duplicate transactions if you re-import the same file again, or a new file that includes some or all of the same transactions that you imported earlier.

# Feeling Generous?

If this script saves you some headaches, feel free to register or upgrade your CoinTracking account using my affiliate link above, or send any amount of crypto to the following addresses:

* BTC (Bitcoin only): `1ErTEvHLorKix4WVRzeFWGi3xjnKo4qFvi`
* ETH (Ethereum only): `0x18792934E8000C94fEda600198D9867353A53465`
* LTC (Litecoin only): `LNhbYmz3mSmeuL1yJsyTfYSack58aJd2Yj`
* BCH (Bitcoin Cash only): `qrwuw2au9vwkf33sf4nvm8qv5khnhhxhtqldqknct3`

These donations will help me pay off my mortgage as well as encourage further development of this and other handy tools.

Happy accounting!
