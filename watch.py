
# import necessary libraries
import requests
import json
import time
import sys

# set up slack webhook url
slack_url = "https://hooks.slack.com/services/XXXXXXXXXXX/XXXXXXXXXXX/XXXXXXXXXXXXXXXXXXXX"

def get_cal():
    '''Returns the calendar from the PCTA permit website. '''
    # Set up. User agent required.
    headers = {
        "User-Agent":
        "Mozilla/5.0 (platform; rv:mobile)"
        + "Gecko/geckotrail Firefox/firefoxversion",
    }
    site = r'https://portal.permit.pcta.org/availability/mexican-border.php'
    page = requests.post(site, headers=headers)
    start = str.find(str(page.content), "var data") + 11
    end = str.find(str(page.content)[start:], "]") + start + 2
    var_data = json.loads(str(page.content)[start:end])
    return var_data
 
def check_days():
    '''Checks calendar for avaliable days.'''
    var_data = get_cal()
    days_available = []
    for i in var_data['calendar']:
        if int(i['num']) < int(var_data["limit"]):
            days_available.append(i['start_date'])
    if len(days_available) != 0:
        return days_available
    else:
        return 0

def change_log(dates):
    '''Records changes to available permits'''
    if changelog[-1] != dates:
        changelog.append(dates)
        print('changelog: ', changelog)
        send_message("Change to Permits!", dates)

def send_message(title, message_text):
    '''Sends message via slack'''
    slack_data = {
        "username": "python_bot",
        "attachments": [
            {
                "fields": [
                    {
                        "title": title,
                        "value": message_text,
                        "short": "false",
                    }
                ]
            }
        ]
    }
    byte_length = str(sys.getsizeof(slack_data))
    headers = {'Content-Type': "application/json", 'Content-Length': byte_length}
    response = requests.post(slack_url, data=json.dumps(slack_data), headers=headers)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    print('message sent: ', message_text)



if __name__ == '__main__':
    '''Scrapes the PCT Permit website every 10 seconds, notifies me of any changes via slack'''
    changelog = [0]
    send_message("Starting scraping program", time.strftime("%H:%M:%S", time.localtime()))
    while True:
        x = check_days()
        t = time.localtime() 
        current_time = time.strftime("%H:%M:%S", t)
        print(current_time, ' --- ', x)
        change_log(x)
        time.sleep(10)

