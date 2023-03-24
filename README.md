# RDoC Expert Survey Author Finder
Chris Iyer
Updated 3/23/2023

This code uses [pubget](https://neuroquery.github.io/pubget/pubget.html) and [Entrez](https://biopython.org/docs/1.76/api/Bio.Entrez.html) from BioPython to search PubMed Central (PMC) for articles pertaining to a given keyword/task. In order to use this code, you'll have to `pip install pubget` and `pip install Bio`.

What this code does:
These articles are downloaded locally and correspondence emails are extracted. Then, Entrez searches for the number of other PMC papers that cite a given paper, and we select the top &lt;n> (100?) papers. The correspondence emails of these papers are then written to a txt file and returned.

Files:
- `author_finder_functions.py` contains all the functions performing the steps above. Critically, it also contains a dictionary `task_keywords` that decides what to query PMC with based on which task we are searching for. Edit this dictionary to refine results.
- `author_finder.ipynb` is where you will put in a `ROOT_PATH` to write outputs to, and a `task_to_run` to search. You may either call each function from `author_finder_functions` in sequence or use `run_author_finder()` to get the emails in one step. Doing so for each task takes somewhere around 5 minutes.

Current problems:
1. The keywords are imperfect. Including "task" will exclude a lot of good papers, but leaving it out means we get articles like [this article](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4359377/) that are about the 'stop codon acting as a stop signal' and not about the stop signal task at all.
2. A few emails are lost (somewhere in the ballpark of 2%). I'm not worried.
3. We are sorting by # of citations only of other papers in PMC (not necessarily all citations of the paper, but just the ones in PMC).
4. The search results are not lining up to what I get when I manually search using the same query in [PMC Advanced Search](https://www.ncbi.nlm.nih.gov/pmc/advanced). I'm looking into this. 
