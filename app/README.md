# Build instructions
1. download this branch to a local directory (you can either git clone if you're a nerd, or just download the zip file from the `Code` dropdown box and then extract it somewhere)
2. make a directory called `/models` inside the `/app` directory
3. [download this .gguf model](https://huggingface.co/QuantFactory/Llama-3.2-3B-Instruct-abliterated-GGUF/resolve/main/Llama-3.2-3B-Instruct-abliterated.Q4_K_S.gguf?download=true) and move that file into your `/models` directory
4. If you haven't already, install python 3.10+ (preferably 3.11 - that one is supposed to be significantly faster)
5. inside your repo directory, create a `/venvs` directory
6. Inside the `/venvs` directory, create another directory called `/local-rag`
7. inside `/local-rag`, open a terminal, and run the command `python -m venv .`. This will create a virtual python environment for you, which will make package management (and flat out deleting packages) much easier/cleaner.
8. run the command `source bin/activate` to activate your virtual environment. You should have a little prefix in your terminal that says `(local-rag)`
9. now inside the same terminal window, run the command `cd ..`, and then run `cd ..` again. This should navigate you back to your main repo directory. From there, type `cd app`, which will take you to your `/app` directory
10. in here, run `pip install -r requirements.txt`. This will (or should) install all package dependencies into your virtual environment. NOTE: this will take a very long time probably. Allow an hour or two, is my guess.
11. Before building, while still in the `/app` directory, try running the commands `python3 run.py` or `python run.py` (whichever works, I never know which one will work). If the app starts up, you're golden. If not, message me lol.
    - If it fully starts up, with no errors while playing around with it, great! we'll move on to the build.
12. To build, while staying in the `/app` directory, simply run either `python3 build_executable.py` or `python build_executable.py` (again, whichever works). This should run PyInstaller, which will compile a bunch of stuff, and again, will take maybe an hour to run. Go eat some pistachio butter in the meantime.
13. Once that's finished running - you should now have a `/dist/run` folder in your `/app` directory. Navigate to that, and I *think* you should have a `run.dmg` file, among other things, or perhaps just a `run` file. At this point, you're on your own - I have no idea how macs work. First thing to try would be to double click on itand see what happens. If that doesn't work, try opening that directory in your terminal and typing `./run` or `./run.dmg` or whatever the filename is. If that has a weird error, last resort is `sudo ./run` or `sudo ./run.dmg` and then you'll need to enter your password. If all else fails, we'll just work on this later lol.

### happy building!
