import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

# INITIALISATION
global driver
driver = webdriver.Chrome()
driver.get('https://www.playinitium.com')
global HP_THRESHOLD
HP_THRESHOLD = (0.4, 0.6)
WAIT = 4

# LOGIN
input('[AUTO-INITIUM] Please log in. Press <enter> once done.')
NAME = driver.find_element_by_class_name('hint').text
print('[AUTO-INITIUM] Logged in as {}.'.format(NAME))

'''
for now, assume player is always in a camp
'''

# FUNCS
def update_hp():
    global driver
    hp_raw = driver.find_element_by_id('hitpointsBar').text
    hp_current = hp_raw[:hp_raw.find('/')]
    hp_total = hp_raw[hp_raw.find('/')+1:]
    hp_current, hp_total = int(hp_current), int(hp_total)
    return (hp_current, hp_total)

def update_location():
    global driver
    return driver.find_element_by_xpath("//a[@id='locationName']").text

def is_fighting():
    global driver
    try:
        hp_enemy_raw = driver.find_element_by_xpath("//div[@class='combatantWidgetContainer']//div[@id='hitpointsBar']").text
        hp_enemy_current = hp_enemy_raw[:hp_enemy_raw.find('/')]
        if hp_enemy_current == '0':
            return False
        else:
            return True
    except NoSuchElementException:
        return False

def button_defend():
    global driver
    driver.find_element_by_xpath("//a[@onclick='campsiteDefend()']").click()

def button_rest():
    global driver
    driver.find_element_by_xpath("//a[@onclick='doRest()']").click()

def button_popup_okay():
    global driver
    driver.find_element_by_xpath("//div[@onclick='closepopupMessage(1)']").click()

def button_attack_left():
    global driver
    driver.find_element_by_xpath("//a[@onclick='combatAttackWithLeftHand()']").click()

def button_attack_right():
    global driver
    driver.find_element_by_xpath("//a[@onclick='combatAttackWithRightHand()']").click()

def button_collect_gold():
    global driver
    driver.find_element_by_partial_link_text('gold').click()

def button_leave_forget_combat():
    global driver
    driver.find_element_by_partial_link_text('Leave this site and forget about it').click()

# AUTOMATIONS
def auto_combat():
    try:
        print('[AUTO-INITIUM] Closing popup...')
        button_popup_okay()
    except NoSuchElementException:
        pass
    while is_fighting():
        print('[AUTO-INITIUM] Attacking with right hand!')
        button_attack_right()
        time.sleep(4)
    if 'Combat site:' in update_location():
        print('[AUTO-INITIUM] Collecting gold...')
        button_collect_gold()
        time.sleep(4)
        print('[AUTO-INITIUM] Leaving and forgetting.')
        button_leave_forget_combat()

def auto_defend():
    while 'Camp:' in update_location():
        hp_player = update_hp()
        hp_player_percent = hp_player[0] / hp_player[1]
        if not hp_player_percent < HP_THRESHOLD[1]:
            try:
                print('[AUTO-INITIUM] Attempting defense...')
                button_defend()
                time.sleep(4)
                auto_combat()
                time.sleep(4)
            except NoSuchElementException:
                auto_combat()
        else:
            button_rest()
            time.sleep(60)
