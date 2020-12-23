


# xCited  
  Download all PDFs of an author's publications given the Google Scholar ID!

# Step 1: Install
```
$ pip install -r requirements.txt
```
# Step 2: Find your Google Scholar ID
The Google Scholar ID is a `string` of **12 characters** corresponding to the value of the `user` field in the URL of your Google Scholar profile.

> ***Example***: 
> If your Google Scholar profile URL is: <br/>
> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; *ht<span>tps://scholar.google.it/citations?user=**VVrumKsAJEJE**&hl=en</span>* <br/>
> then your Google Scholar ID is **VVrumKsAJEJE**

# Step 3: Download!
```
$ python scholarly_api.py <SCHOLAR_ID>
```
The downloaded PDFs will be saved in the format:
```
'./<scholar_id>/<year_publication>_<title_publication>.pdf'
```
