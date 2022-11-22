# wwwtree
[![Python](https://img.shields.io/badge/Python-%E2%89%A5%203.x-yellow.svg)](https://www.python.org/) 
<img src="https://img.shields.io/badge/Developed%20on-kali%20linux-blueviolet">
[![License](https://img.shields.io/badge/License-MIT-red.svg)](https://github.com/t3l3machus/wwwtree/blob/main/LICENSE)
<img src="https://img.shields.io/badge/Maintained%3F-Yes-96c40f">

## Purpose
A utility to assist pentesters with transfering files back & forth victim machines by web hosting directories and auto appending URL prefixes to every file and more.

## Description
wwwtree does the following:
 - hosts a specified root directory and prints the contents in a tree-like format. Every file is translated to it's equivalent server URL so you can quickly copy it and use a web client to transfer it to the victim.
 - Filters out files that contain specific substrings based on user provided keywords (use `-k` to parse comma seperated values).
 - Automatically hides from the output files and folders that are most likely not in the scope of enumeration / exploitation (e.g., txt, yml, docx files or .git directories). You can control this behaviour by editing the list variables `hide_extensions` and `hide_dirs` in the source.
 - The custom python http server powering this tool supports PUT requests and by default saves files in `/tmp` (you can change that in the source)
