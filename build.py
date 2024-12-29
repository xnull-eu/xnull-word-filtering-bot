import PyInstaller.__main__
import os
import shutil

def build_exe():
    print("Building XNull Word Filtering Bot executable...")
    
    # Clean previous builds
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    
    # PyInstaller options
    PyInstaller.__main__.run([
        'XNull Word Filtering Bot.py',     # Your main script
        '--name=XNull Word Filtering Bot', # Name of the executable
        '--onefile',                       # Create a single executable
        '--icon=logo.ico',                 # Add icon if you have one
        '--clean',                         # Clean cache
        # Discord.py related imports
        '--hidden-import=discord',
        '--hidden-import=discord.ui',
        '--hidden-import=discord.app_commands',
        '--hidden-import=discord.ext.commands',
        # Fuzzy matching related imports
        '--hidden-import=fuzzywuzzy',
        '--hidden-import=fuzzywuzzy.fuzz',
        '--hidden-import=fuzzywuzzy.process',
        '--hidden-import=Levenshtein',
        # Collect all packages
        '--collect-all=discord',
        '--collect-all=fuzzywuzzy',
        '--collect-all=Levenshtein',
    ])
    
    print("\nBuild complete! Check the 'dist' folder for your executable.")
    print("\nVisit https://www.xnull.eu for more projects and tools!")

if __name__ == "__main__":
    build_exe() 
