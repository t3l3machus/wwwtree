#!/bin/python3
#
# Author: Panagiotis Chartas (t3l3machus)
# https://github.com/t3l3machus

import ssl, os, re, argparse
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from platform import system as get_system_type
from sys import exit as _exit, argv
from warnings import filterwarnings
import netifaces as ni
from uuid import uuid4;

filterwarnings("ignore", category = DeprecationWarning)

def move_on():
	pass


# Enable colors if Windows 
WINDOWS = True if get_system_type() == 'Windows' else False
os.system('') if WINDOWS else move_on()


''' Colors '''
LINK = '\033[1;38;5;37m'
BROKEN = '\033[48;5;234m\033[1;31m'
HIGHLIGHT = '\033[1;38;5;43m'
GREEN = '\033[38;5;47m'
DIR = '\033[1;38;5;12m'
ORANGE = '\033[0;38;5;214m'
MAIN = '\033[38;5;85m'
END = '\033[0m'
BOLD = '\033[1m'


''' MSG Prefixes '''
INFO = f'{MAIN}Info{END}'
DEBUG = f'{ORANGE}Debug{END}'


def exit_with_msg(msg):
	print('[' + DEBUG  + '] ' + msg)
	_exit(1)



def print_banner():
	
	print('\r')
	padding = '  '

	W = [[' ', '┬', ' ', '┬'], [' ', '│','│','│'], [' ', '└','┴','┘']]
	T = [[' ', '┌','┬','┐'], [' ', ' ','│',' '], [' ', ' ','┴',' ']]
	R = [[' ', '┬','─','┐'], [' ', '├','┬','┘'], [' ', '┴','└','─']]
	E = [[' ', '┌', '─', '┐'], [' ', '├', '┤',' '], [' ', '└','─','┘']]

	banner = [W,W,W,T,R,E,E]
	final = []
	init_color = 1
	txt_color = init_color
	cl = 0

	for charset in range(0, 3):
		for pos in range(0, len(banner)):
			for i in range(0, len(banner[pos][charset])):
				clr = '\033[38;5;' + str(txt_color) + 'm'
				char = clr + banner[pos][charset][i]
				final.append(char)
				cl += 1
				txt_color = txt_color + 36 if cl <= 3 else txt_color

			cl = 0

			txt_color = init_color
		init_color += 31

		if charset < 2: final.append('\n   ')

	print('   ' + ''.join(final))
	print(END + padding +'                by t3l3machus\n')


# -------------- Arguments & Usage -------------- #
parser = argparse.ArgumentParser()

parser.add_argument("-r", "--root-path", action="store", help = "The root path to host.", required = True)
parser.add_argument("-i", "--interface", action="store", help = "The interface to host.", required = True)
parser.add_argument("-l", "--level", action="store", help = "Descend only level directories deep.", type = int)
parser.add_argument("-p", "--port", action="store", help = "Server port (default: 80)", type = int)
parser.add_argument("-k", "--keywords", action="store", help = "Comma separated keywords to search for in file names.")
parser.add_argument("-A", "--ascii", action="store_true", help = "Use ASCII instead of extended characters (use this in case of \"UnicodeEncodeError: 'ascii' codec...\" along with -q).")
parser.add_argument("-q", "--quiet", action="store_true", help = "Do not print the banner on startup.")

args = parser.parse_args()

# Parse interface
try:
	lhost = ni.ifaddresses(args.interface)[ni.AF_INET][0]['addr']
	
except:
	exit_with_msg('Error parsing interface.')


# Parse server port
server_port = 80 if not args.port else args.port

# Parse depth level
if isinstance(args.level, int):
	depth_level = args.level if (args.level > 0) else exit_with_msg('Level (-l) must be greater than 0.') 

else:
	depth_level = 4096


# Parse keyword(s)
keywords = []

if args.keywords:
	for word in args.keywords.split(","):
		if len(word.strip()) > 0:
			keywords.append(word.strip()) 
			
	verify = [k for k in keywords if k.strip() != '']	
	
	if not len(verify):
		exit_with_msg("Illegal keyword(s) value(s).")


ASCII = False
follow_links = True

# File extensions to exclude from the web tree
hide_extensions = ['zip', 'txt', 'rar', 'tar', 'gz', 'html', 'css', 'font', 'doc', 'docx', 'csv', 'xls', \
'xlsx', 'xml', 'pdf', 'pack', 'idx', 'sample', 'gif', 'png', 'jpeg', 'jpg', 'gif', 'md', 'dmp', '7z', 'bz2', \
'xz', 'deb', 'img', 'iso', 'vmdk', 'ovf', 'ova', 'egg', 'log', 'otf', 'mp3', 'mp4', 'conf', 'yml', 'gitignore']

# Directories to exclude from the web tree
hide_dirs = ['.git']



# Define depth level
if isinstance(args.level, int):
	depth_level = args.level if (args.level > 0) else exit_with_msg('Level (-l) must be greater than 0.') 

else:
	depth_level = 4096


def fake2realpath(path, target):
	
	sep_count = target.count(".." + os.sep)
	regex_chk_1 = "^" + re.escape(".." + os.sep)
	regex1_chk_2 = "^" + re.escape("." + os.sep)
	regex1_chk_3 = "^" + re.escape(os.sep)
	
	if (re.search(regex_chk_1, target)) and (sep_count <= (path.count(os.sep) - 1)):
		dirlist = [d for d in path.split(os.sep) if d.strip()]
		dirlist.insert(0, os.sep)

		try:
			realpath = ''

			for i in range(0, len(dirlist) - sep_count ):
				realpath = realpath + (dirlist[i] + os.sep) if dirlist[i] != "/" else dirlist[i]

			realpath += target.split(".." + os.sep)[-1]
			return str(Path(realpath).resolve())
			
		except:
			return None

	elif re.search(regex1_chk_2, target):
		return str(Path((path + (target.replace("." + os.sep, "")))).resolve())
	
	elif not re.search(regex1_chk_3, target):
		return str(Path(path + target).resolve())
	
	else:
		return str(Path(target).resolve())



def adjustUnicodeError():
	exit_with_msg('The system seems to have an uncommon default encoding. Restart wwwtree with options -q and -A to resolve this issue.')


child = (chr(9500) + (chr(9472) * 2) + ' ') if not ASCII else '|-- '
child_last = (chr(9492) + (chr(9472) * 2) + ' ') if not ASCII else '\-- '
parent = (chr(9474) + '   ') if not ASCII else '|   '


def wwwtree(root_dir, intent = 0, depth = '', depth_level = depth_level):

	try:
		global total_dirs_processed, total_files_processed, lhost
		root_dirs = next(os.walk(root_dir))[1]
		root_files = next(os.walk(root_dir))[2]
		total_dirs = len(root_dirs)
		total_files = len(root_files)
		symlinks = []
		recursive = []
		print('\r' + BOLD + GREEN + root_dir + END + ' (web root)') if not intent else move_on()


		''' Handle symlinks '''
		for d in root_dirs:
			if os.path.islink(root_dir + d):
				symlinks.append(d)
		
		
		''' Process files '''
		root_files.sort()
		
		for i in range(0, total_files):
			
			if root_files[i].count('.'):
				ext = root_files[i].rsplit('.', 1)[-1]
				
				if ext.lower() in hide_extensions:
					continue
					
			filename = ('http://' + lhost + root_dir.replace(args.root_path, '/') + HIGHLIGHT + root_files[i] + END)

			''' Print file branch '''
			if not keywords:
				print(depth + child + filename + END) if (i < (total_files + total_dirs) - 1) \
				else print(depth + child_last + filename + END)
				
			else:
				for kword in keywords:
					if re.search(kword.lower(), root_files[i].lower()):
						print(depth + child + filename + END) if (i < (total_files + total_dirs) - 1) \
						else print(depth + child_last + filename + END)
						break


		''' Process dirs '''
		root_dirs.sort()
		
		for i in range(0, total_dirs):

			if root_dirs[i] in hide_dirs:
				continue
			
			joined_path = root_dir + root_dirs[i]
			is_recursive = False
			directory = (root_dirs[i] + os.sep)
						
			''' Access permissions check '''
			try:
				sub_dirs = len(next(os.walk(joined_path))[1])
				sub_files = len(next(os.walk(joined_path))[2])
				errormsg = ''
			
			except StopIteration:
				sub_dirs, sub_files = 0, 0
				errormsg = ' [error accessing dir]'
						
			
			''' Check if symlink and if target leads to recursion '''
			if root_dirs[i] in symlinks:
				symlink_target = target = os.readlink(joined_path)
				target = fake2realpath(root_dir, target)			
				is_recursive = ' [recursive, not followed]' if target == root_dir[0:-1] else ''
				
				if len(is_recursive):
					recursive.append(joined_path)
					
				print(depth + child + LINK + directory + END + ' -> ' + DIR + symlink_target + END + is_recursive + errormsg) if i < total_dirs - 1 \
				else print(depth + child_last + LINK + directory + END + ' -> ' + DIR + symlink_target + END + is_recursive + errormsg)
				
			else:
				print(depth + child + DIR + directory + END + errormsg) if i < total_dirs - 1 \
				else print(depth + child_last + DIR + directory + END + errormsg)

			''' Iterate next dir '''
			if (not follow_links and root_dirs[i] not in symlinks) or (follow_links and not is_recursive):
				if (sub_dirs or sub_files) and (intent + 1) < depth_level:
					tmp = depth
					depth = depth + parent if i < (total_dirs - 1) else depth + '	'
					wwwtree(joined_path + os.sep, intent + 1, depth)
					depth = tmp
			

	except StopIteration:
		print('\r' + DIR + root_dir + END + ' [error accessing dir]')
		
	except UnicodeEncodeError:
		adjustUnicodeError()

	except KeyboardInterrupt:
		exit_with_msg('Keyboard interrupt.')
		
	except Exception as e:
		exit_with_msg('Something went wrong. Consider creating an issue about this in the original repo (https://github.com/t3l3machus/wwwtree)\n' + BOLD + 'Error Details' + END +': ' + str(e))



# -------------- http Server -------------- #
class HTTPRequestHandler(BaseHTTPRequestHandler):
	
	protocol_version = 'HTTP/1.1'
	global path
	
	def do_GET(self):

		try:
			
			requested_resource = open(args.root_path[0:-1] + self.path, 'rb')
			data = requested_resource.read()
			requested_resource.close()
			self.send_response(200)
			self.send_header('Access-Control-Allow-Origin', '*')
			self.end_headers()
			self.wfile.write(bytes(data))
			return
			
		except:
			self.send_response(404)
			self.end_headers()
			self.wfile.write(bytes('NOT FOUND', "utf-8"))
				
			
		
	def do_PUT(self):
		
		resource = self.path.split("/")[-1]
		
		if resource.endswith('/') or not resource:
			self.send_response(400)
			self.end_headers()
			self.wfile.write("You need to provide a file name to write in.\n".encode())
			return
			
		else:
					
			file_path = '/tmp/' + resource
			
			# Check if file exists
			file_path = (file_path + '_' + uuid4().hex[0:6]) if os.path.exists('/tmp/' + resource) else file_path
						
			length = int(self.headers['Content-Length'])
			
			with open(file_path, 'wb') as f:
				f.write(self.rfile.read(length))
				
			self.send_response(201, "Created")
			self.wfile.write("File received.\n".encode())
			return
			


def generate_webtree(path):
	
	root_dir = path if path[-1] == os.sep else path + os.sep	

	if os.path.exists(root_dir):
		wwwtree(root_dir)
		
	else:
		exit_with_msg('Directory does not exist.')

	
	
def main(path, bind_address = '0.0.0.0', bind_port = server_port):

	try:
		httpd = HTTPServer((bind_address, bind_port), HTTPRequestHandler)

	except OSError:
		exit_with_msg(f'Port {bind_port} seems to already be in use.\n')		
	
	httpd = Thread(target = httpd.serve_forever, args = ())
	httpd.daemon = True
	httpd.start()
	
	print_banner() if not args.quiet else move_on()
	print(f'[{INFO}] Http server listening on {ORANGE}{bind_address}{END}:{ORANGE}{bind_port}{END}, Interface addr: {ORANGE}{lhost}{END}')
	print(f'[{INFO}] Press ENTER to exit.\n')
	
	generate_webtree(path)
	print(f'\n------- {ORANGE}Server access log{END} -------')
	
	try:
		inp = input()
		_exit(0)
		
	except KeyboardInterrupt:
		_exit(0)



if __name__ == '__main__':
	main(args.root_path)
