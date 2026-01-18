import os
import random
import time
import pygame

class Window:
	def __init__(self):
		self.screenWidth = 1280
		self.screenHeight = 720
		self.window = pygame.display.set_mode((self.screenWidth, self.screenHeight))
		self.collections = []
		self.displayedCollections = []
		pygame.display.set_caption("Clip Manager")

		self.componentPressed = False

	def get_window(self):
		return self.window

	def add_collection(self, collection, show = True):

		self.collections.append(collection)

		if show:

			collectionList = self.displayedCollections
			collectionList.append(collection)

			self.displayedCollections = []

			while len(collectionList) > 0:

				lowestPriorityCollection = collectionList[0]

				for col in collectionList:
					if col.get_priority() < lowestPriorityCollection.get_priority():
						lowestPriorityCollection = col
				
				collectionList.remove(lowestPriorityCollection)
				self.displayedCollections.append(lowestPriorityCollection)

	def get_collection(self, id):
		for collection in self.collections:
			if collection.get_id() == id:
				return collection

	def update_collection(self, id, newCollection):
		oldCollection = self.get_collection(id)
		self.collections.remove(oldCollection)
		self.displayedCollections.remove(oldCollection)

		self.add_collection(newCollection)

	def show_collection(self, id):
		for collection in self.collections:
			if collection.get_id() == id:
				if collection in self.displayedCollections:
					print("tried to show collection with ID " + id + ", but collection is already showing")
				else:
					self.displayedCollections.append(collection)

	def hide_collection(self, id):
		for collection in self.collections:
			if collection.get_id() == id:
				if collection in self.displayedCollections:
					self.displayedCollections.remove(collection)
				else:
					print("tried to hide collection with ID " + id + ", but collection is already hidden")

	def update(self):
		self.window.fill((225, 225, 255))

		drawGrid = False
		if drawGrid:
			self.draw_grid()

		for collection in self.displayedCollections:
			collection.draw()
		
		pygame.display.update()

	def draw_grid(self):

		tileSize = 20		
		for i in range(0, (self.screenWidth // tileSize) + 1):
			x = i * tileSize
			pygame.draw.line(self.window, (0, 0, 0), (x, 0), (x, self.screenHeight))

		for i in range(0, (self.screenHeight // tileSize) + 1):
			y = i * tileSize
			pygame.draw.line(self.window, (0, 0, 0), (0, y), (self.screenWidth, y))

class Component:
	def draw(self):
		pass

	def action(self):
		pass

	def mouse_hovered_over(self):
		pass

class Collection(Component):
	def __init__(self, id, priority = 999):
		self.id = id
		self.components = []
		self.priority = priority

	def add_component(self, component):
		self.components.append(component)

	def get_components(self):
		return self.components
	
	def get_id(self):
		return self.id
	
	def get_priority(self):
		return self.priority

	def draw(self):
		for component in self.components:
			if component.mouse_hovered_over():
				if MOUSE.has_clicked(0): # 0 = left click
					component.action()

			component.draw()

class Rectangle(Component):
	def __init__(self, coordinates, size, colour = (150, 150, 150), outline = True):
		self.x = coordinates[0]
		self.y = coordinates[1]
		self.width = size[0]
		self.height = size[1]
		self.colour = colour
		self.outline = outline

	def draw(self):

		surface = WINDOW.get_window()

		pygame.draw.rect(surface, self.colour, ((self.x, self.y), (self.width, self.height)))

		if (self.outline):
			corners = (
				(self.x, self.y),
				(self.x + self.width, self.y),
				(self.x + self.width, self.y + self.height),
				(self.x, self.y + self.height)
			)

			for i in range(0, 4):
				startPos = corners[i]
				endPos = corners[(i + 1) % 4]

				pygame.draw.line(surface, (0, 0, 0), startPos, endPos, 3)

class SpecialRectangle(Rectangle):
	def __init__(self, coordinates, size, actionID, colour = (150, 150, 150), outline = True):
		Rectangle.__init__(self, coordinates, size, colour, outline)
		self.actionID = actionID

	def draw(self):
		Rectangle.draw(self)
		scrollStatus = MOUSE.get_scroll_status()
		if scrollStatus != 0:
			self.action(scrollStatus)

	def action(self, info):
		if self.actionID == "scroll":
			if info == 1: # If the scoll was upwards
				self.y -= 10
			else: # If the scoll was downwards
				self.y += 10


class Text(Component):
	def __init__(self, coordinates, fontSize, text):
		self.x = coordinates[0]
		self.y = coordinates[1]
		self.fontSize = fontSize
		self.text = text

		self.font = pygame.font.SysFont(UNIVERSAL_FONT, fontSize)
		self.textRender = self.font.render(self.text, True, (0, 0, 0))

	def draw(self):

		surface = WINDOW.get_window()
		surface.blit(self.textRender, (self.x, self.y))

class Button(Component):
	def __init__(self, coordinates, size, text = "", actionID = "", storage = "", colour = (150, 150, 150), highlightColour = (200, 200, 200)):
		self.x = coordinates[0]
		self.y = coordinates[1]
		self.width = size[0]
		self.height = size[1]
		self.text = text
		self.colour = colour
		self.highlightColour = highlightColour
		self.rectangleColour = colour

		self.actionID = actionID
		self.storage = storage

		fontSize = 30
		self.font = pygame.font.SysFont(UNIVERSAL_FONT, fontSize)
		self.textRender = self.font.render(self.text, True, (0, 0, 0))

		while self.textRender.get_size()[0] > (self.width - 10):
			fontSize -= 2

			self.font = pygame.font.SysFont(UNIVERSAL_FONT, fontSize)
			self.textRender = self.font.render(self.text, True, (0, 0, 0))

	def draw(self):

		surface = WINDOW.get_window()

		rectangle = Rectangle((self.x, self.y), (self.width, self.height), self.rectangleColour)
		rectangle.draw()

		textSize = self.textRender.get_size()
		textWidth = textSize[0]
		textHeight = textSize[1]

		textX = self.x + round((self.width / 2) - (textWidth / 2))
		textY = self.y + round((self.height / 2) - (textHeight / 2))
		surface.blit(self.textRender, (textX, textY))

	def mouse_hovered_over(self):
		mousePos = pygame.mouse.get_pos()
		if mousePos[0] >= self.x and mousePos[0] <= (self.x + self.width):
			if mousePos[1] >= self.y and mousePos[1] <= (self.y + self.height):
				self.rectangleColour = self.highlightColour
				return True
		self.rectangleColour = self.colour
		return False

	def action(self):

		if self.actionID == "open clicked folder":
			EXPLORER.update_path(self.storage)

		if self.text == "Group Manager":
			print("wow!! you clicked the group manager button!")
		else:
			print("you pressed a button. dunno which one tho.")

class Icon(Component):
	def __init__(self, coordinates, sequence, lineWidth):
		self.x = coordinates[0]
		self.y = coordinates[1]
		self.sequence = sequence
		self.lineWidth = lineWidth

	def draw(self):
		sequence = self.sequence

		previousCoords = sequence[0]
		for i in range(1, len(sequence)):
			coords = sequence[i]

			startPos = (previousCoords[0] + self.x, previousCoords[1] + self.y)
			endPos = (coords[0] + self.x, coords[1] + self.y)
			pygame.draw.line(
				surface = WINDOW.get_window(),
				color = (0, 0, 0),
				start_pos = startPos,
				end_pos = endPos,
				width = self.lineWidth)
			previousCoords = coords
			
class Mouse:
	def __init__(self):
		self.MBPressed = (False, False, False, False, False)
		self.MBPressedPreviously = (False, False, False, False, False)
		self.scrollStatus = 0
		self.previousScroll = 0
		self.scrolledPreviously = False

	def update(self):
		self.MBPressedPreviously = self.MBPressed
		self.MBPressed = pygame.mouse.get_pressed(5)

		if self.scrollStatus != 0:
			if self.scrolledPreviously == False:
				self.scrolledPreviously = True
			else:
				self.scrollStatus = 0
				self.scrolledPreviously = False

	def has_clicked(self, mouseButton: int = 0):
		if self.MBPressed[mouseButton]: # If mouse button is being pressed
			if not self.MBPressedPreviously[mouseButton]: # If the mouse button wasnt being pressed in the previous iteration
				return True
		return False

	def get_scroll_status(self):
		return self.scrollStatus

	def scrolled(self, scrollType):
		self.scrollStatus = scrollType

class Explorer:
	def __init__(self, drawPriority = 999):
		self.currentPath = PATH
		self.previousPaths = []
		self.drawPriority = drawPriority

		self.create_clip_explorer_collection()

	def update_path(self, path):
		self.previousPaths.append(self.currentPath)
		self.currentPath = path
		newCollection = self.create_clip_explorer_collection()
		WINDOW.update_collection("clip explorer", newCollection)

	def search_directory(self, path):
		videos = []
		folders = []

		files = os.listdir(path)
		for file in files:
			splitFile = file.split(".")
			if len(splitFile) == 1:
				fileExtension = ""
			else:
				fileExtension = splitFile[-1]

			if fileExtension == VIDEO_FORMAT:
				fileLocation = os.path.join(path, file)
				videos.append(fileLocation)

			elif fileExtension == "": # If the file is a folder
				fileLocation = os.path.join(path, file)
				folders.append(fileLocation)

		return videos, folders

	def create_clip_explorer_collection(self):
		clipExplorer = Collection("clip explorer", self.drawPriority)

		searchResult = self.search_directory(self.currentPath)

		videos = searchResult[0]
		folders = searchResult[1]

		i = 0
		for folder in folders:
			clipExplorer.add_component(self.create_folder_collection(folder, i))
			i += 1	

		return clipExplorer

	def create_folder_collection(self, folderLocation, index):

		baseCoords = (290 + (320 * (index % 3)), 150 + (100 * (index // 3)))

		folderName = os.path.basename(folderLocation)
		items = len(os.listdir(folderLocation))

		folderCollection = Collection("folder")

		folderCollection.add_component(Button(
			coordinates = baseCoords,
			size = (300, 80),
			actionID = "open clicked folder",
			storage = folderLocation
		))

		folderCollection.add_component(Icon(
			coordinates = baseCoords,
			sequence = ((10, 20), (10, 70), (90, 70), (90, 15), (40, 15), (35, 20), (10, 20), (10, 10), (35, 10), (40, 15)),
			lineWidth = 4
		))

		folderCollection.add_component(Text(
			coordinates = (baseCoords[0] + 110, baseCoords[1] + 10),
			fontSize = 24,
			text = folderName
		))

		folderCollection.add_component(Text(
			coordinates = (baseCoords[0] + 110, baseCoords[1] + 35),
			fontSize = 24,
			text = "Items: " + str(items)
		))

		return folderCollection

# Global Variables
pygame.font.init()
UNIVERSAL_FONT = "Calibri"
PATH = os.path.dirname(os.path.realpath(__file__))
VIDEO_FORMAT = "mp4" 

WINDOW = Window()
MOUSE = Mouse()
EXPLORER = Explorer(drawPriority = 2)

# Collections

CLIP_SELECTED_COLLECTION = Collection("clip selected", priority = 3)
if True:
	'''
	#Button(20, 120, 220, 100, "Group Manager"),
	CLIP_SELECTED_COLLECTION.add_component(Button(
		coordinates = (20, 240),
		size = (220, 100),
		text = "Send to Clip Group"
	))
	'''

	CLIP_SELECTED_COLLECTION.add_component(Button(
		coordinates = (20, 360),
		size = (220, 100),
		text = "Open"
	))

	CLIP_SELECTED_COLLECTION.add_component(Button(
		coordinates = (20, 480),
		size = (220, 100),
		text = "Rename"
	))

DEFAULT_COLLECTION = Collection("default", priority = 3)
if True:

	DEFAULT_COLLECTION.add_component(Rectangle(
		coordinates = (260, 462),
		size = (1000, 258),
		colour = (225, 225, 255),
		outline = False
	)) # This rectangle covers any folders / videos that should not be showing below the clip explorer

	DEFAULT_COLLECTION.add_component(Rectangle(
		coordinates = (260, 0),
		size = (1000, 119),
		colour = (225, 225, 255),
		outline = False
	))

	DEFAULT_COLLECTION.add_component(Button(
		coordinates = (1040, 600),
		size = (220, 100),
		text = "Open Random Clip"
	))

	DEFAULT_COLLECTION.add_component(Button(
		coordinates = (260, 40),
		size = (120, 60),
		text = "Back"
	))

	DEFAULT_COLLECTION.add_component(Button(
		coordinates = (400, 40),
		size = (120, 60),
		text = "Forward"
	))

	DEFAULT_COLLECTION.add_component(Rectangle(
		coordinates = (540, 40),
		size = (720, 60)
	))

	DEFAULT_COLLECTION.add_component(Rectangle(
		coordinates = (260, 480),
		size = (1000, 100)
	))

	DEFAULT_COLLECTION.add_component(Rectangle(
		coordinates = (20, 600),
		size = (1000, 100)
	))

EXPLORER_COLLECTION = Collection("explorer", priority = 1)
if True:
	EXPLORER_COLLECTION.add_component(Rectangle(
		coordinates = (260, 120),
		size = (1000, 340)
	))

	'''
	EXPLORER_COLLECTION.add_component(SpecialRectangle(
		coordinates = (1220, 140),
		size = (20, 100),
		colour = (255, 255, 255),
		actionID = "scroll"
	))
	'''
	
WINDOW.add_collection(EXPLORER_COLLECTION)
WINDOW.add_collection(EXPLORER.create_clip_explorer_collection()) # Clip Explorer Collection priority defined in Explorer class creation
WINDOW.add_collection(DEFAULT_COLLECTION)
WINDOW.add_collection(CLIP_SELECTED_COLLECTION)

# Main Loop
clock = pygame.time.Clock()
run = True

while run:

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		elif event.type == pygame.MOUSEWHEEL:
			MOUSE.scrolled(event.y)

	MOUSE.update()
	WINDOW.update()

	clock.tick(60)

pygame.quit()