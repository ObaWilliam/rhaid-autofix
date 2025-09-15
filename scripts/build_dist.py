import subprocess, sys
print('Using python:', sys.executable)
subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'build'], cwd='.')
subprocess.check_call([sys.executable, '-m', 'build', '--sdist', '--wheel', '--outdir', 'dist'], cwd='.')
print('Built distributions in dist/')
