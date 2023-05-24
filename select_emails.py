import pandas as pd
import os
import re
from collections import OrderedDict

# Things to note:
# 1. We want to check for duplicates in list. This could be within task list or across.
# This could also be across people we have already contacted. Don't spam people!
# 2. We want to sequentially go down the ranked list.

ROOT_PATH = '/Users/sunjaeshim/Documents/GitHub/author_finder/' # change this to match your local desired path
data_path = os.path.join(ROOT_PATH, 'pubget_data_5_16_2008-2023')# change this to match your local desired path)
survey_path = os.path.join(ROOT_PATH, 'expert_survey_emails')# change this to match your local desired path)
expert_survey_emails_path = os.path.join(survey_path, 'expert_survey_emails_sent.csv') # change this to match your local desired path
all_tasks = ['spatial_cueing', 'visual_search', 'cued_ts', 'ax_cpt', 'flanker', 'stroop', 'stop_signal', 'go_nogo', 'span', 'change_detection', 'n_back']

# Dictionary mapping tasks to cutoffs
cutoffs = {
    'spatial_cueing': 3,
    'visual_search': 3,
    'cued_ts': 4,
    'ax_cpt': 3,
    'flanker': 3,
    'stroop': 3,
    'stop_signal': 3,
    'go_nogo': 4,
    'span': 3,
    'change_detection': 3,
    'n_back': 3,
}

def extract_emails(s):
    # This pattern matches an email address
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    # Find all occurrences of the pattern
    matches = re.findall(pattern, s)
    
    return matches

def main():
    # List to store email and associated task
    email_list = []
    task_list = []

    # Load emails that have been already sent
    # df_sent = pd.read_csv(expert_survey_emails_path)
    # sent_emails = df_sent['Email'].tolist()

    # Global list to track all emails
    global_emails = []

    for task in all_tasks:
        task_emails = []
        # load pubget data csv
        df = pd.read_csv(os.path.join(data_path, task, task + '_output.csv'))
        df['extracted_emails'] = df['emails'].apply(extract_emails)
        
        for i in range(len(df)):
            task_emails.extend(df['extracted_emails'][i])
            
        # De-duplicate while preserving order
        task_emails = list(OrderedDict.fromkeys(task_emails))
        
        # Remove emails that have been already sent
        # task_emails = [email for email in task_emails if email not in sent_emails]
        
        # Enforce the task-specific cutoff
        task_emails = task_emails[:cutoffs[task]]

        # Remove duplicates from different tasks
        task_emails = [email for email in task_emails if email not in global_emails]
        
        # Add to the global email list
        global_emails.extend(task_emails)

        # Add to the final list
        email_list.extend(task_emails)
        task_list.extend([task]*len(task_emails))

    # Create a DataFrame
    df = pd.DataFrame({'Email': email_list, 'Task': task_list})

    # Save to csv
    df.to_csv(f'{survey_path}/expert_survey_emails.csv', index=False)


main()
