2##### Definitions

import numpy as np
import pandas as pd
import os
from Bio import Entrez
import xml.etree.ElementTree as ET

######### CHANGE THIS! KEYWORDS FOR PUBMED CENTRAL SEARCH
######### {'internal_task_name': ['query_keyword1', 'query_keyword2']}
task_keywords = {
    'spatial_cueing': ['spatial cueing task', 'Posner cueing task', 'Posner paradigm', 'spatial cueing paradigm'], # , 'attention network task'
    'visual_search': ['visual search task', 'visual search paradigm'],
    'cued_ts': ['cued task switching', 'cued task-switching', 'spatial task switching', 'spatial task-switching'], # 'task switching task'
    'ax_cpt': ['AX-CPT', 'AXCPT', 'dot pattern expectancy'],
    'flanker': ['flanker task'],
    'stroop': ['stroop task'],
    'go_nogo': ['go/no go task', 'go/no-go task', 'go-no go task', 'go no go task', 'go no-go task'],
    'span': ['span task'],
    'change_detection': ['change detection task'],
    'n_back': ['n-back task', 'n back task', 'nback task'],
    'stop_signal': ['stop-signal task', 'stop signal task'],
}

###### 1. Execute pubget query

def format_keywords(keywords, field='Abstract'):
    if len(keywords) == 1:
        return f'({keywords[0]}[{field}])' 
    else:
        return f'({format_keywords(keywords[1:])} OR {keywords[0]}[{field}])'

def do_pubget_query(keywords, outpath, minyear=2013):
    query = format_keywords(keywords) 
    query += f' AND ("{minyear}"[Publication Date] : "3000"[Publication Date])'

    command = f'pubget run {outpath} -q "{query}"'
    os.system(command) 

###### 2. Collect PMCIDs and emails of downloaded pubget files

def get_emails_from_articleset(set_path):
    tree = ET.parse(set_path)
    root = tree.getroot()
    emails =[]
    for i in range(len(root)):
        emails.append({"pmcid": [j.text for j in root[i].iter('article-id') if j.attrib['pub-id-type'] == 'pmc'][0],
                    "emails": [i.text for i in root[i].iter('email')]})
        
    found = len([i for i in emails if len(i['emails']) > 0])
    print(f"Out of {len(emails)} papers, {found} had emails and {len(emails) - found} did not.")
    return emails

def get_all_emails(outpath):
    articleset_path = os.path.join(outpath, 
                                [i for i in os.listdir(outpath) if i.startswith('query')][0],
                                'articlesets')
    papers = []
    count = 1
    for artset in [i for i in os.listdir(articleset_path) if i.endswith('.xml')]:
        print(f'Article set #{count}:')
        count += 1
        papers += get_emails_from_articleset(os.path.join(articleset_path, artset))

    # papers_with_emails = [i for i in papers if len(i['emails']) > 0]
    return papers

##### 3. Get citations on all these papers and pick the top 100

def get_most_cited(papers, n = 100):
    Entrez.email = 'csiyer@stanford.edu'

    for i in range(len(papers)):
        id = papers[i]['pmcid']

        handle = Entrez.elink(dbfrom="pmc", db='pmc', id=id, linkname='pmc_pmc_citedby')
        record = Entrez.read(handle)
        test = record[0]['LinkSetDb']
        handle.close()

        citation_count = 0
        if (len(test) > 0): # filters out 0 citations
            citation_count = len(record[0]['LinkSetDb'][0]['Link'])

        papers[i]['citation_count'] = citation_count

    # sort, select top <n>, and return
    papers_sorted = sorted(papers, key=lambda x: int(x['citation_count']), reverse=True)[:n]
    return papers_sorted

##### 4. Final output of emails to send to either csv or txt

def write_email_txt(papers, outpath, *args):
    all_emails = [email for paper in papers for email in paper['emails']]
    all_emails = np.unique(all_emails)

    with open(os.path.join(outpath, 'emails.txt'), 'w') as file:
        file.write('\n'.join(all_emails))    

    return all_emails

# 5 (optional). get csv with all the information we need to validate this approach
def write_papers_csv(papers, outpath, task_to_run):

    # get article metadata output
    meta_path = os.path.join(outpath, 
                          [i for i in os.listdir(outpath) if i.startswith('query')][0],
                          'subset_allArticles_extractedData/metadata.csv')

    meta = pd.read_csv(meta_path)[['pmcid', 'doi', 'title', 'journal','publication_year']]

    # deduplicate emails
    papers_dd = [{'pmcid': int(i['pmcid']), 'emails': np.unique(i['emails']), 'citation_count': i['citation_count']} for i in papers]

    out = pd.DataFrame(columns = list(meta.columns) + [i for i in papers_dd[0].keys() if i != 'pmcid'])

    for i in range(len(papers_dd)):
        meta_row = meta[meta.pmcid == papers_dd[i]['pmcid']]
        out.loc[i] = {
            'pmcid': papers_dd[i]['pmcid'],
            'doi': meta_row.doi.iloc[0],
            'title': meta_row.title.iloc[0],
            'journal': meta_row.journal.iloc[0],
            'publication_year': meta_row.publication_year.iloc[0],
            'citation_count': papers_dd[i]['citation_count'],
            'emails': papers_dd[i]['emails'],
        }
    out.to_csv(os.path.join(outpath, task_to_run + '_output.csv'))
    return out

# All-in-one run
def run_author_finder(tasks_to_run, ROOT_PATH, output = 'txt'):

    for task_to_run in tasks_to_run:
        print('STARTING TASK: ' + task_to_run)
        outpath = os.path.join(ROOT_PATH, task_to_run)

        # pubget query will write a directory at the outpath with the search results
        do_pubget_query(task_keywords[task_to_run], outpath)

        # gets list of dicts with pmcid and emails
        papers = get_all_emails(outpath)

        # gets top 100 most cited
        papers_top = get_most_cited(papers, n=100)

        # write file with top 100 emails
        if output == 'csv':
            all_emails = write_papers_csv(papers_top, outpath, task_to_run)
        else:
            all_emails = write_email_txt(papers_top, outpath)

    return 'Done!'




