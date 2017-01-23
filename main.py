import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

# INITIALISATION
driver = webdriver.Chrome()
driver.get('https://www.playinitium.com')
HP_THRESHOLD = (0.4, 0.6)
# abcdefghijklmnopqrstuvwxyz
EPICS = (
        'Archmage\'s Robes',
        'Bear Hands',
        'Crusader',
        'Fate\'s Call',
        'Final Favor',
        'Forgive and Forget',
        'Gauntlets of Na\'Kareth',
        'Grace of Il\'Kalet',
        'Grave King\'s Axe',
        'Gungnir',
        'Hailstorm',
        'Helm of Na\'Kareth',
        'Molten Blade',
        'Python Scale Tunic',
        'Retribtuion',
        'Rather Rockey Snowball',
        'Seven-League Boots',
        'Suffering\'s End',
        'Thorn',
        'The Really Greatclub',
        'The Black Blade',
        'Western Ranger Cuirass',
        'Wrath of Lotan',
        )

# LOGIN
input('[AUTO-INITIUM] Please log in. Press <enter> once done.')
NAME = driver.find_element_by_class_name('hint').text
print('[AUTO-INITIUM] Logged in as {}.'.format(NAME))
driver.find_element_by_xpath("//a[@onclick='toggleEnvironmentSoundEffects()']").click()

'''
for now, assume player is always in a camp
'''

# FUNCS
def time_format(duration):
    hours = duration // 3600
    duration %= 3600
    minutes = duration // 60
    duration %= 60
    seconds = duration // 1
    hours, minutes, seconds = str(int(hours)), str(int(minutes)), str(int(seconds))
    if hours == '0' and minutes == '0':
        return '{}s'.format(seconds)
    elif hours == '0':
        return '{}mins {}s'.format(minutes, seconds)
    else:
        return '{}hrs {}mins {}s'.format(hours, minutes, seconds)

def update_hp():
    hp_raw = driver.find_element_by_xpath("//div[@class='characterWidgetContainer']//div[@id='hitpointsBar']").text
    hp_current = hp_raw[:hp_raw.find('/')]
    hp_total = hp_raw[hp_raw.find('/')+1:]
    hp_current, hp_total = int(hp_current), int(hp_total)
    return (hp_current, hp_total)

def update_location():
    return driver.find_element_by_xpath("//a[@id='locationName']").text

def update_gold():
    raw = driver.find_element_by_xpath("//div[@id='mainGoldIndicator']").text
    gold = int(raw.replace(',',''))
    return gold

def is_fighting():
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
    driver.find_element_by_xpath("//a[@onclick='campsiteDefend()']").click()

def button_rest():
    driver.find_element_by_xpath("//a[@onclick='doRest()']").click()

def button_popup_okay():
    driver.find_element_by_xpath("//div[@onclick='closepopupMessage(1)']").click()

def button_attack_left():
    driver.find_element_by_xpath("//a[@onclick='combatAttackWithLeftHand()']").click()

def button_attack_right():
    driver.find_element_by_xpath("//a[@onclick='combatAttackWithRightHand()']").click()

def button_collect_gold():
    driver.find_element_by_partial_link_text('gold').click()

def button_custom_collect_item():
    items_all = driver.find_elements_by_xpath("//div[@class='main-item-container']")
    for item in items_all:
        for name in EPICS:
            if name in item.text:
                try:
                    item.find_element_by_link_text('Collect').click()
                    print('[AUTO-INITIUM] {} EPIC! Found a {}.'.format(time.strftime('%I:%M:%S%p'), item))
                except NoSuchElementException:
                    pass


def button_leave_forget_combat():
    driver.find_element_by_partial_link_text('Leave this site and forget about it').click()

# AUTOMATIONS
def _auto_combat():
    try:
        button_popup_okay()
        time.sleep(1)
    except NoSuchElementException:
        pass
    while is_fighting():
        print('[AUTO-INITIUM] {} Attacking with right hand...'.format(time.strftime('%I:%M:%S%p')))
        button_attack_right()
        time.sleep(4)
    if 'Combat site:' in update_location():
        print('[AUTO-INITIUM] {} Collecting gold.'.format(time.strftime('%I:%M:%S%p')))
        button_collect_gold()
        button_custom_collect_item()
        time.sleep(4)
        print('[AUTO-INITIUM] {} Leaving and forgetting.'.format(time.strftime('%I:%M:%S%p')))
        button_leave_forget_combat()
        time.sleep(3)

def _auto_defend():
    try:
    time_start = time.time()
    gold_start = update_gold()
    gold_last = update_gold()
    counter_time_gold_update = 0
    while True:
        counter_time_gold_update += 1
        hp_player = update_hp()
        hp_player_percent = hp_player[0] / hp_player[1]
        if not hp_player_percent < HP_THRESHOLD[1]:
            try:
                button_defend()
                time.sleep(4)
                button_popup_okay()
                time.sleep(1)
            except NoSuchElementException:
                print('[AUTO-INITIUM] {} Combat started.'.format(time.strftime('%I:%M:%S%p')))
                auto_combat()
        else:
            button_rest()
            time.sleep(60)
        if update_gold() != gold_last:
            print('[AUTO-INITIUM] {} Earned {} gold, in {}.'.format(
                time.strftime('%I:%M:%S%p'),
                update_gold()-gold_start,
                time_format(time.time()-time_start)
                ))
            gold_last = update_gold()

def auto_combat():
    try:
        _auto_combat()
    except KeyboardInterrupt:
        return

def auto_defend():
    try:
        _auto_defend()
    except KeyboardInterrupt:
        return
