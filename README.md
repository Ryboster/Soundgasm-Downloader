# Soundgasm.net downloader

### How to start?

1. Download the repository as .zip and unpack it
2. Unpack firefox.zip inside the script's folder (where you can see `main.py`)
3. Open a terminal or shell and navigate to the script's folder (same folder as in previous step)
4. Download the requirements by typing in the following command:
```
pip install -r requirements.txt
```
5. Your program is now ready to start. Type in:
```
python3 main.py
```

Then you'll be prompted to enter the author's username. **Keep in mind**, this has to match the username visible in the URl. For instance, for the following URl: https://soundgasm.net/u/Helion/Ode-To-Joy-by-Friedrich-Schiller-English-Translation, the author's name must be spelled `Helion`.


### How does it work
After typing in the username, you will begin downloading that user's entire portfolio from top to bottom.

The files will be saved with names matching those visible on the user's profile. **Keep in mind** there is no "crazy name" handling. If the name has slashes, the file won't be downloaded.

The files will all be saved inside a newly created folder with your author's name.
