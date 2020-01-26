cmake_minimum_required(VERSION 3.10)
project(NetEmuC)

# Use C++ 11
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)

set(src_files
    ${CMAKE_SOURCE_DIR}/src/main.cpp
    ${CMAKE_SOURCE_DIR}/src/ini.cpp
    ${CMAKE_SOURCE_DIR}/src/Maze.cpp
    ${CMAKE_SOURCE_DIR}/src/INIReader.cpp
    ${CMAKE_SOURCE_DIR}/src/Client.cpp
)

set(inc_dirs 
    ${CMAKE_SOURCE_DIR}/inc
)

# Used packages
find_package(SDL2 REQUIRED)

add_executable(NetEmuC ${src_files})
target_link_libraries(NetEmuC SDL2::SDL2)
target_include_directories(NetEmuC PUBLIC ${inc_dirs})