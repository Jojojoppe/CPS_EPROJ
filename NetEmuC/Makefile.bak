  
.SILENT:

DIRS 			:= src inc
CCFILES			:= $(shell find $(DIRS) -type f -name "*.cpp")
HFILES			:= $(shell find $(DIRS) -type f -name "*.hpp")
OBJ				:= $(patsubst %.cpp,%.cpp.o,$(CCFILES))
DFILES			:= $(patsubst %.cpp,%.cpp.d,$(CCFILES))

ALLFILES		:= $(CCFILES) $(HFILES)

CC				:= g++
CC_FLAGS		:= -I inc -g `sdl2-config --libs --cflags`
CC_WARNINGS		:= -Wall -Wextra -Wno-unused-parameter
CC_LIBS			:= -lpthread
CC_EXTRA		:= -std=c++11

DEBUG ?= 1
ifeq ($(DEBUG), 1)
    CC_EXTRA	+= -DDEBUG
endif

.PHONY: all clean 

all: bin/main

bin/main: $(OBJ)
	echo + Link
	-mkdir bin
	$(CC) $(CC_FLAGS) $(CC_WARNINGS) $(OBJ) $(CC_EXTRA) -o bin/main $(CC_LIBS)

%.cpp.o: %.cpp
	echo '>' $<
	$(CC) $(CC_FLAGS) $(CC_WARNINGS) $(CC_EXTRA) -MMD -o $@ -c $< $(CC_LIBS)

clean:
	echo + Clean
	-rm $(OBJ) $(DFILES)
	-rm bin/main
	-rm -r bin

run: bin/main
	echo + Executing
	bin/main

debug: bin/main
	echo + Debugging
	gdb bin/main

# Header dependencies
-include $(DFILES)