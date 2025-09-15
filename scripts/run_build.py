import sys, subprocess
print('python:', sys.executable)
subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'build'])
import build
builder = build.ProjectBuilder('.')
builder.build('wheel', outdir='dist')
builder.build('sdist', outdir='dist')
print('done')
