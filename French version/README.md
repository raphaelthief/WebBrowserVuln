# WebBrowserVuln

**Exfiltration des données du navigateur web par les infostealer**

De manière générale tous les gestionnaires de mots de passe de nos navigateurs web sont extrêmement vulnérables. Nous allons constater à quel point il est facile de se procurer toutes les données qui sont enregistrées en local dans ces navigateurs.

Pour cette démonstration, nous allons prendre un célèbre navigateur : Chrome

Cette démonstration se basera sur 3 parties :
- Une démonstration manuelle qui expliquent de façon détaillée les actions effectuées par un infostealer
- Une présentation de code d'un infostealer très basique créé par mes soins
- Une représentation schématique d'attaque de ces types de malwares : les infostealer


# INDEX

- [Analyse manuelle](#Analyse-manuelle)
  - [Fichiers ciblés](#Fichiers-ciblés)
  - [Nature des fichiers (Chiffrés - Non chiffrés)](#Nature-des-fichiers)
  - [Contenu des fichiers - tables](#Contenu-des-fichiers)
  - [Déchiffrement des données](#Déchiffrement-des-données)
- [Automatisation - Infostealer](#Automatisation---Infostealer)
  - [Automatisation de la recherche des fichiers cibles](#Automatisation-de-la-recherche-des-fichiers-cibles)
  - [Extraction & traitement des données](#Extraction-et-traitement-des-données)
  - [Envoie des données](#Envoie-des-données)
  - [Eventuelle stratégie de protection](#Eventuelle-stratégie-de-protection)
- [Présentation schématique de fonctionnement](#Présentation-schématique-de-fonctionnement)


  

## Analyse manuelle
### Fichiers ciblés

**Dossier racine de Chrome**   

Dans un premier temps, il faut se rendre dans le dossier principal du navigateur situé dans %APPDATA% de la machine cible

Les navigateurs Chromium que nous visons dans cette démonstration se trouvent dans le dossier "local" mais d'autres navigateurs se trouvent dans la branche "Roaming"

Ainsi, le dossier cible de chrome est le suivant :
```
C:\Users\<username>\AppData\Local\Google\Chrome
```


**Extensions navigateur & dossier principal**   

Le dossier principal se trouve donc dans "User Data"

Les autres dossiers représentent les extensions navigateur. Ces extensions peuvent contenir des gestionnaires de mots de passe pouvant subir les mêmes extractions que nous allons constater avec le gestionnaire de mots de passe Chrome.

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/MainFolder.JPG)   


**Comptes utilisateurs**   

Sur les navigateurs, il est possible de compartimenter plusieurs comptes d'utilisateurs afin d'avoir un usage personnalisé pour chacun

Ici, notre environnement de test sera "Environnement Test"

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/Profiles.JPG)   

Ainsi, le compte utilisateur principal "Personne 1" se nomme "Default" dans les dossiers du navigateur. Les deux autres profils se nommeront "Profile 1" & "Profile 2"

Le "Profile 2" correspond à notre environnement test

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/Profiles2.JPG)   


**Fichiers cibles**   

Les fichiers sensibles qui vont nous intéressés seront les suivants :

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

**Fichiers snapshots**   

Ces fichiers ne sont généralement pas la cible des infostealer classiques qui se concentrent uniquement sur les dernières versions des fichiers précédemment cités. Néanmoins, ils représentent une source d'information très utile dans l'anticipation de la logique des futurs mots de passe de la victime.

Le dossier snapshot contient tous les profils en son sein :
```
C:\Users\<username>\AppData\Local\Google\Chrome\User Data\Snapshots
```
![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/Snapshot.JPG)   


### Nature des fichiers

- Local State   
Ce fichier contient la clé de chiffrement pour accéder aux données chiffrées du navigateur. C'est-à-dire les mots de passe, les données bancaires, les cookies, etc ...

- History   
Contient les données relatives à l'historique de navigation du profil

- Login Data   
Dans ce fichier est entreposé les mots de passe enregistrés sur le profil en question du navigateur

- Web Data   
Ici se trouvent les données d'autoremplissage, les IBAN, les cartes de crédit, les adresses et informations personnelles enregistrées

- Cookies   
Comme son nom l'indique, les données relatives aux cookies


### Contenu des fichiers

Les fichiers que nous avons ciblés sont enfaite des bases de données SQL avec différentes tables dans chacun des fichiers sauf pour le "Local State".   

- Local State   
Ce fichier contient une grosse quantité d'informations. Cependant, ce qui va nous intéresser c'est tout simplement la partie "encrypted_key" encapsulée dans "os_crypt".   

- History   
La table "urls" sera celle qui va nous intéresser :

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/History.JPG)   

Cette table contient toutes les informations relatives à notre historique de navigation (url, titre, nombre de visites, ...)

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/History2.JPG)   


- Login Data   
Ici, la table "logins" sera le centre de notre attention :

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/LoginData.JPG)   

Nous chercherons à sélectionner les colones "action_url", "username_value" et enfin "password_value".   

Cette dernière est chiffrée et nous aurons besoin de la clé de chiffrement située dans le fichier "Local State"

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/LoginData2.JPG)   

- Web Data   
Dans cette partie, nous retrouvons donc un condensé de table avec des informations sensibles très utiles pour l'attaquant telles que les informations bancaires, les autofill, les adresses et autres informations personnelles comme les mails, numéros de téléphone, numéros de sécurité sociale, numéro fiscal de référence, etc ...

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/WebData.JPG)   

Par exemple dans la table "credit_cards" nous retrouvons toutes les informations des cartes de credit enregistrées avec le numéro de carte chiffré que nous pouvons déchiffrer :

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/WebData2.JPG)   

Ici, toutes les informations personnelles enregistrées tels que le nom + prénom, adresse physique, mail, téléphone, etc ... dans la table "local_adresses_type_tokens" :

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/WebData3.JPG)   


- Cookies   
Enfin, les données de navigation dans la table "cookies" :

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/Cookies.JPG)   

Nous allons pouvoir récupérer les informations essentielles pour usurper certaines connexions établies à l'aide des cookies. Par exemple, nous connecter sans avoir à entrer le mot de passe Netflix avec la session déjà ouverte grâce aux cookies.

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/Cookies2.JPG)   


### Déchiffrement des données

Le déchiffrement des données peut se faire à partir d'un script qui relie les différents éléments entre eux. Je vous invite à vous rendre sur le projet NavKiller de mon repo :
[NavKiller](https://github.com/raphaelthief/NavKiller)




## Automatisation - Infostealer

**Avertissement**   

Ce programme python n'est qu'une version minimaliste de ce que peut faire un infostealer. Ici, j'ai ciblé le navigateur chrome pour cette démonstration. Il est important de noter que ce script ne contient aucun moyen d'évasion, de spread ou tout autre logique propre aux malwares car ce n'est pas l'objet de cette démonstration.

Il existe de nombreux scripts qui automatisent le vol des différentes données enregistrées alors ne perdez pas votre temps sur cet exemple qui ne vous apportera rien si votre démarche est d'ordre malveillante. L'objectif de ce script est de pousser la compréhension de ce type de programme afin de mieux les anticiper.

**Conseils**   

Arrêtez d'utiliser votre navigateur pour stocker vos informations sensibles


**Détection EDR (Sentinelle One)**

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/S1.JPG)   


### Automatisation de la recherche des fichiers cibles

**Vous trouverez le code source du script ici**   

[Basic Chrome Stealer](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Basic%20Infostealer/Basic_Code.py)



### Extraction et traitement des données

**Fonctionnement**   

Le programme agit de façon très simple. L'objectif étant d'automatiser toutes les démarches vues précédement.
Dans un premier temps, nous devons nous assurer de la présence du dossier principal Chrome. Si ce dossier existe, alors nous définissons les fichiers cibles à extraire :

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/Works.JPG)   

Puis nous appelons les différentes fonctions visant à extraire les données que nous ciblons en se concentrant sur les tables précises des bases de données à extraire
- Mots de passe (Fichier Login Data)
- Autofill (Fichier Web Data)
- Informations personnelles (Fichier Web Data)
- Cartes de crédits (Fichier Web Data)
- IBAN (Fichier Web Data)
- Cookies (Fichier Cookies)
- Historique (Fichier History)

Dans un second temps, nous allons pousser le vol de ces données en ne ciblant pas uniquement le profil par défaut (Default). Nous allons extraire les données des différents profils existants en parallèle :

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/Works2.JPG)   

A l'aide d'une boucle nous allons traiter tous les dossiers ayant pour nom "Profile " suivi d'un chiffre puis nous effectuons les mêmes tâches qu'auparavant.

Plutôt que de stocker les informations extraites dans la mémoire, nous les entreposons directement dans un fichier texte que nous enverrons par la suite. Souvent la majorité des malwares, par habitude, traitent ces tâches dans le dossier %TEMP% du PC. Cependant, Windows Defender semble s'être adapté à cette récurrence et le fait de créer un fichier temporaire dans cette partie augmente la détection du programme.

Ici, étant donné qu'il s'agit d'un document temporaire, je l'ai placé dans le dossier %DOCUMENTS% de la machine :

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/Works3.JPG)   


Autre point important, il existe plusieurs méthodes d'extraction. Certains infostealer vont chercher à traiter les données directement dans les fichiers se trouvant dans le dossier du navigateur, et d'autres les copieront dans un dossier externe avant de les traiter puis supprimer.

Dans notre cas, je les traite directement dans le dossier du navigateur ce qui implique de devoir fermer tout processus qui utiliserait ces bases de données :

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/Works4.JPG)   



Dans le traitement des bases de données nous procédons en nous attardant sur une table pour y extraire des colonnes spécifiques.
Par exemple, pour les cartes de crédit enregistrées dans le fichier Web Data, nous allons sur la table "credit_cards" puis  sélectionnons les colonnes qui nous semblent pertinentes :
- card_number_encrypted
- name_on_card
- expiration_month
- expiration_year

Pour la colonne "card_number_encrypted" les données sont chiffrées et nous avons donc besoin du fichier "Local State" pour déchiffrer cette colone. Ainsi, nous sélectionnons "encrypted_key" présente dans "os_crypt" dans ce fichier "Local State".

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/Works5.JPG)   


**Résultat du traitement**   

Ces données sont fictives et sont à titre d'exemple. J'ai sélectionné le "Profile 2" qui est notre environnement de test (toutes les données de mon navigateur chrome ont bien été extraites cependant)

Les mises en forme qui vont suivre respectent les canevas que l'on voit régulièrement dans les fichiers d'extraction de ces types de programmes.

Les mots de passe :

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/Resultat.JPG)   


Informations personnelles, cartes de crédits, IBAN et cookies :

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/Resultat2.JPG)   


Historique de navigation :

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/Resultat3.JPG)   





### Envoie des données

Dernièrement, il est commun de voir l'utilisation de webhook pour l'exfiltration des données volées en passant par des comptes Discord ou Télégram. Dans cet exemple, j'ai fait le choix d'utiliser un webhook discord.

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/SendIT.JPG)   

Les données se présentent de cette façon sur le discord :

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/CaptureDiscord.JPG)   


### Eventuelle stratégie de protection

La première porte d'entrée est et restera humaine. Cependant, une bonne configuration et gestion du parfeu et autres moyens de contrôle des connexions est ce qui permettra de mettre hors circuit ce type de logiciel.

Ces programmes ont pour habitude dans la majorité des cas d'envoyer les données sur certains webhook :
- Discord
- Telegram

Mais également sur des sites d'hébergement anonymes
- Anonfiles (Down)
- Io.files

etc ...

L'accès à ces sites n'est pas nécessaire en entreprise par exemple. La bonne stratégie selon moi est de créer certains filtres empêchant l'accès à ces DNS spécifiques.


## Présentation schématique de fonctionnement

![alt text](https://github.com/raphaelthief/WebBrowserVuln/blob/main/Pictures/Infostealer.jpg)   
