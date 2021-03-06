## Qlibs 0.6.0
 - Feature: SpriteMaster can now load PIL images and ImageData directly.
 - Feature: texture filter can now be specified for SpriteMaster.
 - Feature: absolute paths can be used instead of resource paths everywhere. Relative paths are also used directly when they couldn't be resolved to anything else.
 - Feature: font kerning.
 - Feature: a new way to set up text formatting.
 - Fix: multiple fonts not working. At all.

## Qlibs 0.5.7
 - Fix: turns out glyph.bearing.x was ignored. Not anymore, resulting in a more correct font rendering.

## Qlibs 0.5.6
 - Fix: use integer values for scissor test
 - Ref: use enum instead of str in node types

## Qlibs 0.5.5
 - Fix: V1 node renderer sometimess messed up draw order

## Qlibs 0.5.4
 - C modules are now in a separete module, Qlibs Cyan

## Qlibs 0.5.3
 - Fix: leaking in basic_shapes
 - Matrix4 C module temporaly disabled

## Qlibs 0.5.2
 - Perfomance: Matrix4 C module

## Qlibs 0.5.1
 - Fix: DirectFontRender can't find default font on mac (Issue #1)

## Qlibs 0.5.0
 - Feature: support for sRGB textures.
 - Fix: model loader was confused by spaces in filenames.
 - Perfomance: model loader now loads models faster
 - Feature: matrix inverse(slow))

## Qlibs 0.4.3
 - Feature: ColumnDiagram Behavior.

## Qlibs 0.4.2
 - Fix: not every window can now be closed.
 - Fix: App skips rendering if window width or height is equal to zero. (Caused crash on windows)
 - Fix(.2) App was broken

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
 
