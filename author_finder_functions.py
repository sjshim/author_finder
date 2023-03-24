##### Definitions

import numpy as np
import os
from Bio import Entrez
import xml.etree.ElementTree as ET

######### CHANGE THIS! KEYWORDS FOR PUBMED CENTRAL SEARCH
######### {'internal_task_name': ['query_keyword1', 'query_keyword2']}
task_keywords = {
    'spatial_cueing': ['spatial cueing', 'Posner cueing', 'attention network task'],
    'visual_search': ['visual search'],
    'cued_ts': ['cued task switching', 'cued task-switching', 
                            'spatial task switching', 'spatial task-switching'],
    'ax_cpt': ['AX-CPT', 'AXCPT', 'dot pattern expectancy'],
    'flanker': ['flanker'],
    'stroop': ['stroop'],
    'stop_signal': ['stop-signal', 'stop signal'],
    'go_nogo': ['go/no go', 'go/no-go', 'go-no go', 'go no go', 'go no-go'],
    'span': ['span task', 'simple span task', 'operation span task', 'complex span task'],
    'change_detection': ['change detection task'],
    'n_back': ['n-back', 'n back', 'nback']
}

###### 1. Execute pubget query

def format_keywords(keywords, field='Abstract'):
    s = f'{keywords[0]}[{field}]'
    for i in range(1,len(keywords)):
        s += f' OR {keywords[i]}[{field}])'
    return '(' + s + ')'

def do_pubget_query(keywords, outpath, minyear=2013):
    query = f'(("{minyear}"[Publication Date] : "3000"[Publication Date]) AND ' + format_keywords(keywords)

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

def get_all_emails(query_path):
    papers = []
    count = 1
    for artset in [i for i in os.listdir(query_path) if i.endswith('.xml')]:
        print(f'Article set #{count}:')
        count += 1
        papers += get_emails_from_articleset(os.path.join(query_path, artset))

    papers_with_emails = [i for i in papers if len(i['emails']) > 0]
    print(f'Result: {len(papers)} papers; {len(papers_with_emails)} with emails.')
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

##### 4. Final output of emails to send to

def write_email_txt(papers, dir_to_write):
    all_emails = [email for paper in papers for email in paper['emails']]
    all_emails = np.unique(all_emails)

    with open(os.path.join(dir_to_write, 'emails.txt'), 'w') as file:
        file.write('\n'.join(all_emails))    

    return all_emails

# All-in-one run
def run_author_finder(task_to_run, ROOT_PATH):
    outpath = os.path.join(ROOT_PATH, task_to_run)

    # pubget query will write a directory at the outpath with the search results
    do_pubget_query(task_keywords[task_to_run], outpath)

    query_path = os.path.join(outpath, 
                              [i for i in os.listdir(ROOT_PATH + task_to_run) if i.startswith('query')][0],
                              'articlesets')
    # gets list of dicts with pmcid and emails
    papers = get_all_emails(query_path)

    # gets top 100 most cited
    papers_top = get_most_cited(papers, n=100)

    # write csv with top 100 emails
    all_emails = write_email_txt(papers_top, outpath)

    return all_emails




