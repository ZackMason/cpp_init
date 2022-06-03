# cpp_init
A python script for creating c/cpp projects that use cmake, with options for adding conan libraries

## setup

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
+ --create-class [%CLASS_NAME%]
+ --create-code [%CODE_NAME%]
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
```
cd example/build
conan install ..
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

cpp-style header
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




