from conans import ConanFile, CMake, tools, AutoToolsBuildEnvironment
from conans.util import files
import os
import shutil

class LibVTKConan(ConanFile):
    name = "vtk"
    version = "8.0.1"
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
    license="http://www.vtk.org/licensing/"
    description = "Visualization Toolkit by Kitware"
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"
    short_paths = True

    def requirements(self):
        self.requires("qt/5.11.1@fw4spl/stable")
        self.requires("glew/2.0.0@fw4spl/stable")
        if not tools.os_info.is_linux:
            self.requires("libjpeg/9c@fw4spl/stable")
            self.requires("expat/2.2.5@fw4spl/stable")
            self.requires("libxml2/2.9.8@fw4spl/stable")
            self.requires("freetype/2.9.1@fw4spl/stable")
            self.requires("libpng/1.6.34@fw4spl/stable")
            self.requires("libtiff/4.0.9@fw4spl/stable")
            self.requires("zlib/1.2.11@fw4spl/stable")

    def system_requirements(self):
        if tools.os_info.linux_distro == "ubuntu":
            pack_names = [
                "freeglut3-dev",
                "mesa-common-dev",
                "mesa-utils-extra",
                "libgl1-mesa-dev",
                "libglapi-mesa",
                "libsm-dev",
                "libx11-dev",
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
            installer.update()
            installer.install(" ".join(pack_names))

    def source(self):
        tools.get("https://github.com/Kitware/VTK/archive/v{0}.tar.gz".format(self.version))
        os.rename("VTK-" + self.version, self.source_subfolder)

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

        cmake.definitions["VTK_INSTALL_QT_PLUGIN_DIR"] = os.path.join(self.deps_cpp_info["qt"].rootpath, "plugins")

        cmake.definitions["VTK_USE_GL2P"] = "ON"
        cmake.definitions["VTK_USE_GLSL_SHADER"] = "ON"
        cmake.definitions["VTK_USE_TK"] = "OFF"
        cmake.definitions["VTK_LEGACY_REMOVE"] = "OFF"
        cmake.definitions["VTK_USE_PARALLE"] = "ON"
        cmake.definitions["VTK_USE_HYBRI"] = "ON"
        cmake.definitions["VTK_Group_Qt"] = "OFF"
        cmake.definitions["VTK_WRAP_PYTHON"] = "ON"
        cmake.definitions["VTK_MAKE_INSTANTIATOR"] = "ON"
        cmake.definitions["VTK_QT_VERSION"] = "ON"
        cmake.definitions["Module_vtkFiltersFlowPath"] = "ON"
        cmake.definitions["Module_vtkGUISupportQ"] = "ON"
        cmake.definitions["Module_vtkGUISupportQtOpenG"] = "ON"
        cmake.definitions["Module_vtkGUISupportQtWebkit"] = "OFF"
        cmake.definitions["Module_vtkGUISupportQtSQ"] = "ON"
        cmake.definitions["Module_vtkRenderingQ"] = "ON"
        cmake.definitions["Module_vtkViewsQ"] = "ON"
        cmake.definitions["Module_vtkIOExpor"] = "ON"
        cmake.definitions["Module_vtkImagingStenci"] = "ON"
        cmake.definitions["Module_vtkImagingStatistic"] = "ON"
        cmake.definitions["Module_vtkIOImpor"] = "ON"
        cmake.definitions["Module_vtkIOLegac"] = "ON"
        cmake.definitions["Module_vtkIOGeometr"] = "ON"
        cmake.definitions["Module_vtkIOPL"] = "ON"

        if tools.os_info.is_macos:
            cmake.definitions["VTK_USE_CARBON"] = "OFF"
            cmake.definitions["VTK_USE_COCOA"] = "ON"


        cmake.configure(build_folder=self.build_subfolder)
        cmake.build()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
