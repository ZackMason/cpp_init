# cpp_init
A crossplatform python script for creating templates of c/cpp projects that use cmake, with options for adding conan libraries and code templates

you can expand much of the functionality by creating templates in ```~/.cpp_init/templates``` and setting the path in ```~/.cpp_init/config.yaml``` (more info below)

right now there are only options for creating executable projects
I plan on adding static libs and dynamic libs later

The default unit testing template for cpp requires cpp 20, if you are using an earlier version you need to write your own template

## setup

if you don't have ```pyyaml``` installed then run
```
python3 -m pip install --user pyyaml
```
or whatever your alias for python3 is

install dependancies if you don't already have them
+ cmake - https://cmake.org/
+ conan (optional) - https://conan.io/ 

clone the repo

```
git clone https://github.com/ZackMason/cpp_init
```

add the directory to your PATH and open a new shell

if you are on linux you might want to add a shebang to the top of ```cpp_init.py``` so bash knows where to find python3, idk I use windows

if you are on windows make sure the default program to launch .py files is python3

run 
```
cpp_init.py
```

this will create ```~/.cpp_init/``` which holds the config file and a directory where you can store your templates

config example (this will be expanded to have multiple profiles soon)

```
hpp_template: hpp_template.txt
cpp_template: cpp_template.txt
cpp_version_template: default
c_version_template:   default
cmake_template: default
cmake_tests_template: default
prologue: prologue.txt
epilogue: none
types_hpp_template: default
core_hpp_template: default
tests_cpp_template: fmt_tests.cpp
tests_c_template: default
main_cpp_template: main_cpp_template.txt
main_c_template: default
cmake_version: default
```

notice the use of ```none``` in ```epilogue``` which will use an empty string in its place, this is different than default which
will use my default templates.

## Usage
```
usage: cpp_init.py [-h] [--create-project CREATE_PROJECT] [--languages LANGUAGES [LANGUAGES ...]] [--cpp-version CPP_VERSION]
                   [--c-version C_VERSION] [--use-conan] [--unit-testing] [--no-vscode] [--create-class CREATE_CLASS [CREATE_CLASS ...]]    
                   [--create-code CREATE_CODE [CREATE_CODE ...]] [--create-header CREATE_HEADER [CREATE_HEADER ...]]
                   [--create-source CREATE_SOURCE [CREATE_SOURCE ...]]

options:
  -h, --help            show this help message and exit
  --create-project CREATE_PROJECT
                        Create a cpp project in the current directory
  --languages LANGUAGES [LANGUAGES ...]
                        The languages used by the project
  --cpp-version CPP_VERSION
                        The cpp version to use
  --c-version C_VERSION
                        The c version to use
  --use-conan           Using conan package manager
  --unit-testing        Creates a seperate executable for unit testing
  --no-vscode           Turns off the generator for .vscode/settings.json
  --create-class CREATE_CLASS [CREATE_CLASS ...]
                        Create a cpp and hpp file with boilerplate filled out, expects that you are in the root of your project
  --create-code CREATE_CODE [CREATE_CODE ...]
                        Create a c and h file with boilerplate filled out, expects that you are in the root of your project
  --create-header CREATE_HEADER [CREATE_HEADER ...]
                        Create an h file with boilerplate filled out, expects that you are in the root of your project
  --create-source CREATE_SOURCE [CREATE_SOURCE ...]
                        Create a c file with boilerplate filled out, expects that you are in the root of your project
```


## Creating and Building your project

run 
```
cpp_init.py --create-project example --use-conan --languages CXX C --cpp-version 20 --unit-testing 
```
if you don't want to use conan you can omit the ```--use-conan``` flag

if there are dependancies that you need to use then add them to ```conanfile.txt```
```
cd example/build
conan install .. -s build_type=%TYPE% // conan should give you instructions if something goes wrong here, most likely you need to --build
cmake ..
cmake --build . --config %TYPE% (for msvc specify build type, not needed on others I think??)
```

```cmake ..``` could also be replaced with
```
cmake .. -G %GENERATOR% -DCMAKE_BUILD_TYPE=%TYPE%
```
example
```
conan install .. -s build_type=Release
cmake .. -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release
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

```%CODE_NAME%``` and ```%CLASS_NAME%``` are actually equivalent 

the command ```cpp_init.py --create-class Graphics/window``` using the above template will produce 

```
#pragma once

struct window_t {

};
```

---
template header
```
#pragma once

template<typename T>
struct %CLASS_NAME%_t {
  T& get() const;
  T value;
};

#include "%SOURCE_PATH%"

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
%C_VERSION%

%CONAN_SETUP%

file(GLOB_RECURSE src_files 
    ${PROJECT_SOURCE_DIR}/src/*.c*
)

include_directories(include)

add_executable(${PROJECT_NAME} ${src_files})
target_compile_definitions(${PROJECT_NAME} PUBLIC CMAKE_ASSETS_PATH="${CMAKE_CURRENT_SOURCE_DIR}/assets/")

%CMAKE_TESTS%
%CONAN_LINK%
```

---
## TODO - feel free to help :)

+ add vcpkg support
+ multiple profiles in config.yaml
+ emscripten support
+ user defined project layout




