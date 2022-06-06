import os, argparse, yaml
from datetime import date
from random import choice

code_template_keywords = [
    'CLASS_NAME',
    '^CLASS_NAME',
    '^^CLASS_NAME',
    'CODE_NAME',
    '^CODE_NAME',
    '^^CODE_NAME',
    'HEADER_PATH',
    'SOURCE_PATH',
    'DATE',
    'RANDOM_GREETING',
]

greetings = [
    'Hello World!',
    'Hello Captain!',
    'Hello Sailor!',
]

CPP_CLASS_TEMPLATE = '''#include "%HEADER_PATH%"


'''
HPP_CLASS_TEMPLATE = '''#pragma once

struct %CLASS_NAME% {

};
'''
H_CODE_TEMPLATE = '''#ifndef %^^CODE_NAME%_H
#define %^^CODE_NAME%_H

typedef struct %CODE_NAME%_t {

} %CODE_NAME%_t;

#endif /* %^^CODE_NAME%_H */
'''
C_CODE_TEMPLATE = '''#include "%HEADER_PATH%"
'''
MAIN_C_TEMPLATE = '''#include "stdio.h"

int main(int argc, char** argv)
{
    printf("Hello Captain!\\n");

    return 0;
}
'''
MAIN_CPP_TEMPLATE = '''#include <iostream>

int main(int argc, char** argv)
{
    std::cout << "Hello Captain!" << std::endl;

    return 0;
}
'''
TESTS_CPP_TEMPLATE = '''#include <iostream>
#include <cassert>
#include <exception>

static size_t tests_run = 0;
static size_t tests_passed = 0;

struct test_failed : std::exception {
    std::string message;
    test_failed(std::string&& text){ 
        message = std::move(text);
    }

    const char* what() const noexcept override {
        return message.c_str();
    }
};

constexpr auto throw_assert(const bool b, std::string&& text) -> auto {
    if (!b) throw test_failed(std::move(text));
}

constexpr auto throw_assert(const bool b) -> auto {
    throw_assert(b, "Assert Failed"s);
}


#define TEST_ASSERT( x ) throw_assert(x, "TEST FAILED: " #x);


template <typename Fn>
auto run_test(const char* name, const Fn& test) -> auto {
    ++tests_run;
    try {
        test();
        ++tests_passed;
        std::cout << "Succeeded: " << name << std::endl;
    } catch (std::exception & e) {
        std::cout << "Failed: " << name << " - " << e.what() << std::endl;
    }
}

int main(int argc, char** argv) {
    run_test("equal", [](){
        TEST_ASSERT(1 == 1);
    });

    run_test("fail_test", [](){
        TEST_ASSERT(0 == 1);
    });

    std::cout << tests_passed << " / " << tests_run << " Tests Succeeded!" << std::endl;
    return 0;
}
'''
TESTS_C_TEMPLATE = '''#include "stdio.h"

int tests_passed = 0;
int tests_run = 0;

int main(int argc, char** argv) {
    printf("%i / %i Tests Succeeded!\\n", tests_passed, tests_run);
    return 0;
}
'''
CORE_HPP_TEMPLATE = '''#pragma once

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

#include "types.hpp"

#ifndef CMAKE_ASSETS_PATH
#define CMAKE_ASSETS_PATH "./"
#endif

#define ASSETS_PATH std::string(CMAKE_ASSETS_PATH)

constexpr int BIT(int x)
{
	return 1 << x;
}
'''
TYPES_HPP_TEMPLATE = '''#pragma once

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
CONAN_TEMPLATE = '''[requires]

[generators]
cmake
'''
CONAN_SETUP_TEMPLATE = '''include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()'''
CONAN_LINK_TEMPLATE = '''target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
'''
CONAN_LINK_TESTS_TEMPLATE = '''target_link_libraries(tests ${CONAN_LIBS})
'''
CPP_VERSION_TEMPLATE = '''set(CMAKE_CXX_STANDARD %i)
set(CMAKE_CXX_STANDARD_REQUIRED True)'''
C_VERSION_TEMPLATE = '''set(CMAKE_C_STANDARD %i)'''
CMAKE_TESTS_TEMPLATE = '''file(GLOB_RECURSE test_files 
    ${PROJECT_SOURCE_DIR}/src/*.c*
    ${PROJECT_SOURCE_DIR}/tests/*.c*
)
list(FILTER test_files EXCLUDE REGEX ${PROJECT_SOURCE_DIR}/src/main.c*)

add_executable(tests ${test_files})
target_compile_definitions(tests PUBLIC CMAKE_ASSETS_PATH="${CMAKE_CURRENT_SOURCE_DIR}/assets/")
%s'''
CMAKE_TEMPLATE = '''cmake_minimum_required(VERSION %CMAKE_VERSION%)
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

config = {
    'cpp_version_template': CPP_VERSION_TEMPLATE,
    'c_version_template': C_VERSION_TEMPLATE,
    'hpp_template': HPP_CLASS_TEMPLATE,
    'cpp_template': CPP_CLASS_TEMPLATE,
    'c_template': C_CODE_TEMPLATE,
    'h_template': H_CODE_TEMPLATE,
    'cmake_template': CMAKE_TEMPLATE,
    'cmake_tests_template': CMAKE_TESTS_TEMPLATE,
    'types_hpp_template': TYPES_HPP_TEMPLATE,
    'core_hpp_template': CORE_HPP_TEMPLATE,
    'main_cpp_template': MAIN_CPP_TEMPLATE,
    'main_c_template': MAIN_C_TEMPLATE,
    'tests_cpp_template': TESTS_CPP_TEMPLATE,
    'tests_c_template': TESTS_C_TEMPLATE,
    'prologue': '',
    'epilogue': '',
    'cmake_version': '2.8.12'
}

def generate_project(project_name, use_conan, languages, cpp_version, c_version, use_vscode, with_tests):
    project_directory_path = os.getcwd() + '/' + project_name
    print(f'Creating directory: {project_directory_path}')
    os.mkdir(project_directory_path)
    
    if use_conan:
        print(f'Creating conanfile.txt')
        with open(f'{project_directory_path}/conanfile.txt', 'x') as f:
            f.write(CONAN_TEMPLATE)

    print(f'Creating CMakeLists.txt')
    with open(f'{project_directory_path}/CMakeLists.txt', 'x') as f:
        template = config['cmake_template']
        template = template.replace('%CMAKE_VERSION%', config['cmake_version'])
        template = template.replace('%PROJECT_NAME%', project_name)
        template = template.replace('%LANGUAGES%', ' '.join(languages))
        template = template.replace('%CONAN_SETUP%', CONAN_SETUP_TEMPLATE if use_conan else '')
        template = template.replace('%CONAN_LINK%', CONAN_LINK_TEMPLATE if use_conan else '')
        if with_tests:
            template = template.replace('%CMAKE_TESTS%', config['cmake_tests_template'] % (CONAN_LINK_TESTS_TEMPLATE if use_conan else ''))
        else:
            template = template.replace('%CMAKE_TESTS%', '')
        template = template.replace('%CPP_VERSION%', (config['cpp_version_template'] % cpp_version) if 'CXX' in languages else '')
        template = template.replace('%C_VERSION%', (config['c_version_template'] % c_version) if 'C' in languages else '')
        f.write(template)

    os.mkdir(f'{project_directory_path}/src')
    os.mkdir(f'{project_directory_path}/include')
    os.mkdir(f'{project_directory_path}/assets')
    os.mkdir(f'{project_directory_path}/build')
    if use_vscode:
        os.mkdir(f'{project_directory_path}/.vscode')
        with open(f'{project_directory_path}/.vscode/settings.json', 'x') as f:
            f.write(VSCODE_SETTINGS_JSON_TEMPLATE)
    if with_tests:
        os.mkdir(f'{project_directory_path}/tests')

    if 'CXX' in languages:
        with open(f'{project_directory_path}/src/main.cpp', 'x') as f:
            f.write(config['main_cpp_template'])

        if config['core_hpp_template']:
            with open(f'{project_directory_path}/include/core.hpp', 'x') as f:
                f.write(config['core_hpp_template'])
        if config['types_hpp_template']:
            with open(f'{project_directory_path}/include/types.hpp', 'x') as f:
                f.write(config['types_hpp_template'])
        if with_tests:
            with open(f'{project_directory_path}/tests/tests.cpp', 'x') as f:
                f.write(config['tests_cpp_template'])
    else:
        with open(f'{project_directory_path}/src/main.c', 'x') as f:
            f.write(config['main_c_template'])
        if with_tests:
            with open(f'{project_directory_path}/tests/tests.c', 'x') as f:
                f.write(config['tests_c_template'])

def create_cpp_class(class_name, header_ext, source_ext):
    project_directory_path = os.getcwd()

    class_sub_dir, class_name = os.path.split(class_name)

    class_include = f'{project_directory_path}/include/{class_sub_dir}'
    class_source = f'{project_directory_path}/src/{class_sub_dir}'

    for dir in [class_include, class_source]:
        if os.path.isdir(dir) == False:
            os.makedirs(dir, exist_ok=True)

    todays_date = date.today()

    def create_template(name, prologue = '',epilogue = ''):
        contents = config[name].replace('%CLASS_NAME%', class_name)
        sub_dir = class_sub_dir + '/' if class_sub_dir else ''
        contents = contents.replace('%CODE_NAME%', class_name)
        contents = contents.replace('%^CODE_NAME%', str.capitalize(class_name))
        contents = contents.replace('%^CLASS_NAME%', str.capitalize(class_name))
        contents = contents.replace('%^^CLASS_NAME%', str.upper(class_name))
        contents = contents.replace('%^^CODE_NAME%', str.upper(class_name))
        contents = contents.replace('%HEADER_PATH%', f'{sub_dir}{class_name}.{header_ext}')
        contents = contents.replace('%SOURCE_PATH%', f'{sub_dir}{class_name}.{source_ext}')
        contents = contents.replace('%DATE%', str(todays_date))
        contents = contents.replace('%RANDOM_GREETING%', choice(greetings))
        sep = '\n' if prologue else ''
        return f'{prologue}{sep}{contents}{epilogue}'
    
    prologue = create_template('prologue')
    epilogue = create_template('epilogue')

    try:
        if header_ext:
            with open(f'{class_include}/{class_name}.{header_ext}', 'x') as f:
                f.write(create_template('hpp_template' if header_ext == 'hpp' else 'h_template', prologue, epilogue))
        if source_ext:
            with open(f'{class_source}/{class_name}.{source_ext}', 'x') as f:
                f.write(create_template('cpp_template' if source_ext == 'cpp' else 'c_template', prologue, epilogue))
        print(f'Created Class: {class_name} in project {project_directory_path}')
    except Exception as e:
        print(f'Failed to create class: {class_name} ', e)

def init_data_dir():
    '''creates config dir in home directory if it doesn't exist already'''
    home_dir = os.path.expanduser('~/.cpp_init')
    if os.path.isdir(home_dir): return
    os.mkdir(home_dir)
    os.mkdir(f'{home_dir}/templates')
    with open(f'{home_dir}/config.yaml', 'x') as f:
        f.write('''hpp_template: default
cpp_template: default
cpp_version_template: default
c_version_template: default
cmake_template: default
cmake_tests_template: default
prologue: default
epilogue: none
types_hpp_template: none
core_hpp_template: none
main_cpp_template: default
main_c_template: default
tests_cpp_template: default
tests_c_template: default
cmake_version: default''')

def read_config():
    global config
    home_dir = os.path.expanduser('~/.cpp_init')

    def load_template(name):
        '''loads the global config settings'''
        if yaml_config[name] != 'default':
            template_file = yaml_config[name]

            if template_file == 'none':
                config[name] = ''
            else:
                with open(f'{home_dir}/templates/{template_file}') as tf:
                    config[name] = tf.read()

    assert os.path.isdir(home_dir)
    with open(f'{home_dir}/config.yaml', 'r') as f:
        yaml_config = yaml.load(f, Loader=yaml.FullLoader)
        load_template('hpp_template')
        load_template('cpp_template')
        load_template('cpp_version_template')
        load_template('c_version_template')
        load_template('cmake_template')
        load_template('cmake_tests_template')
        load_template('prologue')
        load_template('epilogue')
        load_template('types_hpp_template')
        load_template('core_hpp_template')
        load_template('types_hpp_template')
        load_template('main_cpp_template')
        load_template('tests_cpp_template')
        load_template('tests_c_template')
        load_template('main_c_template')
        load_template('cmake_version')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--create-project', type=str, help='Create a cpp project in the current directory')
    parser.add_argument('--languages', type=str, nargs='+', help='The languages used by the project', default=['C', 'CXX'])
    parser.add_argument('--cpp-version', type=int, help='The cpp version to use', default=11)
    parser.add_argument('--c-version', type=int, help='The c version to use', default=11)
    parser.add_argument('--use-conan', default=False, action='store_true', help='Using conan package manager')
    parser.add_argument('--unit-testing', default=False, action='store_true', help='Creates a seperate executable for unit testing')
    parser.add_argument('--no-vscode', default=False, action='store_true', help='Turns off the generator for .vscode/settings.json')
    parser.add_argument('--create-class', nargs='+',  type=str, help='Create a cpp and hpp file with boilerplate filled out, expects that you are in the root of your project')
    parser.add_argument('--create-code', nargs='+',  type=str, help='Create a c and h file with boilerplate filled out, expects that you are in the root of your project')
    parser.add_argument('--create-header', nargs='+',  type=str, help='Create an h file with boilerplate filled out, expects that you are in the root of your project')
    parser.add_argument('--create-source', nargs='+',  type=str, help='Create a c file with boilerplate filled out, expects that you are in the root of your project')

    args = parser.parse_args()

    init_data_dir()
    read_config()

    if args.create_project:
        generate_project(args.create_project, 
            use_conan=args.use_conan,
            languages=args.languages,
            cpp_version=args.cpp_version,
            c_version=args.c_version,
            use_vscode=not args.no_vscode, 
            with_tests=args.unit_testing)
    if args.create_code:
        for name in args.create_code:
            create_cpp_class(name, 'h', 'c')
    elif args.create_class:
        for name in args.create_class:
            create_cpp_class(name, 'hpp', 'cpp')
    elif args.create_header:
        for name in args.create_header:
            create_cpp_class(name, 'h', '')
    elif args.create_source:
        for name in args.create_source:
            create_cpp_class(name, '', 'c')