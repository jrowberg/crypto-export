# Crypto Export script, version 20180215.0 by Jeff Rowberg
# Latest version always available at: https://github.com/jrowberg/crypto-export
#
# This script is released under the MIT license. Basically this means that you
# can do whatever the heck you want to with it, personally or commercially, and
# I'm not responsible for anything that happens with it. For details, see the
# "LICENSE" file in the root of the above GitHub repository.
#
# ==============================================================================
# CRYPTO SAFETY DISCLAIMER: This script makes use of some official and some
# unofficial 3rd-party API libraries, all of which are open-source. They are
# only used for READ operations, as you can see from the code, and no actual
# trades, deposits, or withdrawals are attempted under any circumstances.
# However, I strongly encourage you to review the code as well as the libraries
# used for API communication to ensure the safety of your funds. It is always
# a good idea to vet any code that can cost you actual money if it doesn't work
# as described.
#
# ==============================================================================
# Comprehensive pip module installation for exchange API connectors:
#
#   pip install coinbase gdax
#
# Planned future support (NOT NECESSARY TO INCLUDE THESE YET):
#
#   pip install python-binance BitstampClient python-kucoin python-quoine https://github.com/s4w3d0ff/python-poloniex/archive/v0.4.7.zip
#
# Under investigation:
#
#           cryptopia? https://github.com/crypto-crew-tech/cryptopia-api-python or https://github.com/salfter/PyCryptopia
#           livecoin? https://github.com/metaperl/pylivecoin
#
# Fix for winrandom problem with WinPython 3.5 64bit: https://stackoverflow.com/a/39478958/2863900

import argparse, configparser, os, sys, re, json
import pprint

supported_exchanges = ['coinbase', 'gdax']

# welcome banner with script version
print("-------------------------------")
print("Crypto Export Script 20180215.0")
print("-------------------------------")
print("")

# define and parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", help="Configuration file, default is crypto_export.conf", default="crypto_export.conf")
parser.add_argument("-i", "--include", help="List of exchanges to include (whitelist) for this job", nargs="+")
parser.add_argument("-x", "--exclude", help="List of exchanges to exclude (blacklist) for this job", nargs="+")
parser.add_argument("-l", "--local", help="Use locally stored cache files if present", action="store_true")
args = parser.parse_args()

# make sure configuration file exists
if not os.path.isfile(args.config):
    print("Cannot find config file '%s'" % args.config)
    sys.exit(1)

# read configuration details
config = configparser.ConfigParser()
config.read(args.config)

# get file prefix settings, if configured
file_prefix = ''
if 'files' in config.sections():
    if 'prefix' in config['files']:
        file_prefix = config['files']['prefix']

# find all defined exchanges that we care about
print("Supported exchanges: %s" % supported_exchanges)
print("Whitelisted exchanges: %s" % args.include)
print("Blacklisted exchanges: %s" % args.exclude)
defined_exchanges = []
queued_exchanges = []
for exchange in supported_exchanges:
    # skip if we have a whitelist and this isn't on it
    if args.include != None and exchange not in args.include:
        print("Skipping checks for '%s'" % exchange)
        continue

    print("Checking for '%s' definition in configuration file..." % exchange, end='')
    if exchange in config.sections():
        print("found")
        defined_exchanges.append(exchange)
    else:
        print("not found")
        if args.include != None and exchange in args.include:
            print("Explicitly included exchange '%s' is not defined in config file" % exchange)
            sys.exit(2)
        continue

    if (args.exclude == None or exchange not in args.exclude) and (args.include == None or exchange in args.include):
        queued_exchanges.append(exchange)

# import modules required to run job
print("Job list: %s" % ', '.join(queued_exchanges))

# COINBASE EXPORT
if 'coinbase' in queued_exchanges:
    from coinbase.wallet.client import Client as CoinbaseClient
    if not set(['key', 'secret']).issubset(set(config['coinbase'])):
        print("Coinbase configuration requires 'key' and 'secret' values")
        sys.exit(3)

    print("Creating Coinbase client")
    coinbase_client = CoinbaseClient(config['coinbase']['key'], config['coinbase']['secret'])

    if args.local and os.path.isfile('%scoinbase_accounts.json' % file_prefix):
        print("Reading Coinbase account details from %scoinbase_accounts.json" % file_prefix)
        with open('%scoinbase_accounts.json' % file_prefix, 'r') as infile:
            coinbase_accounts = json.load(infile)
    else:
        print("Getting Coinbase account list via API")
        coinbase_accounts = coinbase_client.get_accounts(order='asc', limit=100)

        for i, account in enumerate(coinbase_accounts["data"]):
            print("- #%d %s: %s %s available (currently %s %s)" % (i, account['id'], account['balance'], account['currency'], account['native_balance']['amount'], account['native_balance']['currency']))

            print("--- Getting transactions via API")
            coinbase_accounts['data'][i]['transactions'] = coinbase_client.get_transactions(account['id'], order='asc', limit=100)
            pagination = coinbase_accounts['data'][i]['transactions'].pagination
            page = 2
            while pagination != None and pagination['next_uri'] != None:
                print("--- Getting transactions via API (page %d)" % page)
                starting_after_guid = re.search('starting_after=([0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12})', pagination.next_uri, re.I).group(1)
                next_page = coinbase_client.get_transactions(account['id'], order='asc', limit=100, starting_after=starting_after_guid)
                coinbase_accounts['data'][i]['transactions']['data'] = coinbase_accounts['data'][i]['transactions']['data'] + next_page['data']
                pagination = next_page.pagination
                page = page + 1

            print("--- Getting buys via API")
            coinbase_accounts['data'][i]['buys'] = coinbase_client.get_buys(account['id'], order='asc', limit=100)
            pagination = coinbase_accounts['data'][i]['buys'].pagination
            page = 2
            while pagination != None and pagination['next_uri'] != None:
                print("--- Getting buys via API (page %d)" % page)
                starting_after_guid = re.search('starting_after=([0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12})', pagination.next_uri, re.I).group(1)
                next_page = coinbase_client.get_buys(account['id'], order='asc', limit=100, starting_after=starting_after_guid)
                coinbase_accounts['data'][i]['buys']['data'] = coinbase_accounts['data'][i]['buys']['data'] + next_page['data']
                pagination = next_page.pagination
                page = page + 1

            print("--- Getting sells via API")
            coinbase_accounts['data'][i]['sells'] = coinbase_client.get_sells(account['id'], order='asc', limit=100)
            pagination = coinbase_accounts['data'][i]['sells'].pagination
            page = 2
            while pagination != None and pagination['next_uri'] != None:
                print("--- Getting sells via API (page %d)" % page)
                starting_after_guid = re.search('starting_after=([0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12})', pagination.next_uri, re.I).group(1)
                next_page = coinbase_client.get_sells(account['id'], order='asc', limit=100, starting_after=starting_after_guid)
                coinbase_accounts['data'][i]['sells']['data'] = coinbase_accounts['data'][i]['sells']['data'] + next_page['data']
                pagination = next_page.pagination
                page = page + 1

            print("--- Getting deposits via API")
            coinbase_accounts['data'][i]['deposits'] = coinbase_client.get_deposits(account['id'], order='asc', limit=100)
            pagination = coinbase_accounts['data'][i]['deposits'].pagination
            page = 2
            while pagination != None and pagination['next_uri'] != None:
                print("--- Getting deposits via API (page %d)" % page)
                starting_after_guid = re.search('starting_after=([0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12})', pagination.next_uri, re.I).group(1)
                next_page = coinbase_client.get_deposits(account['id'], order='asc', limit=100, starting_after=starting_after_guid)
                coinbase_accounts['data'][i]['deposits']['data'] = coinbase_accounts['data'][i]['deposits']['data'] + next_page['data']
                pagination = next_page.pagination
                page = page + 1

            print("--- Getting withdrawals via API")
            coinbase_accounts['data'][i]['withdrawals'] = coinbase_client.get_withdrawals(account['id'], order='asc', limit=100)
            pagination = coinbase_accounts['data'][i]['withdrawals'].pagination
            page = 2
            while pagination != None and pagination['next_uri'] != None:
                print("--- Getting withdrawals via API (page %d)" % page)
                starting_after_guid = re.search('starting_after=([0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12})', pagination.next_uri, re.I).group(1)
                next_page = coinbase_client.get_withdrawals(account['id'], order='asc', limit=100, starting_after=starting_after_guid)
                coinbase_accounts['data'][i]['withdrawals']['data'] = coinbase_accounts['data'][i]['withdrawals']['data'] + next_page['data']
                pagination = next_page.pagination
                page = page + 1

        print("Storing account data in %scoinbase_accounts.json" % file_prefix)
        with open('%scoinbase_accounts.json' % file_prefix, 'w') as outfile:
            json.dump(coinbase_accounts, outfile)

    coinbase_entries = []
    for z, account in enumerate(coinbase_accounts['data']):
        if account['currency'] not in ['BTC', 'ETH', 'LTC', 'BCH']:
            # skip non-crypto accounts, native currencies are handled as part of buy/sell transactions
            continue

        for i, buy in enumerate(account['buys']['data']):
            if buy['status'] in ['canceled']:
                continue
            row = [
                buy['created_at'],
                buy['amount']['amount'],
                buy['amount']['currency'],
                buy['total']['amount'],
                buy['total']['currency'],
                '%0.8f' % (float(buy['total']['amount']) - float(buy['subtotal']['amount'])),
                buy['total']['currency'],
                buy['id'],
                'Reference: %s' % buy['user_reference'],
                'trade',
                'Coinbase']
            coinbase_entries.append(row)
            #pprint.pprint(buy)
            #print(','.join('%s' % x for x in row))

        for i, sell in enumerate(account['sells']['data']):
            if sell['status'] in ['canceled']:
                continue
            row = [
                sell['created_at'],
                sell['total']['amount'],
                sell['total']['currency'],
                sell['amount']['amount'],
                sell['amount']['currency'],
                '%0.8f' % (float(sell['subtotal']['amount']) - float(sell['total']['amount'])),
                sell['total']['currency'],
                sell['id'],
                'Reference: %s' % sell['user_reference'],
                'trade',
                'Coinbase']
            coinbase_entries.append(row)
            #pprint.pprint(sell)
            #print(','.join('%s' % x for x in row))

        for i, transaction in enumerate(account['transactions']['data']):
            if transaction['status'] in ['canceled']:
                continue
            row = [transaction['created_at'], 0, '', 0, '', 0, '', transaction['id'], 'Native %s %s' % (transaction['native_amount']['amount'], transaction['native_amount']['currency']), '', 'Coinbase']
            if transaction['type'] == 'buy':
                # incoming fiat currency associated with buy transaction
                row[1] = transaction['native_amount']['amount']
                row[2] = row[4] = row[6] = transaction['native_amount']['currency']
                row[8] = "Deposit for %s %s buy from %s" % (transaction['amount']['amount'], transaction['amount']['currency'], transaction['details']['payment_method_name'])
                row[9] = 'deposit'
            elif transaction['type'] == 'sell':
                # outgoing fiat currency associated with sell transaction
                row[3] = transaction['native_amount']['amount']
                row[2] = row[4] = row[6] = transaction['native_amount']['currency']
                row[8] = "Withdrawal from %s %s sell into %s" % (transaction['amount']['amount'], transaction['amount']['currency'], transaction['details']['payment_method_name'])
                row[9] = 'withdrawal'
            elif transaction['type'] == 'send':
                if 'to' in transaction:
                    # withdrawal (outgoing funds)
                    row[3] = '%0.8f' % -float(transaction['amount']['amount'])
                    row[2] = row[4] = transaction['amount']['currency']
                    row[8] = row[8] + (': To %s' % transaction['to']['resource'])
                    row[9] = 'withdrawal'
                else:
                    # deposit (incoming funds)
                    row[1] = '%0.8f' % float(transaction['amount']['amount'])
                    row[2] = row[4] = transaction['amount']['currency']
                    row[8] = row[8] + (': From %s' % transaction['from']['resource'])
                    row[9] = 'deposit'
                    if 'status' in transaction['network'] and transaction['network']['status'] == "off_blockchain":
                        # strange transaction, could be a referral bonus or an oddly categorized deposit
                        # this should NOT be necessary as far as I can tell from the API docs, but it is for corner cases
                        if 'buy' in transaction:
                            buy_transaction_id = transaction['buy']['resource_path'].split('/')[-1]
                            for t2 in account['buys']['data']:
                                if t2['id'] == buy_transaction_id:
                                    row[1] = transaction['native_amount']['amount']
                                    row[2] = row[4] = row[6] = transaction['native_amount']['currency']
                                    row[5] = '%0.8f' % (float(t2['total']['amount']) - float(t2['subtotal']['amount'])),
                                    row[8] = "Deposit for %s %s buy from unexpected payment source" % (transaction['amount']['amount'], transaction['amount']['currency'])
            elif transaction['type'] in ['pro_withdrawal', 'pro_deposit', 'exchange_deposit', 'exchange_withdrawal', 'fiat_deposit', 'fiat_withdrawal', 'order']:
                row[8] = row[8] + (': %s %s' % (transaction['details']['title'], transaction['details']['subtitle']))
                if float(transaction['amount']['amount']) < 0:
                    # withdrawal (outgoing funds)
                    row[3] = '%0.8f' % -float(transaction['amount']['amount'])
                    row[2] = row[4] = transaction['amount']['currency']
                    row[9] = 'withdrawal'
                else:
                    # deposit (incoming funds)
                    row[1] = '%0.8f' % float(transaction['amount']['amount'])
                    row[2] = row[4] = transaction['amount']['currency']
                    row[9] = 'deposit'
            else:
                # unknown transaction type, maybe they changed their API or something
                print("%s has unknown transaction type '%s'" % (row[7], transaction['type']))
                pprint.pprint(transaction)
                continue

            coinbase_entries.append(row)
            #pprint.pprint(transaction)
            #print(','.join('%s' % x for x in row))

        #for i, deposit in enumerate(account['deposits']['data']):
            #pprint.pprint(deposit)

        #for i, withdrawal in enumerate(account['withdrawals']['data']):
            #pprint.pprint(withdrawal)

    coinbase_transactions_count = len(coinbase_entries)
    print("- Processed %d transactions for all accounts" % coinbase_transactions_count)
    print("- Total of %d records obtained from Coinbase" % len(coinbase_entries))

    with open('%scoinbase_transactions.csv' % file_prefix, 'w') as outfile:
        outfile.write('Trade date,Buy amount,Buy currency,Sell amount,Sell currency,Fee amount,Fee currency,Trade ID,Comment,Type\n')
        for row in sorted(coinbase_entries, key=lambda row: row[0]):
            outfile.write('%s\n' % ','.join(['%s' % x for x in row]))

# GDAX EXPORT
if 'gdax' in queued_exchanges:
    import gdax
    if not set(['passphrase', 'key', 'secret']).issubset(set(config['gdax'])):
        print("GDAX configuration requires 'passphrase', 'key', and 'secret' values")
        sys.exit(3)

    print("Creating authenticated GDAX client")
    gdax_auth_client = gdax.AuthenticatedClient(config['gdax']['key'], config['gdax']['secret'], config['gdax']['passphrase'])

    if args.local and os.path.isfile('%sgdax_accounts.json' % file_prefix):
        print("Reading GDAX account details from %sgdax_accounts.json" % file_prefix)
        with open('%sgdax_accounts.json' % file_prefix, 'r') as infile:
            gdax_accounts = json.load(infile)
    else:
        print("Getting GDAX account list via API")
        gdax_accounts = gdax_auth_client.get_accounts()

        print("- GDAX profile %s" % (gdax_accounts[0]['profile_id']))
        for i, account in enumerate(gdax_accounts):
            print("- #%d %s: %0.16f %s available (%0.16f %s on hold), getting account history via API" % (i, account['id'], float(account['available']), account['currency'], float(account['hold']), account['currency']))
            gdax_accounts[i]['history'] = gdax_auth_client.get_account_history(account['id'])

        print("Storing account history in %sgdax_accounts.json" % file_prefix)
        with open('%sgdax_accounts.json' % file_prefix, 'w') as outfile:
            json.dump(gdax_accounts, outfile)

    if args.local and os.path.isfile('%sgdax_fills.json' % file_prefix):
        print("Reading GDAX fill details from %sgdax_fills.json" % file_prefix)
        with open('%sgdax_fills.json' % file_prefix, 'r') as infile:
            gdax_fills = json.load(infile)
    else:
        print("Getting GDAX order fill history via API")
        gdax_fills = gdax_auth_client.get_fills()

        print("Storing fill history in %sgdax_fills.json" % file_prefix)
        with open('%sgdax_fills.json' % file_prefix, 'w') as outfile:
            json.dump(gdax_fills, outfile)

    gdax_entries = []
    for i, fill_page in enumerate(gdax_fills):
        for j, fill in enumerate(fill_page):
            row = [fill['created_at'], 0, 'XYZ', 0, 'XYZ', fill['fee'], 'XYZ', '%s-%s' % (fill['order_id'], fill['trade_id']), 'USD volume: $%f' % float(fill['usd_volume']), 'trade', 'GDAX']
            buy_cur, sell_cur = fill['product_id'].split('-')
            row[6] = sell_cur
            if fill['side'] == 'buy':
                row[1] = fill['size']
                row[2] = buy_cur
                row[3] = '%0.8f' % ((float(fill['size']) * float(fill['price'])) + float(fill['fee']))
                row[4] = sell_cur
            else:
                row[1] = '%0.8f' % ((float(fill['size']) * float(fill['price'])) - float(fill['fee']))
                row[2] = sell_cur
                row[3] = fill['size']
                row[4] = buy_cur

            gdax_entries.append(row)
            #pprint.pprint(fill)
            #print(','.join('%s' % x for x in row))

    gdax_fills_count = len(gdax_entries)
    print("- Processed %d order fills for all accounts" % gdax_fills_count)

    for z, account in enumerate(gdax_accounts):
        for i, transaction_page in enumerate(account['history']):
            for j, transaction in enumerate(transaction_page):
                row = [transaction['created_at'], 0, account['currency'], 0, account['currency'], 0, account['currency'], '', '', '', 'GDAX']
                if transaction['type'] == 'match':
                    continue
                elif transaction['type'] == 'fee':
                    continue
                elif transaction['type'] == 'transfer':
                    row[7] = '%s' % (transaction['details']['transfer_id'])
                    if transaction['details']['transfer_type'] == 'deposit':
                        row[9] = 'deposit'
                        row[1] = '%0.16f' % float(transaction['amount'])
                    elif transaction['details']['transfer_type'] == 'withdraw':
                        row[9] = 'withdrawal'
                        row[3] = '%0.16f' % -float(transaction['amount'])
                else:
                    # unknown transaction type, maybe they changed their API or something
                    continue

                gdax_entries.append(row)
                #pprint.pprint(transaction)
                #print(','.join('%s' % x for x in row))

    gdax_transfers_count = len(gdax_entries) - gdax_fills_count
    print("- Processed %d transfers for all accounts" % gdax_transfers_count)
    print("- Total of %d records obtained from GDAX" % len(gdax_entries))

    with open('%sgdax_transactions.csv' % file_prefix, 'w') as outfile:
        outfile.write('Trade date,Buy amount,Buy currency,Sell amount,Sell currency,Fee amount,Fee currency,Trade ID,Comment,Type\n')
        for row in sorted(gdax_entries, key=lambda row: row[0]):
            outfile.write('%s\n' % ','.join(['%s' % x for x in row]))
