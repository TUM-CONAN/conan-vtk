import os
import shutil
import re

from fnmatch import fnmatch
from conans import ConanFile, CMake, tools


class LibVTKConan(ConanFile):
    name = "vtk"
    upstream_version = "8.2.0"
    package_revision = "-r1"
    version = "{0}{1}".format(upstream_version, package_revision)

    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    exports = [
        "patches/CMakeProjectWrapper.txt",
        "patches/optimization.diff",
        "patches/offscreen_size_windows.diff"
    ]
    url = "https://git.ircad.fr/conan/conan-vtk"
    license = "http://www.vtk.org/licensing/"
    description = "Visualization Toolkit by Kitware"
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"
    short_paths = True

    def configure(self):
        del self.settings.compiler.libcxx
        # if 'CI' not in os.environ:
        #     os.environ["CONAN_SYSREQUIRES_MODE"] = "verify"

    def requirements(self):
        self.requires("ircad_common/1.0.2@camposs/stable")
        self.requires("qt/5.12.2-r1@ircad/testing")
        # self.requires("qt/5.12.2@bincrafters/stable")

        if tools.os_info.is_windows:
            self.requires("libxml2/2.9.8-r2@camposs/stable")
            self.requires("expat/2.2.5-r2@camposs/stable")
            self.requires("zlib/1.2.11@camposs/stable")

        if not tools.os_info.is_linux:
            self.requires("glew/2.1.0@camposs/stable")
            self.requires("libjpeg/9c-r2@camposs/stable")
            self.requires("freetype/2.9.1@bincrafters/stable")
            self.requires("libpng/1.6.36@bincrafters/stable")
            self.requires("libtiff/4.0.9@bincrafters/stable")

    def build_requirements(self):
        if tools.os_info.linux_distro == "linuxmint":
            pack_names = [
                "libgl1-mesa-dev",
                "libglapi-mesa",
                "libsm-dev",
                "libxext-dev",
                "libxt-dev",
                "libglu1-mesa-dev",
                "libfreetype6-dev",
                "libxml2-dev",
                "libexpat1-dev",
                "libicu-dev",
                "libjpeg-turbo8-dev",
                "libtiff5-dev",
                "libglew-dev",
                "libpng-dev",
            ]
            if tools.os_info.os_version.major(fill=False) == "18":
                pack_names.append("libpng12-dev")
            elif tools.os_info.os_version.major(fill=False) == "19":
                pack_names.append("libpng-dev")
            installer = tools.SystemPackageTool()
            for p in pack_names:
                installer.install(p)
        if tools.os_info.linux_distro == "ubuntu":
            pack_names = [
                "libgl1-mesa-dev",
                "libglapi-mesa",
                "libsm-dev",
                "libxext-dev",
                "libxt-dev",
                "libglu1-mesa-dev",
                "libfreetype6-dev",
                "libxml2-dev",
                "libexpat1-dev",
                "libicu-dev",
                "libjpeg-turbo8-dev",
                "libtiff5-dev",
                "libglew-dev",
                "libpng-dev",
            ]
            installer = tools.SystemPackageTool()
            for p in pack_names:
                installer.install(p)

    def system_requirements(self):
        if tools.os_info.linux_distro == "linuxmint":
            pack_names = [
                "libsm6",
                "libxt6",
                "libglu1-mesa",
                "libfreetype6",
                "libxml2",
                "libexpat1",
                "libjpeg-turbo8",
                "libtiff5"
            ]
            if tools.os_info.os_version.major(fill=False) == "18":
                pack_names.extend(["libpng12-0", "libicu55", "libglew1.13"])
            elif tools.os_info.os_version.major(fill=False) == "19":
                pack_names.extend(["libpng16-16", "libicu60", "libglew2.0"])
            installer = tools.SystemPackageTool()
            installer.install(["libgl1", "libgl1-mesa-glx"])
            for p in pack_names:
                installer.install(p)
        if tools.os_info.linux_distro == "ubuntu":
            pack_names = [
                "libsm6",
                "libxt6",
                "libglu1-mesa",
                "libfreetype6",
                "libxml2",
                "libexpat1",
                "libjpeg-turbo8",
                "libtiff5",
                "libpng16-16", 
                "libicu60", 
                "libglew2.0"
            ]
            installer = tools.SystemPackageTool()
            installer.install(["libgl1", "libgl1-mesa-glx"])
            for p in pack_names:
                installer.install(p)

    def source(self):
        tools.get("https://github.com/Kitware/VTK/archive/v{0}.tar.gz".format(self.upstream_version))
        os.rename("VTK-" + self.upstream_version, self.source_subfolder)

    # This is needed until the MR (https://gitlab.kitware.com/vtk/vtk/merge_requests/5467) is merged on a VTK release.
    # Ensure that every signals & slots keywords are replaced by Q_SIGNALS and Q_SLOTS.
    def replace_qt_keyword(self, root):
        for path, subdirs, names in os.walk(root):
            for name in names:
                if fnmatch(name, '*.h'):
                    tools.replace_in_file(os.path.join(path, name), 'signals:', 'Q_SIGNALS:', strict=False)
                    tools.replace_in_file(os.path.join(path, name), 'slots:', 'Q_SLOTS:', strict=False)                   

    def build(self):
        # Import common flags and defines
        import common

        vtk_source_dir = os.path.join(self.source_folder, self.source_subfolder)
        shutil.move("patches/CMakeProjectWrapper.txt", "CMakeLists.txt")

        tools.patch(vtk_source_dir, "patches/optimization.diff")
        tools.patch(vtk_source_dir, "patches/offscreen_size_windows.diff")

        # Patch all headers that contains Qt stuff to use Q_SIGNALS Q_SLOTS variant
        # Ensure that VTK is compiling.
        self.replace_qt_keyword(os.path.join(vtk_source_dir))

        cmake = CMake(self)
        
        # Set common flags
        cmake.definitions["SIGHT_CMAKE_C_FLAGS"] = common.get_c_flags()
        cmake.definitions["SIGHT_CMAKE_CXX_FLAGS"] = common.get_cxx_flags()
        
        cmake.definitions["BUILD_EXAMPLES"] = "OFF"
        cmake.definitions["BUILD_TESTING"] = "OFF"
        cmake.definitions["BUILD_DOCUMENTATION"] = "OFF"

        cmake.definitions["VTK_USE_SYSTEM_EXPAT"] = "ON"
        cmake.definitions["VTK_USE_SYSTEM_JPEG"] = "ON"
        cmake.definitions["VTK_USE_SYSTEM_LIBXML2"] = "ON"
        cmake.definitions["VTK_USE_SYSTEM_PNG"] = "ON"
        cmake.definitions["VTK_USE_SYSTEM_ZLIB"] = "ON"
        cmake.definitions["VTK_USE_SYSTEM_FREETYPE"] = "ON"
        cmake.definitions["VTK_USE_SYSTEM_TIFF"] = "ON"
        cmake.definitions["VTK_USE_SYSTEM_GLEW"] = "ON"

        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared

        cmake.definitions["VTK_Group_StandAlone"] = "OFF"

        cmake.definitions["VTK_USE_GL2PS"] = "ON"
        cmake.definitions["VTK_USE_GLSL_SHADERS"] = "ON"
        cmake.definitions["VTK_USE_TK"] = "OFF"
        cmake.definitions["VTK_LEGACY_REMOVE"] = "OFF"
        cmake.definitions["VTK_USE_PARALLEL"] = "ON"
        cmake.definitions["VTK_USE_HYBRID"] = "ON"
        cmake.definitions["VTK_Group_Qt"] = "OFF"
        cmake.definitions["VTK_WRAP_PYTHON"] = "OFF"
        cmake.definitions["VTK_QT_VERSION"] = "5"
        cmake.definitions["VTK_BUILD_QT_DESIGNER_PLUGIN"] = "OFF"
        cmake.definitions["Module_vtkFiltersFlowPaths"] = "ON"
        cmake.definitions["Module_vtkGUISupportQt"] = "ON"
        cmake.definitions["Module_vtkGUISupportQtOpenGL"] = "ON"
        cmake.definitions["Module_vtkGUISupportQtWebkit"] = "OFF"
        cmake.definitions["Module_vtkGUISupportQtSQL"] = "ON"
        cmake.definitions["Module_vtkRenderingQt"] = "ON"
        cmake.definitions["Module_vtkViewsQt"] = "ON"
        cmake.definitions["Module_vtkIOExport"] = "ON"
        cmake.definitions["Module_vtkImagingStencil"] = "ON"
        cmake.definitions["Module_vtkImagingStatistics"] = "ON"
        cmake.definitions["Module_vtkIOImport"] = "ON"
        cmake.definitions["Module_vtkIOLegacy"] = "ON"
        cmake.definitions["Module_vtkIOGeometry"] = "ON"
        cmake.definitions["Module_vtkIOPLY"] = "ON"
        cmake.definitions["Module_vtkRenderingExternal"] = "ON"

        if tools.os_info.is_macos:
            cmake.definitions["VTK_USE_CARBON"] = "OFF"
            cmake.definitions["VTK_USE_COCOA"] = "ON"

        if not tools.os_info.is_windows:
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = "ON"

        cmake.configure(build_folder=self.build_subfolder)
        cmake.build()
        cmake.install()

    def cmake_fix_path(self, file_path, package_name):
        try:
            tools.replace_in_file(
                file_path,
                self.deps_cpp_info[package_name].rootpath.replace('\\', '/'),
                "${CONAN_" + package_name.upper() + "_ROOT}",
                strict=False
            )
        except:
            self.output.info("Ignoring {0}...".format(package_name))

    def cmake_fix_macos_sdk_path(self, file_path):
        # Read in the file
        with open(file_path, 'r') as file:
            file_data = file.read()

        if file_data:
            # Replace the target string
            file_data = re.sub(
                # Match sdk path
                r';/Applications/Xcode\.app/Contents/Developer/Platforms/MacOSX\.platform/Developer/SDKs/MacOSX\d\d\.\d\d\.sdk/usr/include',
                '',
                file_data,
                re.M
            )

            # Write the file out again
            with open(file_path, 'w') as file:
                file.write(file_data)

    def package(self):
        # Patch all headers that contains Qt stuff to use Q_SIGNALS Q_SLOTS variant
        self.replace_qt_keyword(os.path.join(self.package_folder, 'include'))

        for path, subdirs, names in os.walk(os.path.join(self.package_folder, 'lib', 'cmake')):
            for name in names:
                if fnmatch(name, '*.cmake'):
                    cmake_file = os.path.join(path, name)
                    
                    tools.replace_in_file(
                        cmake_file, 
                        self.package_folder, 
                        '${CONAN_VTK_ROOT}', 
                        strict=False
                    )
                    
                    tools.replace_in_file(
                        cmake_file,
                        os.path.join(self.build_folder, self.build_subfolder),
                        '${CONAN_VTK_ROOT}',
                        strict=False
                    )
                    
                    self.cmake_fix_path(cmake_file, "glew")
                    self.cmake_fix_path(cmake_file, "qt")
                    self.cmake_fix_path(cmake_file, "freetype")
                    self.cmake_fix_path(cmake_file, "libjpeg")
                    self.cmake_fix_path(cmake_file, "libpng")
                    self.cmake_fix_path(cmake_file, "libtiff")
                    self.cmake_fix_path(cmake_file, "zlib")
                    self.cmake_fix_path(cmake_file, "expat")
                    self.cmake_fix_path(cmake_file, "libxml2")
                    self.cmake_fix_macos_sdk_path(cmake_file)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
