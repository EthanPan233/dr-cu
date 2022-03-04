#########
# Setup #
#########

# Specify the minimum version for CMake
cmake_minimum_required(VERSION 2.8)

# Message
message(STATUS "ISPD19 DR CUHK")
message(STATUS ${CMAKE_CURRENT_SOURCE_DIR})
message(STATUS ${PROJECT_SOURCE_DIR})


set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)
set(LD_LIBRARY_PATH /usr/lib64)
message(STATUS ${LD_LIBRARY_PATH})
set(LIBRARY_PATH /usr/lib64)
message(STATUS ${LIBRARY_PATH})

# Find includes in the build directories
set(CMAKE_INCLUDE_CURRENT_DIR ON)

# Project's name
project(ispd19dr)

# Set the output folder where your program will be created
set(EXECUTABLE_OUTPUT_PATH ${CMAKE_BINARY_DIR})
set(LIBRARY_OUTPUT_PATH ${CMAKE_BINARY_DIR})

set(CMAKE_CXX_STANDARD 14)

set(PATH_RSYN ${CMAKE_CURRENT_SOURCE_DIR}/../rsyn)
set(PATH_ICCAD19 ${CMAKE_CURRENT_SOURCE_DIR})

###################
# Warnings/Errors #
###################

set(CMAKE_CXX_FLAGS  "${CMAKE_CXX_FLAGS} -Werror=return-type")

######################
# Check Dependencies #
######################
# uncommment this line if you are using self-compiled boost lib
# set(BOOST_LIBRARYDIR /ubc/ece/home/ai/grads/yuxuanpan/Envs/boost_1_75_0/stage/libs)
set(BOOST_ROOT /ubc/ece/home/ai/grads/yuxuanpan/Envs/boost_1_75_0)
set(Boost_USE_STATIC_LIBS ON)
find_package(Boost COMPONENTS system filesystem program_options REQUIRED)
# find_package(Threads)

###############
# Source Code #
###############
file(GLOB_RECURSE SRC_FILES_RSYN
    ${PATH_RSYN}/src/*.cpp
    ${PATH_RSYN}/src/*.cc
    ${PATH_RSYN}/src/*.c)

file(GLOB_RECURSE SRC_FILES_ICCAD19
    ${PATH_ICCAD19}/*.cpp
    ${PATH_ICCAD19}/*.c)

set(SRC_FILES ${SRC_FILES_RSYN} ${SRC_FILES_ICCAD19})

#################
# Library Paths #
#################
# Need to come before target is created.

if(${CMAKE_SYSTEM_NAME} MATCHES "Linux")
link_directories(${PATH_RSYN}/lib/linux)
endif()

if(${CMAKE_SYSTEM_NAME} MATCHES "Darwin")
link_directories(${PATH_RSYN}/lib/macosx)
endif()


###########
# Targets #
###########

add_executable(ispd19dr ${SRC_FILES})

#######################
# Include Directories #
#######################

include_directories(${PATH_RSYN}/src)
include_directories(${PATH_RSYN}/src/rsyn/export)
include_directories(${PATH_RSYN}/include)
include_directories(${PATH_ICCAD19})

#################
# Linker Flags  #
#################

# TODO: set static under release mode only
set_target_properties(ispd19dr PROPERTIES LINK_FLAGS "-Wl,--whole-archive -rdynamic -lpthread -Wl,--no-whole-archive")

# LEF/DEF
target_link_libraries(ispd19dr lef)
target_link_libraries(ispd19dr def)

# LD libraries
add_library(lm SHARED IMPORTED)
set_target_properties(lm PROPERTIES IMPORTED_LOCATION "/usr/lib64/libm.so")
target_link_libraries(ispd19dr lm)
add_library(lpthread STATIC IMPORTED)
set_target_properties(lpthread PROPERTIES IMPORTED_LOCATION "/usr/lib64/libpthread.so.0")
target_link_libraries(ispd19dr lpthread)

# Boost
target_include_directories(ispd19dr PUBLIC ${Boost_INCLUDE_DIR})
target_link_libraries(ispd19dr ${Boost_LIBRARIES})
