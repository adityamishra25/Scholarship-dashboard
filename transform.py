#!/usr/bin/env python
# coding: utf-8

# In[19]:


import pandas as pd
import numpy as np


# In[20]:


agra=pd.read_csv('Desktop/data/registry_Agra.csv')
kanpur= pd.read_csv('Desktop/data/registry_Kanpur.csv')
lucknow= pd.read_csv('Desktop/data/registry_Lucknow.csv')
prayagraj= pd.read_csv('Desktop/data/registry_Prayagraj.csv')
varanasi= pd.read_csv('Desktop/data/registry_Varanasi.csv')
payments= pd.read_csv('Desktop/data/payment_logs.csv')
applications=pd.read_csv('Desktop/data/application_status.csv')


# In[21]:


agra.head()


# In[22]:


##Fix column names (Kanpur & Lucknow have different names)

rename_map = {
    "category_type": "category",
    "district_name": "district",
    "grade_level":   "class",
    "reg_date":      "registration_date"
}
kanpur.rename(columns=rename_map, inplace=True)
lucknow.rename(columns=rename_map, inplace=True)

print("Columns fixed!")


# In[23]:


##Combine all districts into one table

registry = pd.concat([agra, kanpur, lucknow, prayagraj, varanasi], ignore_index=True)

print("Total students:", len(registry))
print(registry.head())


# In[24]:


registry.duplicated().sum()


# In[25]:


payments.describe()


# In[26]:


# Remove duplicates
registry.drop_duplicates(inplace=True)


# In[27]:


###Clean the data

import re

def clean_age(val):
    if pd.isna(val): return None
    match = re.search(r"(\d{1,2})", str(val))
    if match:
        age = int(match.group(1))
        return age if 5 <= age <= 25 else None
    return None

def clean_class(val):
    if pd.isna(val) or str(val).strip() == "": return None
    match = re.search(r"(\d{1,2})", str(val))
    return f"Class {match.group(1)}" if match else None

registry["age_clean"]   = registry["age"].apply(clean_age)
registry["class_clean"] = registry["class"].apply(clean_class)
applications["status"]  = applications["status"].str.strip().str.title()
payments["payment_status"] = payments["payment_status"].str.strip().str.title()


# In[28]:


##See key numbers

print("=== Students per District ===")
print(registry["district"].value_counts())

print("\n=== Application Status ===")
print(applications["status"].value_counts())

print("\n=== Payment Status ===")
print(payments["payment_status"].value_counts())

print("\n=== ALERT: Negative Payments ===")
print((payments["amount"] < 0).sum(), "negative transactions found!")


# In[29]:


##Save to database

import sqlite3

conn = sqlite3.connect('Desktop/data/pipeline.db')
registry.to_sql("registry",         conn, if_exists="replace", index=False)
payments.to_sql("payments",         conn, if_exists="replace", index=False)
applications.to_sql("applications", conn, if_exists="replace", index=False)
conn.close()

print("Saved to pipeline.db")


# In[30]:


##Make a quick chart
import plotly.express as px

dist_counts = registry["district"].value_counts().reset_index()
dist_counts.columns = ["District", "Students"]

fig = px.bar(dist_counts, x="District", y="Students",
             title="Student Registrations by District",
             color="District", text="Students")
fig.show()


# In[31]:


# Merge payment data

master = registry.merge(
    payments,
    on='student_id',
    how='left'
)


# In[32]:


master.describe()


# In[33]:


# Merge application status

master = master.merge(
    applications,
    on='student_id',
    how='left'
)


# In[34]:


# Save master dataset
master.to_csv(
    'Desktop/data/processed/master_dataset.csv',
    index=False
)


# In[35]:


print(master.head())
print(master.shape)


# In[ ]:



