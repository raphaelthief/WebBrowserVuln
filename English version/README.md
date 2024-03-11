# WebBrowserVuln

**Exfiltration of web browser data by infostealers**   

In general, all password managers in our web browsers are extremely vulnerable. We will observe how easy it is to obtain all the data stored locally in these browsers.

For this demonstration, we will take a famous browser : Chrome.

This demonstration will be divided into 3 parts :
- A manual demonstration explaining in detail the actions performed by an infostealer
- Presentation of code for a very basic infostealer created by myself
- A schematic representation of the attack pattern of these types of malware: infostealers

# INDEX

- [Manual Analysis](#manual-analysis)
  - [Targeted Files](#targeted-files)
  - [Nature of Files (Encrypted - Unencrypted)](#nature-of-files)
  - [Content of Files - tables](#content-of-files)
  - [Data Decryption](#data-decryption)
- [Automation - Infostealer](#automation---infostealer)
  - [Automating the Search for Targeted Files](#automating-the-search-for-targeted-files)
  - [Data Extraction & Processing](#data-extraction--processing)
  - [Data Transmission](#data-transmission)
  - [Potential Protection Strategies](#potential-protection-strategies)
- [Schematic Presentation of Functioning](#schematic-presentation-of-functioning)


## Manual Analysis

### Targeted Files

**Chrome root folder**   

Initially, one must navigate to the main folder of the browser located in the %APPDATA% of the target machine. The Chromium browsers we are targeting in this demonstration are found in the "local" folder, but other browsers may be found in the "Roaming" branch.

Thus, the target folder for Chrome is as follows :
```
C:\Users\<username>\AppData\Local\Google\Chrome
```
**Browser Extensions & Main Folder**   

The main folder is found in "User Data". The other folders represent browser extensions. These extensions may contain password managers that can undergo the same extractions as we will see with the Chrome password manager.

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/MainFolder.JPG)   


**User Accounts**   

Browsers allow compartmentalization of multiple user accounts to have personalized usage for each. Here, our test environment will be "Test Environment".

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/Profiles.JPG)   

Thus, the main user account "Person 1" is named "Default" in the browser folders. The other profiles will be named "Profile 1" & "Profile 2". "Profile 2" corresponds to our test environment.

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/Profiles2.JPG)   


**Target Files**   

The sensitive files of interest are as follows :

- Local State
```
C:\Users\<username>\AppData\Local\Google\Chrome\User Data\Local State
```

- History
```
C:\Users\<username>\AppData\Local\Google\Chrome\User Data\Profile 2\History
```

- Login Data
```
C:\Users\<username>\AppData\Local\Google\Chrome\User Data\Profile 2\Login Data
```

- Web Data
```
C:\Users\<username>\AppData\Local\Google\Chrome\User Data\Profile 2\Web Data
```

- Cookies
```
C:\Users\<username>\AppData\Local\Google\Chrome\User Data\Profile 2\Network\Cookies
```

**Snapshot Files**

These files are generally not targeted by typical infostealers that focus solely on the latest versions of the previously mentioned files. However, they represent a very useful source of information in anticipating the logic of future victim passwords.
The snapshot folder contains all profiles within it :
```
C:\Users\<username>\AppData\Local\Google\Chrome\User Data\Snapshots
```
![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/Snapshot.JPG)   


### Nature of Files

- Local State   
This file contains the encryption key to access the encrypted browser data. This includes passwords, banking data, cookies, etc...

- History   
Contains data related to the browsing history of the profile.

- Login Data   
This file stores saved passwords on the browser profile in question.

- Web Data   
Contains autofill data, IBANs, credit card information, addresses, and personal information.

- Cookies   
Contains navigation data.

### Content of Files

The targeted files are essentially SQL databases with different tables in each of the files except for "Local State".

- Local State   
This file contains a large amount of information. However, what interests us is simply the "encrypted_key" part encapsulated in "os_crypt".

- History   
The "urls" table will be of interest to us :

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/History.JPG)   

This table contains all the information related to our browsing history (url, title, number of visits, ...)

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/History2.JPG)   

- Login Data   
Here, the "logins" table will be the focus :

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/LoginData.JPG)   

We will select the columns "action_url", "username_value", and finally "password_value".
The latter is encrypted and we will need the decryption key located in the "Local State" file.

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/LoginData2.JPG)   

- Web Data   
In this section, we find a mix of tables with very useful sensitive information for the attacker such as banking information, autofill, addresses, and other personal information like emails, phone numbers, social security numbers, tax reference numbers, etc...

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/WebData.JPG)   

For example, in the "credit_cards" table, we find all credit card information with the encrypted card number that we can decrypt :

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/WebData2.JPG)   

Here, all the personal information recorded such as name + surname, physical address, email, phone number, etc... in the "local_adresses_type_tokens" table :

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/WebData3.JPG)   


- Cookies   
Finally, navigation data in the "cookies" table :

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/Cookies.JPG)   

We will be able to retrieve essential information to impersonate certain established connections using cookies. For example, log in without entering the Netflix password with the session already open thanks to cookies.

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/Cookies2.JPG)   


### Data Decryption

Data decryption can be done using a script that connects the different elements. Please refer to my NavKiller project for this :
[NavKiller](https://github.com/raphaelthief/NavKiller)



## Automation - Infostealer

**Disclaimer**   

This python program is just a minimalist version of what an infostealer can do. Here, I targeted the Chrome browser for this demonstration. It is important to note that this script contains no evasion, spreading, or any other logic specific to malware because that is not the purpose of this demonstration.
There are many scripts that automate the theft of various stored data, so do not waste your time on this example if your intent is malicious. The purpose of this script is to enhance understanding of this type of program to better anticipate them.

**Tips**  
 
Stop using your browser to store sensitive information

**EDR Detection (Sentinelle One)**

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/S1.JPG)   

### Automating the Search for Targeted Files

**You can find the source code of the script here**   

[Basic Chrome Stealer](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Basic%20Infostealer/Basic_Code.py)


### Data Extraction & Processing

**Operation**   

The program acts very simply. The goal is to automate all the steps seen previously.
First, we need to ensure the presence of the Chrome main folder. If this folder exists, we define the target files to extract :

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/Works.JPG)   

Then, we call the various functions aimed at extracting the data we target by focusing on specific tables of the databases to extract :
- Passwords (Login Data file)
- Autofill (Web Data file)
- Personal information (Web Data file)
- Credit cards (Web Data file)
- IBAN (Web Data file)
- Cookies (Cookies file)
- History (History file)

Secondly, we will push the theft of this data by not only targeting the default profile (Default). We will extract data from the various existing profiles in parallel :

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/Works2.JPG)   

Using a loop, we will process all folders named "Profile " followed by a number and perform the same tasks as before.


Rather than storing the extracted information in memory, we store it directly in a text file that we will send later. Often, most malwares, out of habit, perform these tasks in the %TEMP% folder of the PC. However, Windows Defender seems to have adapted to this recurrence, and creating a temporary file in this area increases the program's detection.
Here, since it is a temporary document, I placed it in the %DOCUMENTS% folder of the machine :

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/Works3.JPG)   


Another important point is that there are several extraction methods. Some infostealers will try to process the data directly in the files in the browser folder, and others will copy them to an external folder before processing and deleting them.
In our case, I process them directly in the browser folder, which implies having to close any process using these databases :

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/Works4.JPG)   



In processing the databases, we proceed by focusing on a table to extract specific columns.
For example, for credit cards registered in the Web Data file, we go to the "credit_cards" table and select the columns that seem relevant to us :
- card_number_encrypted
- name_on_card
- expiration_month
- expiration_year

For the "card_number_encrypted" column, the data is encrypted, so we need the "encrypted_key" file in "os_crypt" in the "Local State" file to decrypt this column. Thus, we select "encrypted_key" present in "os_crypt" in this "Local State" file.

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/Works5.JPG)   


**Processing Result**   

These data are fictitious and are for example purposes only. I selected "Profile 2", which is our test environment (all data from my Chrome browser has indeed been extracted, however).
The formatting that follows respects the templates that are often seen in extraction files of these types of programs.

Passwords:

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/Resultat.JPG)   


Personal information, credit cards, IBANs, and cookies :

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/Resultat2.JPG)   


Browsing history:

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/Resultat3.JPG)   





### Data Transmission

Finally, it is common to use webhooks for the exfiltration of stolen data through Discord or Telegram accounts. In this example, I chose to use a Discord webhook.

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/SendIT.JPG)   

The data appears like this on Discord :

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/CaptureDiscord.JPG)   


### Potential Protection Strategies

The first entry point is and will remain human. However, good configuration and management of the firewall and other connection control means will put this type of software out of commission.
These programs often tend to send data to certain webhooks :
- Discord
- Telegram

But also to anonymous hosting sites :
- Anonfiles (Down)
- Io.files

etc ...

Access to these sites is not necessary in a business, for example. The right strategy in my opinion is to create certain filters preventing access to these specific DNS.


## Schematic Presentation of Functioning

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/Infostealer.jpg)   
