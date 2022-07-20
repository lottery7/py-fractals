from cx_Freeze import Executable, setup

executables = [Executable('src/main.py', target_name='run.exe', base='Win32GUI',
                          icon='res/icon.ico'),
               # Executable('src/main.py', target_name='newRun.exe', base='Win32GUI',
               #            icon='res/icon.ico')
]

packages = ['OpenGL', 'PyQt5']
include_files = ['res']

options = {
    'build_exe': {
        'include_msvcr': True,
        'packages': packages,
        'include_files': include_files,
        'build_exe': 'build',
        }
}

setup(name='Fractals',
      version='0.1',
      description='Drawing fractals',
      executables=executables,
      options=options)
