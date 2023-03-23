# RDoC Expert Survey Author Finder
Chris Iyer
Updated 3/23/2023

This code uses [pubget](https://neuroquery.github.io/pubget/pubget.html) and [Entrez](https://biopython.org/docs/1.76/api/Bio.Entrez.html) from BioPython to search PubMed Central (PMC) for articles pertaining to a given keyword/task.

These articles are downloaded locally and correspondence emails are extracted. Then, Entrez searches for the number of other PMC papers that cite a given paper, and we select the top &lt;n> (100?) papers. The correspondence emails of these papers are then written to a txt file and returned.

Files:
- `author_finder_functions.py` contains all the functions performing the steps above. Critically, it also contains a dictionary `task_keywords` that decides what to query PMC with based on which task we are searching for. Edit this dictionary to refine results.
- `author_finder.ipynb` is where you will put in a `ROOT_PATH` to write outputs to, a `task_to_run` to search. You may either call each function from `author_finder_functions` in sequence or use `run_author_finder()` to get the emails in one step. Doing so for each task takes somewhere around 5 minutes.

