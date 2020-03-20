import sys

if len(sys.argv) < 2:
    print('No input file.')
    sys.exit(1)

print('Loading modules...')
from Analysis import AnalysisShell

AnalysisShell(sys.argv[1]).start()
