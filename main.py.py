import os
import telebot
import requests
import json
from cowin_api import CoWinAPI
print("STARTING\n\n")
API_KEY = "1883537193:AAExoq-1syEyTXmd3PypFYoWOU1QkhLM1p0"
bot = telebot.TeleBot(API_KEY)
cow = CoWinAPI()

# print(API_KEY)

@bot.message_handler(commands=['start','hi', 'Start', 'Hi'])
def greet(message):
  bot.reply_to(message, "Hello ! " + message.from_user.first_name +'\n')


@bot.message_handler(commands = ['slot'])
def find_vac_slot(message):
  bot.reply_to(message, "Type \"/pin {$pincode$} {$date$} {$age-group$}\" to search by pincode\n\n")


def get_available_slots_by_pincode(pin_code, inp_date, age_group):

  min_age = -1
  if(age_group == "18+"):
    min_age = 18
  else:
    min_age = 45

  # available_centers = cow.get_availability_by_pincode(pin_code, inp_date)
  header = {'accept': 'application/json','Origin': 'https://apisetu.gov.in', 'referer':'https://www.replit.com', 'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'} 
  r = requests.get("https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={}&date={}".format(pin_code, inp_date), headers = header)
  if 'json' in r.headers.get('Content-Type'):
    json_data = r.json()
    # print(json_data)
  else:
    print('Response content is not in JSON format.')
    print(r)
    json_data = 'spam'
      # print(r)
  available_centers = json_data
  print("DONE")
  valid_data = []
  for dic in available_centers['centers']:
    # valid_center = 0
    for sess in dic['sessions']:
      if(sess['date'] == inp_date and sess['min_age_limit'] <= min_age and sess['available_capacity'] > 0):
        valid_data.append(dic)
        break
  return valid_data

def form_printable_pin_comm_string(centre_detail, input_date):
  sess_index = -1
  ptr = 0
  for sess in centre_detail['sessions']:
    if(sess['date'] == input_date):
      sess_index = ptr
      break
    ptr += 1

  final_string = "Name : " + centre_detail['name'] + "\nAddress : " + centre_detail['address'] + "\nState : " + centre_detail['state_name'] + "\nDistrict : " + centre_detail['district_name'] + "\nBlock : " + centre_detail['block_name'] + "\nTimings : " + centre_detail['from'] + ' to ' + centre_detail['to'] + "\nFee Type : " + centre_detail['fee_type']+ "\nVaccine : " + centre_detail['sessions'][sess_index]['vaccine'] +"\nTotal Doses : " + str(centre_detail['sessions'][sess_index]['available_capacity']) + "\nDose-1 shots : " + str(centre_detail['sessions'][sess_index]['available_capacity_dose1']) + "\nDose-2 shots : " + str(centre_detail['sessions'][sess_index]['available_capacity_dose2']) +"\nSlots : \n"
  slot_num = 1
  for slot in centre_detail['sessions'][sess_index]['slots']:
    final_string += str(slot_num) + ". " + slot + "\n"
    slot_num += 1
  return final_string

@bot.message_handler(commands = ['pin'])
def find_slot_by_pin(message):
  comms = message.text.split()
  pincode = comms[1]
  inp_date = comms[2]
  age_group = comms[3]
  print(pincode)
  print(inp_date)
  print(age_group)
  all_pincode_data = get_available_slots_by_pincode(pincode, inp_date, age_group)
  bot_string = ""
  if(len(all_pincode_data) > 0):
    bot_string += "Available slots in area pincode " + pincode + " on " + inp_date + " for age group " + age_group + "\n\n"
    for centre in all_pincode_data:
      centre_string = form_printable_pin_comm_string(centre, inp_date)
      bot_string += centre_string + "\n"
  else:
    bot_string += "No slots currently available ! \n\n We will inform you as soon as a slot is available in the given area for the age group " + age_group +"\n"
  bot.reply_to(message, bot_string)
  
@bot.message_handler(commands = ['test'])
def tester(message):
	markup = telebot.types.ReplyKeyboardMarkup(row_width = 2)
	btn1 = telebot.types.KeyboardButton('a')
	btn2 = telebot.types.KeyboardButton('b')
	btn3 = telebot.types.KeyboardButton('c')
	btn4 = telebot.types.KeyboardButton('d')
	markup.add(btn1, btn2, btn3, btn4)
	bot.reply_to(message, "Choose one letter:", reply_markup=markup)
	var option = {
					"parse_mode": "Markdown",
  					"reply_markup": {
    						"keyboard": [
      										["a"],
      										["b"],
      										["c"],
      										["d"]
    									]
  									}
				};
	print(option)




bot.polling()
