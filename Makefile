PROGRAM = domaci
GCC = g++
GCCFLAGS = -std=c++17 -Wall
LDLIBS = -framework GLUT -framework OpenGL 

$(PROGRAM) : slerp.o transform.o
	$(GCC) $(GCCFLAGS) -o $@ slerp.o transform.o $(LDLIBS)

slerp.o : slerp.cpp
	$(GCC) $(GCCFLAGS) -c slerp.cpp -o slerp.o 
transform.o : transform.cpp 
	$(GCC) $(GCCFLAGS) -c transform.cpp -o transform.o 
	
.PHONY : clean

clean: 
	rm *.o $(PROGRAM)