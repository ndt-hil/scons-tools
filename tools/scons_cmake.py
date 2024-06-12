from SCons.Builder import Builder
from SCons.Environment import Environment

from SCons.Script import ARGUMENTS

import subprocess
import os

OUTPUT_DIR = ARGUMENTS.get('output', '_build')
CMAKE_GENERATOR_NAME = ARGUMENTS.get('cmake_generator_name', 'Unix Makefiles')
BUILD_CONFIGURATION = ARGUMENTS.get('build_config', 'Debug')
CMAKE_TOOLCHAIN_FILE = ARGUMENTS.get('cmake_toolchain', 'cmake/netx90_gccarmemb.cmake')

CMAKELISTS_FILE = ARGUMENTS.get('source_file', 'CMakeLists.txt')

CMAKE_OTHER_FLAGS = ARGUMENTS.get("other_flags", "")


def get_cmake_files(target, source, env):
    root_dir = os.path.dirname(str(source[0]))

    target_file = "CMakeCache.txt"
    source_file = "CMakeLists.txt"

    return (root_dir, target_file, source_file)

'''
    The action that will invoke cmake. Here we build the command line
'''
def cmake(target, source, env):
    cmd = [
        "cmake",
        "-G", CMAKE_GENERATOR_NAME,
        "-DCMAKE_BUILD_TYPE={BUILD_CONFIGURATION}",
        "-B", OUTPUT_DIR,
        "--toolchain", CMAKE_TOOLCHAIN_FILE,
    ]

    # If the source file is not specified, we skip it
    source_dir = os.path.dirname(str(CMAKELISTS_FILE))
    if source_dir:
        cmd.append("-S")
        cmd.append(source_dir)

    if CMAKE_OTHER_FLAGS:
        other_flags = CMAKE_OTHER_FLAGS.split()
        cmd += other_flags

    return subprocess.call(cmd)


def cmake_build(target, source, env):
    cmd = [
        "cmake",
        "--build",
        OUTPUT_DIR
    ]

    return subprocess.call(cmd)

'''
    The emitter is what will modify the source and target lists. This is what tells
    SCons when our action needs to be called (If source or target file changes).
'''
def cmake_emitter(target ,source, env):
    (root_dir, target_file, source_file) = get_cmake_files(target, source, env)

    return ([ os.path.join(root_dir, OUTPUT_DIR) ],
            [ os.path.join(root_dir, source_file) ])

'''
    Script starting point
'''
env = Environment()

cmake_generator = env.Builder(
    action = cmake,
    single_source = True,
    emitter = cmake_emitter,
    source_factory = env.fs.File,
    target_factory = env.fs.Dir
)

cmake_builder = env.Builder(
    action = cmake_build,
    single_source = True,
    emitter = cmake_emitter,
    source_factory = env.fs.File,
    target_factory = env.fs.Dir,
)

env['BUILDERS']['CMake'] = cmake_generator
env['BUILDERS']['CMakeBuild'] = cmake_builder

cmake_gen_target = env.CMake(CMAKELISTS_FILE)
cmake_bld_target = env.CMakeBuild(CMAKELISTS_FILE)

env.AlwaysBuild(cmake_gen_target, cmake_bld_target)
env.Default(cmake_gen_target, cmake_bld_target)
