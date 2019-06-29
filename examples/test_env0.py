from qlibs import resource_manager as rm
from qlibs.gui.window_provider import window_provider

win = window_provider.Window()
ctx = win.ctx

print(rm.get_storage_of_context(ctx))
print(rm.get_storage_of_context(ctx))
