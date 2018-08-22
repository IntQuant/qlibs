from enum import Enum, auto

import pyglet

BORDER_COLOR = (0, 0.75, 1, 1)
BORDER_HIGHLIGHT_COLOR = (0, 1, 0, 1)

BG_COLOR = (0, 0, 0, 1)
CARET_COLOR = (255, 255, 255)

BREAK_ON_NEXT_DISPATCHER_FOUND = True

INC_TEXT_HORIZONTAL_MOD = 2

def make_rectangle_verticle_sequence(x1, y1, x2, y2):
	return (x1, y1, x2, y1, x2, y2, x1, y2)

class EventTypes(Enum):
	PRE_DRAW = auto()
	POST_DRAW = auto()
	
	MOUSE_MOTION = auto()
	MOUSE_RELEASE = auto()
	MOUSE_PRESS = auto()
	MOUSE_DRAG = auto()
	
	TEXT = auto()
	TEXT_MOTION = auto()
	TEXT_MOTION_SELECT = auto()
	
	
class GuiNode():
	def __init__(self, parent=None, rx=0, ry=0, rwidth=1, rheight=1, window=None, **kwargs):
		self.parent = parent
		self.children = []
		
		self.shown = True
		self.recieves_events = True
		
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
			if self.window.node is not None:
				self.window.node.nodes.append(self)
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
	def update_size(self):
		#print("Updating", self)
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
		pass
	def dispatch_event(self, event, args):
		pass
	def dispatch_click(self, x, y, button, mod):
		for chld in self.children:
			if chld.contains(x, y) and chld.recieves_events:
				chld.dispatch_click(x, y, button, mod)
				if BREAK_ON_NEXT_DISPATCHER_FOUND:
					break
	def dispatch_hover(self, x, y):
		for chld in self.children:
			if chld.contains(x, y) and chld.recieves_events:				
				chld.dispatch_hover(x, y)
				if BREAK_ON_NEXT_DISPATCHER_FOUND:
					break
	def add_child(self, obj):
		self.children.append(obj)
		if self.window is not None:
			obj.window = self.window
	def delete(self):
		if self.border is not None:
			self.border.delete()
		if self.window is not None:
			self.window.node.nodes.remove(self)
		del self.children
	def __del__(self):
		self.delete()
	def hide(self):
		if self.shown:
			self.shown = False
			self.draw_border = False
			if self.window is not None and self.window.node.selected is self:
				self.window.node.selected = None
			
			if self.border is not None:
				self.border.delete()
				del self.border
		for chld in self.children:
			chld.hide()
		
		self.recieves_events = True
	def show(self):
		if not self.shown:
			self.shown = True
			self.draw_border = True
			self.update_border()
		
		for chld in self.children:
			chld.show()	
		
		self.recieves_events = False

class GuiNodeHighlighted(GuiNode):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.highlighted = False	
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

class GuiNodeHighlightedByHover(GuiNodeHighlighted):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)	
	def dispatch_to_all(self, event, args):
		if self.highlighted and (event is EventTypes.PRE_DRAW):
			if not self.contains(*self.window.mouse_pos):
				self.unlight()	
	def dispatch_hover(self, x, y):
		super().dispatch_hover(x, y)
		self.highlight()

class GuiNodeButton(GuiNodeHighlightedByHover):
	def __init__(self, *args, **kwargs):
		"""Has 'action' keyword - sets up button callback"""
		super().__init__(*args, **kwargs)
		self.action = kwargs["action"] if "action" in kwargs else None
	def dispatch_click(self, x, y, button, mod):
		super().dispatch_click(x, y, button, mod)
		if self.action is not None:
			self.action()

class GuiNodeIncText(GuiNodeHighlighted):
	def __init__(self, *args, **kwargs):
		"""
		  Additional keywords:
		   document - sets the document to use
		"""
		self.layout = None
		
		super().__init__(*args, **kwargs)
		
		self.document = kwargs["document"] if "document" in kwargs else pyglet.text.document.UnformattedDocument("")
		if "document" not in kwargs:
			self.document.set_style(0, len(self.document.text), dict(color=(255, 255, 255, 255)))
		
		self.layout = pyglet.text.layout.IncrementalTextLayout(
			self.document, self.w, self.h, multiline=True, batch=self.window.batch)
		self.caret = pyglet.text.caret.Caret(self.layout)
		self.caret.color = CARET_COLOR
		self.caret.visible = False
		
		self.update_layout()	
	def highlight(self):
		super().highlight()
		self.caret.visible = True
	def unlight(self):
		super().unlight()
		self.caret.visible = False		
	def dispatch_to_all(self, event, args):
		if self.highlighted and (event is EventTypes.PRE_DRAW):
			if self.window.node.selected is not self:
				self.unlight()	
	def dispatch_click(self, x, y, button, mod):
		super().dispatch_click(x, y, button, mod)
		self.window.node.selected = self
		self.highlight()
	def dispatch_event(self, event, args):
		if self.window.node.selected is self:
			if event is EventTypes.MOUSE_PRESS:
				self.caret.on_mouse_press(*args)
			elif event is EventTypes.MOUSE_DRAG:
				self.caret.on_mouse_drag(*args)
			elif event is EventTypes.TEXT:
				self.caret.on_text(*args)
			elif event is EventTypes.TEXT_MOTION:
				self.caret.on_text_motion(*args)
			elif event is EventTypes.TEXT_MOTION_SELECT:
				self.caret.on_text_motion_select(*args)
	def update_size(self):
		super().update_size()
		if self.layout is not None:
			self.update_layout()	
	def update_layout(self):
		font = self.document.get_font()
		height = font.ascent - font.descent
		
		self.layout.width = self.w - INC_TEXT_HORIZONTAL_MOD
		self.layout.height = self.h
		self.layout.x = self.x + INC_TEXT_HORIZONTAL_MOD
		self.layout.y = self.y# + height
	def delete(self):
		super().delete()
		self.layout.delete()

#TODO
class GuiNodeListPlacer(GuiNode):
	def __init__(self, *args, step=0.1, vetrical=True, **kwargs):
		super().__init__(*args, **kwargs)
		self.step = step
		self.vertical = vertical

class MainGuiNode(GuiNode):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.selected = None
		self.dispatch_events_to = []
		self.nodes = []
	def dispatch_to_all(self, event, args):
		for node in self.nodes:
			if node.recieves_events:
				node.dispatch_to_all(event, args)
	def dispatch_event(self, event, args):
		if event is EventTypes.MOUSE_MOTION:
			self.dispatch_hover(*args[:2])
		elif event is EventTypes.MOUSE_PRESS:
			self.dispatch_click(*args)
		if self.selected is not None:
			self.selected.dispatch_event(event, args)
		for dispatcher in self.dispatch_events_to:
			if dispatcher.recieves_events:
				dispatcher.dispatch_event(event, args)
			
class Window(pyglet.window.Window):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.node = None
		self.batch = pyglet.graphics.Batch()
		self.node = MainGuiNode(window=self)
		self.mouse_pos = (0, 0)
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
		self.node.dispatch_to_all(EventTypes.PRE_DRAW, None)
		pyglet.gl.glClearColor(*BG_COLOR)
		self.clear()
		self.batch.draw()
		self.node.dispatch_to_all(EventTypes.POST_DRAW, None)
	def on_mouse_motion(self, *args):
		self.mouse_pos = args[:2]
		self.node.dispatch_event(EventTypes.MOUSE_MOTION, args)	
	def on_mouse_press(self, *args):
		self.node.dispatch_event(EventTypes.MOUSE_PRESS, args)	
	def on_mouse_drag(self, *args):
		self.node.dispatch_event(EventTypes.MOUSE_DRAG, args)
	def on_mouse_release(self, *args):
		self.node.dispatch_event(EventTypes.MOUSE_RELEASE, args)	
	def on_text(self, *args):
		self.node.dispatch_event(EventTypes.TEXT, args)	
	def on_text_motion(self, *args):
		self.node.dispatch_event(EventTypes.TEXT_MOTION, args)	
	def on_text_motion_select(self, *args):
		self.node.dispatch_event(EventTypes.TEXT_MOTION_SELECT, args)

if __name__ == "__main__":
	window = Window(resizable=True)
	print("Created window")
	node = GuiNode(window.node, 0.1, 0.1, 0.5, 0.4)
	button = GuiNodeButton(node, 0, 0, 1, 0.5, action=lambda :print("Pressed"))
	text = GuiNodeIncText(window.node, 0.1, 0.5, 0.5, 0.2)
	text2 = GuiNodeIncText(window.node, 0.1, 0, 0.5, 0.2)
	#window.draw_rectangle_outline(10, 10, 200, 200, (1, 0.5, 0.5, 1))
	pyglet.clock.schedule_interval(lambda dt:True, 1/20)
	pyglet.app.run()
