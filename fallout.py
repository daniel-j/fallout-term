
import urwid
from random import randrange

content = [
	[
		["out", "SECURITY RESET..."],
		["wait", 0.08]
	],
	[
		["wait", 0.1],
		["out",	"WELCOME TO ROBCO INDUSTRIES (TM) TERMLINK\n"],
		["in",	"SET TERMINAL/INQUIRE"],
		["wait", 0.2],
		["out",	"RIT-V300\n"],
		["in",	"SET FILE/PROTECTION-OWNER:RWED ACCOUNTS.F"],
		["in",	"SET HALT RESTART/MAINT"],
		["wait", 0.4],
		["out",	"Initializing Robco Industries(TM) MF Boot Agent v2.3.0\n"
				"RETROS BIOS\n"
				"RBIOS-4.02.08.00 52EE5.E7.E8\n"
				"Copyright 2201-2203 Robco Ind.\n"
				"Uppermem: 64 KB\n"
				"Root (5AB)\n"
				"Maintenance Mode\n"],
		["in",	"RUN DEBUG/ACCOUNTS.F"],
		["wait", 0.8]
	],
	[
		["out", "ROBCO INDUSTRIES (TM) TERMLINK PROTOCOL\nENTER PASSWORD NOW"]
	]
]

palette = [
	('inverted', 'black', 'light gray')
]

screen = 0
line = 0
pos = 0
delay = 0
state = 0

startAddress = randrange(0xF000, 0xFE7F)


#for screen in copy:
#	for item in screen:
#		s = item[1]
#		if item[0] == 'in':
#			s = ">"+s

addresses = [[], []]
addrPile = [urwid.Pile([]), urwid.Pile([])]

for i in range(16):
	for j in range(2):
		s = "0x" + (hex(startAddress+16*12*j+i*12).upper()[2:])+" ............"
		#txt = urwid.Text(s)
		addresses[j].append(s)


bootpile = urwid.Pile([])
attemptstxt = urwid.Text("")
columns = urwid.Columns([('fixed', 20, addrPile[0]), ('fixed', 20, addrPile[1]), urwid.Divider(" ")])


toppile = urwid.Pile([bootpile, attemptstxt, columns])


TYPE_SPEED = 0.055
OUTPUT_SPEED = 0.018

def typeText(loop):
	global content, screen, line, pos, bootpile, delay, state

	if state == 0:
		type = content[screen][line][0]
		value = content[screen][line][1]
	else:
		type = "out"
		value = addresses[screen][line]

	if line == 0 and pos == 0 and state == 0: # clear screen
		del bootpile.contents[:]

	if type == 'wait':
		delay = value
		bootpile.contents.append((urwid.Text(""), bootpile.options()))
		line += 1
	else:
		if type == 'out':
			delay = OUTPUT_SPEED
		else:
			delay = TYPE_SPEED

		s = value+" "
		if type == 'in':
			s = ">"+s
			if pos == 1:
				delay = 0.5

		if pos == 0:
			txt = urwid.Text("")
			if state == 0:
				bootpile.contents.append((txt, bootpile.options()))
			else:
				addrPile[screen].contents.append((txt, addrPile[screen].options()))
		else:
			if state == 0:
				txt = bootpile.contents[line][0]
			else:
				txt = addrPile[screen].contents[line][0]
		if pos == len(s) or (type == 'in' and pos == 0):
			txt.set_text(s[:pos])
		else:
			txt.set_text([s[:pos], ('inverted', " ")])
		pos += 1

		if pos == len(s)+1: # after a line
			pos = 0
			line += 1
			if type == 'in':
				delay = 0

	if (state == 0 and line == len(content[screen])) or (state == 1 and line == len(addresses[screen])): # after a screen
		line = 0
		screen += 1

	if state == 0:
		return screen < len(content)
	else:
		return screen < len(addresses)

def unhandled_input(key):
	if key in ('q', 'Q'):
		raise urwid.ExitMainLoop()
	#txt.set_text(repr(key))

def animate(loop, user_data=None):
	global delay, state, screen, line, pos
	if state == 0:
		cont = typeText(loop)
		if not cont:
			state = 1
			screen = 0
			line = 0
			pos = 0
			delay = 0
	elif state == 1:
		cont = typeText(loop)
		cont = typeText(loop)
		if not cont:
			state = 2
	if state < 2:
		animate_alarm = loop.set_alarm_in(delay, animate)

padding = urwid.Padding(toppile, left=0, right=0)
top = urwid.Filler(padding, 'top', top=0, bottom=0)
loop = urwid.MainLoop(top, palette, unhandled_input=unhandled_input)
animate(loop)

loop.run()

