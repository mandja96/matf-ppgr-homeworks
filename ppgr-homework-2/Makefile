PROGRAM = domaci
GCC = g++
GCCFLAGS = -std=c++17 -Wall

$(PROGRAM) : main.cpp
	$(GCC) $(GCCFLAGS) -o $@ $<

.PHONY : clean

clean: 
	rm *.o $(PROGRAM)