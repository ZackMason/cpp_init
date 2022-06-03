# cpp_init
A python script for creating c/cpp projects that use cmake, with options for adding conan libraries

## setup

install dependancies
+ cmake - https://cmake.org/
+ conan (optional) - https://conan.io/ 

clone the repo

```
git clone https://github.com/ZackMason/cpp_init
```

add the directory to your PATH and open a new shell

run 
```
cpp_init.py
```

this will create ```~/.cpp_init/``` which holds the config file and a directory where you can store your templates

config example

```
hpp_template: hpp_template.txt
cpp_template: cpp_template.txt
prologue: prologue.txt
epilogue: none
types_hpp_template: default
core_hpp_template: default
main_cpp_template: default
main_c_template: default
cmake_version: default
```

notice the use of ```none``` in ```epilogue``` which will use an empty string in its place, this is different than default which
will use my default templates.

## Flags
+ -h, --help
+ --create-project %PROJECT_NAME%
+ --create-class [filepath/class_name]
+ --create-code [filepath/code_name]
+ --use-conan
+ --languages "CXX" | "C" | "CXX C"
+ --cpp-version %i
+ --c-version %i

## Creating and Building your project

run 
```
cpp_init.py --create-project example --use-conan --languages CXX
```
if you don't want to use conan you can omit the ```--use-conan``` flag

if there are dependancies that you need to use then add them to ```conanfile.txt```
```
cd example/build
conan install .. // conan should give you instructions if something goes wrong here
cmake ..
cmake --build .
```


## Example Templates

c-style header
```
#ifndef %^^CODE_NAME%_H
#define %^^CODE_NAME%_H

typedef struct %CODE_NAME%_t {

} %CODE_NAME%_t;

#endif /* %^^CODE_NAME%_H */
```

```%^^CODE_NAME%``` will capitalize all letters in the name passed into ```--create-code``` whereas
```%^CODE_NAME%``` will only capitalize the first letter

---

c-style source
```
#include "%HEADER_PATH%"
```

---

cpp-style header

cpp style templates are created using ```--create-class```

```
#pragma once

struct %CLASS_NAME%_t {

};
```
---

prologue
```
// Author: Zackery Mason-Blaug
// Date: %DATE%
//////////////////////////////////////////////////////////

```

---

default CMakeLists.txt
```
cmake_minimum_required(VERSION %CMAKE_VERSION%)
project(%PROJECT_NAME% %LANGUAGES%)

%CPP_VERSION%

%CONAN_SETUP%

file(GLOB_RECURSE src_files 
    ${PROJECT_SOURCE_DIR}/src/*.c*
)

include_directories(include)

add_executable(${PROJECT_NAME} ${src_files})
target_compile_definitions(${PROJECT_NAME} PUBLIC CMAKE_ASSETS_PATH="${CMAKE_CURRENT_SOURCE_DIR}/assets/")

%C_VERSION%

%CONAN_LINK%

```


