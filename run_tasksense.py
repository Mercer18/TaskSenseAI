import sys
import os

# Add the project root to sys.path so 'tasksenseai' package can be found
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from tasksenseai.main import main

if __name__ == '__main__':
    main()

