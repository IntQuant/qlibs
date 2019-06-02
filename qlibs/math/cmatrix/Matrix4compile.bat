@set PATH=%C:\Program Files\CodeBlocks\MinGW\bin\;%PATH%
@echo Compiling.
@"C:\Program Files\CodeBlocks\MinGW\bin\g++" -std=c++14 -O3 -c Matrix4.cpp -o Matrix4.o
@echo Creating dll.
@"C:\Program Files\CodeBlocks\MinGW\bin\g++" -shared -o Matrix4.dll Matrix4.o -Wl,--out-implib,Matrix4.a
@echo Generating objdump.
@objdump -p Matrix4.dll > out.txt
@echo Done.
@pause.


