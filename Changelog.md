## Qlibs 0.4.2
 - Fix: not every window can now be closed.
 - Fix: App skips rendering if window width or height is equal to zero. (Caused crash on windows)

## Qlibs 0.4.-1
 - Font system being reworked.
 - Fixed weird word wrapping behavior.
 - A lot of changes to widget system.
 - ScrollableListB and ScrollableStringListB now have target_size property.
 - Added some context variables (current_window and current_context).
 - ScrollbarB now handles dragging outside of itself. 
 - WindowNodeB and RootNodeB were added.
 - Vectors now have in_box(a, b) method.

## Qlibs 0.3.2
 - Some fixes for text rendering.

## Qlibs 0.3.1
 - Fixed centering being a bit off in multiline text rendering.
 - Default distance has been increased to 15.

## QLibs 0.3.0
 - QLibs window is passed instead of glfw window in callbacks.
 - Widget controller no longer depends on flipped mouse.
 - Some improvements of FormattedText.
 - All nodes now support using FormattedText.

## QLibs 0.2.10
 - Any behavior can now have it's name specified in the constructor.
 - It is now possible to multiply and divide by Vec2.
 - Added small ident to text.
 - set_node() method of app only changes node if it is different from current.
 