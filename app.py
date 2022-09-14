import PySimpleGUI as sg
import csv
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

# Find your Account SID and Auth Token at twilio.com/console

sg.theme('DarkBlue 14')
recipients_dict = {}
phone_number_list = []


tab1_layout = [
    [sg.T("Message to send:")],
    [sg.Multiline("", k="message_to_send", size=(50, 20))],
    [sg.B("Send")]
               ]

tab2_layout = [
    [sg.T('Twilio Account SID:')],
    [sg.I(sg.user_settings_get_entry('account_sid', ''), k='account_sid')],
    [sg.T('Twilio Auth Token:')],
    [sg.I(sg.user_settings_get_entry('auth_token', ''), k='auth_token')],
    [sg.T('Origination Phone Number:')],
    [sg.I(sg.user_settings_get_entry('send_from_number', 'Ex. +15554569823'), k='send_from_number')],
    [sg.B("Save Settings")]
                ]

tab3_layout = [
    [sg.T('Add recipients with button at bottom.')],
    [sg.Multiline(sg.user_settings_get_entry('recipient_box', ''), k='recipient_box', size=(50, 20), write_only=True)],
    [sg.B("Add Recipient")]
                ]

# The Tab Group layout - it must contain only Tabs
tab_group_layout = [
    [sg.Tab('Send', tab1_layout, key='tab1'),
     sg.Tab('Settings', tab2_layout, key='tab2'),
     sg.Tab('Recipients', tab3_layout, key='tab3')]
                     ]

# The window layout - defines the entire window
layout = [
    [sg.TabGroup(tab_group_layout, enable_events=True, key='tab_group')],
    [sg.Button('Exit')]
           ]

window = sg.Window("Twilio Sender", layout)
mline = window['recipient_box']


def send_message(message_to_send):
    acc_sid = sg.user_settings_get_entry('account_sid')
    a_t = sg.user_settings_get_entry('auth_token')
    client = Client(acc_sid, a_t)
    from_num = sg.user_settings_get_entry('send_from_number')
    for key, val in recipients_dict.items():
        temp_phone_number_list = []
        temp_phone_number_list.append(val)
        [phone_number_list.append(x) for x in temp_phone_number_list if x not in phone_number_list]
    try:
        for number in phone_number_list:
            message = client.messages \
                .create(
                     body=message_to_send,
                     from_=from_num,
                     to=number
                 )
    except TwilioRestException as e:
        sg.popup(e, title="An error was returned from Twilio")
        pass


def add_new_recipient(name, phone_number):
    temp_dict = {name : phone_number}
    with open('recipients.csv', 'a', newline='') as file:
        write = csv.writer(file)
        for key, val in temp_dict.items():
            write.writerow([key, val])


def update_mline():
    global recipients_dict
    try:
        with open('recipients.csv', 'r') as file:
            read = csv.reader(file)
            recipients_dict = {rows[0] : rows[1] for rows in read}
            mline.update(recipients_dict)
    except IndexError:
        print("IndexError")
        pass
    except FileNotFoundError:
        print("FileNotFoundError")
        pass


def main():
    while True:
        event, values = window.read()
        update_mline()
        if event == "Send":
            send_message(values['message_to_send'])
        if event == "Save Settings":
            sg.user_settings_set_entry('send_from_number', values['send_from_number'])
            sg.user_settings_set_entry('auth_token', values['auth_token'])
            sg.user_settings_set_entry('account_sid', values['account_sid'])
        if event == "Add Recipient":
            new_recipient_name = sg.popup_get_text(message="Enter only the recipient's name:",
                                                   title="Add Recipient")
            new_recipient_number = sg.popup_get_text(message="Enter only the recipient's phone number "
                                                     "with country and area code (ex. +15554569823):",
                                                     title="Add Recipient")
            add_new_recipient(new_recipient_name, new_recipient_number)
            update_mline()
        if event == "Exit" or event == sg.WIN_CLOSED:
            window.close()
            exit(0)


if __name__ == '__main__':
    main()
