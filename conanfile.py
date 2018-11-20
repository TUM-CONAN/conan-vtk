import os
import shutil

from conans import ConanFile, CMake, tools, AutoToolsBuildEnvironment
from conans.util import files


class LibVTKConan(ConanFile):
    name = "vtk"
    short_version = "8.0.1"
    version = "{0}-r1".format(short_version)
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    exports = [
        "patches/CMakeProjectWrapper.txt",
        "patches/IO_Import_CMakeLists.diff",
        "patches/optimization.diff",
        "patches/CMakeLists_glew.diff",
        "patches/QVTKOpenGLWidget.diff",
        "patches/offscreen_size_windows.diff"
    ]
    url = "https://gitlab.lan.local/conan/conan-vtk"
    license = "http://www.vtk.org/licensing/"
    description = "Visualization Toolkit by Kitware"
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"
    short_paths = True

    def configure(self):
        del self.settings.compiler.libcxx
        if 'CI' not in os.environ:
            os.environ["CONAN_SYSREQUIRES_MODE"] = "verify"

    def requirements(self):
        self.requires("qt/5.11.2@sight/stable")
        self.requires("glew/2.0.0@sight/stable")

        if tools.os_info.is_windows:
            self.requires("libxml2/2.9.8@sight/stable")
            self.requires("expat/2.2.5@sight/stable")
            self.requires("zlib/1.2.11@sight/stable")

        if not tools.os_info.is_linux:
            self.requires("libjpeg/9c@sight/stable")
            self.requires("freetype/2.9.1@sight/stable")
            self.requires("libpng/1.6.34@sight/stable")
            self.requires("libtiff/4.0.9@sight/stable")

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
                "libpng-dev",
                "libjpeg-turbo8-dev",
                "libtiff5-dev"
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
                "libicu55",
                "libpng16-16",
                "libjpeg-turbo8",
                "libtiff5"
            ]
            installer = tools.SystemPackageTool()
            installer.install(["libgl1", "libgl1-mesa-glx"])
            for p in pack_names:
                installer.install(p)

    def source(self):
        tools.get("https://github.com/Kitware/VTK/archive/v{0}.tar.gz".format(self.short_version))
        os.rename("VTK-" + self.short_version, self.source_subfolder)

    def build(self):
        vtk_source_dir = os.path.join(self.source_folder, self.source_subfolder)
        shutil.move("patches/CMakeProjectWrapper.txt", "CMakeLists.txt")
        tools.patch(vtk_source_dir, "patches/IO_Import_CMakeLists.diff")
        tools.patch(vtk_source_dir, "patches/optimization.diff")
        tools.patch(vtk_source_dir, "patches/CMakeLists_glew.diff")
        tools.patch(vtk_source_dir, "patches/QVTKOpenGLWidget.diff")
        tools.patch(vtk_source_dir, "patches/offscreen_size_windows.diff")

        cmake = CMake(self)
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
        cmake.definitions["TK_Group_Qt"] = "OFF"
        cmake.definitions["VTK_WRAP_PYTHON"] = "OFF"
        cmake.definitions["VTK_MAKE_INSTANTIATORS"] = "ON"
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
        tools.replace_in_file(
            file_path,
            self.deps_cpp_info[package_name].rootpath.replace('\\', '/'),
            "${CONAN_" + package_name.upper() + "_ROOT}"
        )

    def package(self):
        if not tools.os_info.is_windows:
            vtkConfig_file = os.path.join(self.package_folder, "lib", "cmake", "vtk-8.0", "VTKConfig.cmake")

            tools.replace_in_file(
                vtkConfig_file,
                self.package_folder,
                "${CONAN_VTK_ROOT}"
            )

            tools.replace_in_file(
                vtkConfig_file,
                os.path.join(self.build_folder, self.build_subfolder),
                "${CONAN_VTK_ROOT}"
            )

        vtkTargets_file = os.path.join(self.package_folder, "lib", "cmake", "vtk-8.0", "VTKTargets.cmake")
        vtkModules_dir = os.path.join(self.package_folder, "lib", "cmake", "vtk-8.0", "Modules")

        self.cmake_fix_path(vtkTargets_file, "glew")
        self.cmake_fix_path(os.path.join(vtkModules_dir, "vtkglew.cmake"), "glew")
        self.cmake_fix_path(os.path.join(vtkModules_dir, "vtkGUISupportQt.cmake"), "qt")
        self.cmake_fix_path(os.path.join(vtkModules_dir, "vtkGUISupportQtOpenGL.cmake"), "qt")
        self.cmake_fix_path(os.path.join(vtkModules_dir, "vtkGUISupportQtSQL.cmake"), "qt")
        self.cmake_fix_path(os.path.join(vtkModules_dir, "vtkRenderingQt.cmake"), "qt")
        self.cmake_fix_path(os.path.join(vtkModules_dir, "vtkViewsQt.cmake"), "qt")

        if not tools.os_info.is_linux:
            self.cmake_fix_path(vtkTargets_file, "freetype")
            self.cmake_fix_path(os.path.join(vtkModules_dir, "vtkfreetype.cmake"), "freetype")
            self.cmake_fix_path(os.path.join(vtkModules_dir, "vtkjpeg.cmake"), "libjpeg")
            self.cmake_fix_path(os.path.join(vtkModules_dir, "vtkpng.cmake"), "libpng")
            self.cmake_fix_path(os.path.join(vtkModules_dir, "vtktiff.cmake"), "libtiff")

        if tools.os_info.is_windows:
            self.cmake_fix_path(vtkTargets_file, "zlib")
            self.cmake_fix_path(os.path.join(vtkModules_dir, "vtkexpat.cmake"), "expat")
            self.cmake_fix_path(os.path.join(vtkModules_dir, "vtkzlib.cmake"), "zlib")
            self.cmake_fix_path(os.path.join(vtkModules_dir, "vtkpng.cmake"), "zlib")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
