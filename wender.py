import optparse, queue, random, sys, threading
import pygame
from pygame.locals import *

# ---------------------------------------------------------------------------------------

class CharSprite():
	def __init__(self, surface):
		self.width = surface.get_width()
		self.height = surface.get_height()
		self.base = surface
		self.colours = {
			"black" : colourise_surface(self.base, pygame.Color("black"))				,
			"white" : colourise_surface(self.base, pygame.Color("white"))				,
			"gray" : colourise_surface(self.base, pygame.Color(192,192,192,255))		,
			"red" : colourise_surface(self.base, pygame.Color("red"))					,
			"green" : colourise_surface(self.base, pygame.Color("green"))				,
			"yellow" : colourise_surface(self.base, pygame.Color("yellow"))				,
			"blue" : colourise_surface(self.base, pygame.Color("blue"))					,
			"cyan" : colourise_surface(self.base, pygame.Color("cyan"))					,
			"orange" : colourise_surface(self.base, pygame.Color("orange"))
			}

class MainWindow():
	def __init__(self, width, height, char_width, char_height, chars_filename):
		self.width = width
		self.height = height
		self.char_width = char_width
		self.char_height = char_height

		self._surface = pygame.display.set_mode((width * char_width, height * char_height))
		self._ascii_num = bytearray(width * height)
		self._sprites_list = load_sprites(char_width, char_height, chars_filename)

	def clear_all(self):
		self._ascii_num = bytearray(self.width * self.height)
		self._surface.fill(pygame.Color(0,0,0))

	def set(self, x, y, val, colour):
		if x < 0 or x >= self.width or y < 0 or y >= self.height:
			return
		if type(val) == str:
			val = ord(val[0])
		assert(val >= 0 and val <= 127)

		index = y * self.width + x
		self._ascii_num[index] = val

		screenx = x * self.char_width
		screeny = y * self.char_height

		sprite = self._sprites_list[val]
		if colour not in sprite.colours:
			colour = "white"

		self._surface.blit(sprite.colours[colour], (screenx, screeny))

	def clear(self, x, y):			# Clear a single spot
		self.set(x, y, 0, BLACK)

# ---------------------------------------------------------------------------------------

def colourise_surface(surface, colour):
	result = surface.copy()
	for x in range(result.get_width()):
		for y in range(result.get_height()):
			pix = result.get_at((x,y))
			if pix.r != 0 or pix.g != 0 or pix.b != 0:
				result.set_at((x,y), colour)
	return result

def load_sprites(w, h, filename):
	sprite_image = pygame.image.load(filename).convert_alpha()
	sprite_dict = dict()
	for c in range(0, 128):
		rect = pygame.Rect(w * c, 0, w, h)
		surface = sprite_image.subsurface(rect).copy().convert_alpha()
		sprite_dict[c] = CharSprite(surface)
	return sprite_dict

# ---------------------------------------------------------------------------------------

def start_sdl():
	pygame.mixer.pre_init(frequency = 22050, size = -16, channels = 16, buffer = 512)
	pygame.init()
	pygame.mixer.init()

def cleanexit(*args):
	print("QUIT")
	sys.stdout.flush()			# Apparently any and all lines we send need to be flushed
	pygame.quit()
	sys.exit()

def handle_sdl_events():
	for event in pygame.event.get():
		if event.type == QUIT:
			cleanexit()

def parse_args():

	global opts

	opt_parser = optparse.OptionParser()

	opt_parser.add_option(
	    "--width",
	    dest = "width",
	    type = "int",
	    help = "Width in characters [default: %default]")
	opt_parser.set_defaults(width = 80)

	opt_parser.add_option(
	    "--height",
	    dest = "height",
	    type = "int",
	    help = "Height in characters [default: %default]")
	opt_parser.set_defaults(height = 40)

	opt_parser.add_option(
	    "--charwidth",
	    dest = "charwidth",
	    type = "int",
	    help = "Pixel width of a character [default: %default]")
	opt_parser.set_defaults(charwidth = 8)

	opt_parser.add_option(
	    "--charheight",
	    dest = "charheight",
	    type = "int",
	    help = "Pixel height of a character [default: %default]")
	opt_parser.set_defaults(charheight = 12)

	opt_parser.add_option(
		"--charfile",
		dest = "charfile",
		type = "str",
		help = "Character file [default: %default]")
	opt_parser.set_defaults(charfile = "chars8x12.png")

	opts, __ = opt_parser.parse_args()

def main():
	start_sdl()
	parse_args()
	mainwindow = MainWindow(opts.width, opts.height, opts.charwidth, opts.charheight, opts.charfile)
	renderloop(mainwindow)

def input_thread(q):
	while 1:
		s = input()
		q.put(s)

def renderloop(win):

	input_queue = queue.Queue()

	threading.Thread(target = input_thread, daemon = True, kwargs = {"q" : input_queue}).start()

	n = 0

	while 1:

		try:
			s = input_queue.get(block = False)
		except queue.Empty:
			s = ""

		if s == "":
			pass
		elif s == "QUIT":
			cleanexit()
		elif s == "DRAW":
			pygame.display.update()
			print("OK")
			sys.stdout.flush()			# Apparently any and all lines we send need to be flushed
			n += 1
			pygame.display.set_caption(str(n))
		elif s == "CLEAR":
			win.clear_all()
		else:
			fields = s.split()
			c = int(fields[0])
			x = int(fields[1])
			y = int(fields[2])
			try:
				colour = fields[3]
			except:
				colour = "white"
			win.set(x, y, chr(c), colour)

		handle_sdl_events()

if __name__ == "__main__":
	main()
