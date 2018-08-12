from enum import Enum, auto

import pyglet

BORDER_COLOR = (0, 0.75, 1, 1)
BORDER_HIGHLIGHT_COLOR = (0, 1, 0, 1)

BG_COLOR = (0, 0, 0, 1)

BREAK_ON_NEXT_DISPATCHER_FOUND = True

def make_rectangle_verticle_sequence(x1, y1, x2, y2):
	return (x1, y1, x2, y1, x2, y2, x1, y2)

class EventTypes(Enum):
	PRE_DRAW = auto()
	POST_DRAW = auto()
	
	MOUSE_MOTION = auto()
	MOUSE_RELEASE = auto()
	MOUSE_PRESS = auto()
	MOUSE_DRAG = auto()
	
class GuiNode():
	def __init__(self, parent=None, rx=0, ry=0, rwidth=1, rheight=1, window=None, **kwargs):
		self.parent = parent
		self.children = []
		
		self.window = window
		
		self.rx = rx
		self.ry = ry
		self.rw = rwidth
		self.rh = rheight
		self.x = 0
		self.y = 0
		self.w = 0
		self.h = 0
		self.border = None
		
		self.draw_border = True #TODO
		
		if self.parent is not None:
			self.parent.add_child(self)
		
		if (self.window is not None) and self.window.batch is not None:
			self.update_size()
	
	def convert_to_abs(self, rx, ry):
		x = self.x + self.w * rx
		y = self.y + self.h * ry
		return x, y
	
	def convert_to_abs_hw(self, rx, ry):
		return self.w*rx, self.h*ry
	
	def update_border(self):
		if self.border is None and self.draw_border:
			print(self.x, self.y, self.w, self.h)
			self.border = self.window.draw_rectangle_outline(self.x+1, self.y+1, self.x+self.w, self.y+self.h, BORDER_COLOR)
		else:
			self.border.vertices = make_rectangle_verticle_sequence(self.x+1, self.y+1, self.x+self.w, self.y+self.h)
			#TODO
	
	def update_size(self):
		print("Updating", self)
		if self.parent is not None:
			self.x, self.y = self.parent.convert_to_abs(self.rx, self.ry)
			self.w, self.h = self.parent.convert_to_abs_hw(self.rw, self.rh)
		elif self.window is not None:
			self.x, self.y = 0, 0
			self.w, self.h = self.window.get_size()
		
		for chld in self.children:
			chld.update_size()
		
		self.update_border()
	
	def contains(self, x, y):
		return ((self.x <= x <= self.x + self.w) and 
			(self.y <= y <= self.y + self.h))
	
	def dispatch_to_all(self, event, args):
		for chld in self.children:
			chld.dispatch_to_all(event, args)
	
	def dispatch_event(self, event, args):
		pass
	
	def dispatch_click(self, x, y, button, mod):
		for chld in self.children:
			if chld.contains(x, y):
				chld.dispatch_click(x, y, button, mod)
				if BREAK_ON_NEXT_DISPATCHER_FOUND:
					break
	
	def dispatch_hover(self, x, y):
		for chld in self.children:
			if chld.contains(x, y):
				chld.dispatch_hover(x, y)
				if BREAK_ON_NEXT_DISPATCHER_FOUND:
					break
	
	def add_child(self, obj):
		self.children.append(obj)
		if self.window is not None:
			obj.window = self.window

class GuiNodeHighlighted(GuiNode):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.highlighted = False
		self.window.node.dispatch_events_to.append(self)
	
	def highlight(self):
		if not self.highlighted:
			self.highlighted = True
			if self.border is not None:
				self.border.colors = BORDER_HIGHLIGHT_COLOR * 4
	
	def unlight(self):
		if self.highlighted:
			self.highlighted = False
			if self.border is not None:
				self.border.colors = BORDER_COLOR * 4
	
	def dispatch_event(self, event, args):
		if self.highlighted and (event is EventTypes.MOUSE_MOTION):
			if not self.contains(*args[0:2]):
				self.unlight()
		#super().dispatch_to_all(event, args)
	
	def dispatch_hover(self, x, y):
		super().dispatch_hover(x, y)
		self.highlight()

class GuiNodeButton(GuiNodeHighlighted):
	def __init__(self, *args, **kwargs):
		"""Has 'action' keyword - sets up button callback"""
		super().__init__(*args, **kwargs)
		self.action = kwargs["action"] if "action" in kwargs else None
	def dispatch_click(self, x, y, button, mod):
		super().dispatch_click(x, y, button, mod)
		if self.action is not None:
			self.action()

class GuiNodeText(GuiNode)

class MainGuiNode(GuiNode):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.selected = None
		self.dispatch_events_to = []
	
	def dispatch_to_all(self, event, args):
		
		
		super().dispatch_to_all(event, args)
	
	def dispatch_event(self, event, args):
		if event is EventTypes.MOUSE_MOTION:
			self.dispatch_hover(*args[0:2])
		elif event is EventTypes.MOUSE_PRESS:
			self.dispatch_click(*args)
		
		if self.selected is not None:
			self.selected.dispatch_event(event, args)
		for dispatcher in self.dispatch_events_to:
			dispatcher.dispatch_event(event, args)
			
class Window(pyglet.window.Window):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.batch = pyglet.graphics.Batch()
		self.node = MainGuiNode(window=self)
	
	
	def draw_rectangle_outline(self, x1, y1, x2, y2, color):
		#print("Rectangle at", x1, y1, x2, y2)
		return self.batch.add_indexed(4, pyglet.gl.GL_LINES, None,
			(0, 1, 1, 2, 2, 3, 3, 0),
			('v2f', (x1, y1, x2, y1, x2, y2, x1, y2)), #make_rectangle_verticle_sequence could be used
			('c4f', color*4)
		)
		
	def on_resize(self, x, y):
		super().on_resize(x, y)
		self.node.update_size()
	
	def on_draw(self):
		self.node.dispatch_event(EventTypes.PRE_DRAW, None)
		pyglet.gl.glClearColor(BG_COLOR)
		self.clear()
		self.batch.draw()
		self.node.dispatch_event(EventTypes.POST_DRAW, None)
	
	def on_mouse_motion(self, *args):
		self.node.dispatch_event(EventTypes.MOUSE_MOTION, args)
	
	def on_mouse_press(self, *args):
		self.node.dispatch_event(EventTypes.MOUSE_PRESS, args)
	
	def on_mouse_drag(self, *args):
		self.node.dispatch_event(EventTypes.MOUSE_DRAG, args)
	
	def on_mouse_release(self, *args):
		self.node.dispatch_event(EventTypes.MOUSE_RELEASE, args)
		

if __name__ == "__main__":
	window = Window(resizable=True)
	print("Created window")
	node = GuiNode(window.node, 0.1, 0.1, 0.5, 0.4)
	button = GuiNodeButton(node, 0, 0, 1, 0.5, action=lambda :print("Pressed"))
	#window.draw_rectangle_outline(10, 10, 200, 200, (1, 0.5, 0.5, 1))
	pyglet.clock.schedule_interval(lambda dt:True, 1/20)
	pyglet.app.run()
