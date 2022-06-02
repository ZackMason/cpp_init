import os, argparse
from datetime import date

import yaml


code_template_keywords = [
    'CLASS_NAME',
    'HEADER_PATH',
    'SOURCE_PATH',
]

CPP_CLASS_TEMPLATE = '''#include "%HEADER_PATH%"


'''

HPP_CLASS_TEMPLATE = '''#pragma once

struct %CLASS_NAME%_t {

};
'''

config = {
    'hpp_template': HPP_CLASS_TEMPLATE,
    'cpp_template': CPP_CLASS_TEMPLATE,
    'preamble': '',
}

CONAN_TEMPLATE = '''
[requires]

[generators]
cmake
'''

# [project_name, c++ version]
CMAKE_CONAN_TEMPLATE = '''
cmake_minimum_required(VERSION 2.8.12)
project(%s C CXX)

set(CMAKE_CXX_STANDARD %i)
set(CMAKE_CXX_STANDARD_REQUIRED True)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

file(GLOB_RECURSE src_files 
    ${PROJECT_SOURCE_DIR}/src/*.cpp
)

include_directories(include)

add_executable(${PROJECT_NAME} ${src_files})
target_compile_definitions(${PROJECT_NAME} PUBLIC ASSETS_PATH="${CMAKE_CURRENT_SOURCE_DIR}/assets/")

target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
'''

CMAKE_TEMPLATE = '''
cmake_minimum_required(VERSION 2.8.12)
project(%s C CXX)

set(CMAKE_CXX_STANDARD %i)
set(CMAKE_CXX_STANDARD_REQUIRED True)

file(GLOB_RECURSE src_files 
    ${PROJECT_SOURCE_DIR}/src/*.cpp
)

include_directories(include)

add_executable(${PROJECT_NAME} ${src_files})
target_compile_definitions(${PROJECT_NAME} PUBLIC CMAKE_ASSETS_PATH="${CMAKE_CURRENT_SOURCE_DIR}/assets/")
'''

MAIN_CPP_TEMPLATE = '''
#include "core.hpp"

int main(int argc, char** argv)
{
    std::cout << "Hello Captain!" << std::endl;

    return 0;
}
'''

CORE_HPP_TEMPLATE = '''
#pragma once

#include <memory>
#include <iostream>
#include <vector>
#include <array>
#include <cmath>
#include <string>
#include <fstream>
#include <cassert>
#include <sstream>
#include <unordered_map>
#include <unordered_set>
#include <functional>
#include <algorithm>
#include <filesystem>

#include "types.hpp"

const std::string ASSETS_PATH = CMAKE_ASSETS_PATH;

constexpr int BIT(int x)
{
	return 1 << x;
}
'''

TYPES_HPP_TEMPLATE = '''
#pragma once

using u8  = uint8_t;
using u16 = uint16_t;
using u32 = uint32_t;
using u64 = uint64_t;

using i8  = int8_t;
using i16 = int16_t;
using i32 = int32_t;
using i64 = int64_t;

using f32 = float;
using f64 = double;
'''

VSCODE_SETTINGS_JSON_TEMPLATE = '''{
    "C_Cpp.clang_format_path": "/usr/lib/llvm-10/bin/clang-format",
    "C_Cpp.default.includePath": [
      "~/.conan/data/**", "./include/"
    ],
    "files.associations": {
        "string": "cpp",
        "xstring": "cpp"
    }
}'''

def generate_project(project_name, use_conan):
    project_directory_path = os.getcwd() + '/' + project_name
    print(f'Creating directory: {project_directory_path}')
    os.mkdir(project_directory_path)
    
    if use_conan:
        print(f'Creating conanfile.txt')
        with open(f'{project_directory_path}/conanfile.txt', 'x') as f:
            f.write(CONAN_TEMPLATE)

    print(f'Creating CMakeLists.txt')
    with open(f'{project_directory_path}/CMakeLists.txt', 'x') as f:
        f.write((CMAKE_CONAN_TEMPLATE if use_conan else CMAKE_TEMPLATE) % (project_name, 20))

    os.mkdir(f'{project_directory_path}/src')
    os.mkdir(f'{project_directory_path}/include')
    os.mkdir(f'{project_directory_path}/assets')
    os.mkdir(f'{project_directory_path}/build')
    os.mkdir(f'{project_directory_path}/.vscode')

    with open(f'{project_directory_path}/src/main.cpp', 'x') as f:
        f.write(MAIN_CPP_TEMPLATE)

    with open(f'{project_directory_path}/include/core.hpp', 'x') as f:
        f.write(CORE_HPP_TEMPLATE)

    with open(f'{project_directory_path}/include/types.hpp', 'x') as f:
        f.write(TYPES_HPP_TEMPLATE)
    
    if use_conan:
        with open(f'{project_directory_path}/.vscode/settings.json', 'x') as f:
            f.write(VSCODE_SETTINGS_JSON_TEMPLATE)

def create_cpp_class(class_name):
    project_directory_path = os.getcwd()

    class_sub_dir = class_name.split('/')
    class_name = class_sub_dir[-1]
    class_sub_dir = '/'.join(class_sub_dir[:-1]) + ('/' if class_sub_dir[:-1] else '')

    class_include = f'{project_directory_path}/include/{class_sub_dir}'
    class_source = f'{project_directory_path}/src/{class_sub_dir}'

    for dir in [class_include, class_source]:
        if os.path.isdir(dir) == False:
            os.mkdir(dir)

    todays_date = date.today()

    def create_template(name, preamb = ''):
        contents = config[name].replace('%CLASS_NAME%', class_name)
        contents = contents.replace('%HEADER_PATH%', f'{class_sub_dir}{class_name}.hpp')
        contents = contents.replace('%DATE%', str(todays_date))
        return f'{preamb}\n{contents}'
    
    preamble = create_template('preamble')

    try:
        with open(f'{class_include}/{class_name}.hpp', 'x') as f:
            f.write(create_template('hpp_template', preamble))
        with open(f'{class_source}/{class_name}.cpp', 'x') as f:
            f.write(create_template('cpp_template', preamble))
        print(f'Created Class: {class_name} at {project_directory_path}')
    except Exception as e:
        print(f'Failed to create class: {class_name} ', e)

def init_data_dir():
    home_dir = os.path.expanduser('~/.cpp_init')
    if os.path.isdir(home_dir): return
    os.mkdir(home_dir)
    os.mkdir(f'{home_dir}/templates')
    with open(f'{home_dir}/config.yaml', 'x') as f:
        f.write('''hpp_template: default
cpp_template: default
preamble: default''')

def read_config():
    global config
    home_dir = os.path.expanduser('~/.cpp_init')

    def load_template(name):
        if yaml_config[name] != 'default':
            template_file = yaml_config[name]
            with open(f'{home_dir}/templates/{template_file}') as tf:
                config[name] = tf.read()

    assert os.path.isdir(home_dir)
    with open(f'{home_dir}/config.yaml', 'r') as f:
        yaml_config = yaml.load(f, Loader=yaml.FullLoader)
        load_template('hpp_template')
        load_template('cpp_template')
        load_template('preamble')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--create-project', type=str, help='Create a cpp project in the current directory')
    parser.add_argument('--use-conan', type=bool, default=True, help='Using conan package manager')
    parser.add_argument('--create-class', type=str, help='Create a cpp and hpp file with boilerplate filled out')

    args = parser.parse_args()

    init_data_dir()
    read_config()

    if args.create_project:
        generate_project(args.create_project, use_conan=args.use_conan)

    if args.create_class:
        create_cpp_class(args.create_class)