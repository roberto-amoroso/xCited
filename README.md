# xCited    
 Download all PDFs of an author's publications given the Google Scholar ID!  
  
# Step 1: Install  
```  
$ pip install -r requirements.txt  
```  
# Step 2: Find your Google Scholar ID  
The Google Scholar ID is a `string` of **12 characters** corresponding to the value of the `user` field in the URL of your Google Scholar profile.  
  
> ***Example***: <br/>  
>  If your Google Scholar profile URL is: <br/>  
> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; *ht<span>tps://scholar.google.it/citations?user=**VVrumKsAJEJE**&hl=en</span>* <br/>  
> then your Google Scholar ID is **VVrumKsAJEJE**  
  
# Step 3: Download!  
```  
$ python xCited.py <SCHOLAR_ID>  
```  
The downloaded PDFs will be saved in the format:  
```  
'./<SCHOLAR_ID>/<year_publication>_<title_publication>.pdf'  
```
if `year_publication` is available, otherwise:
```  
'./<SCHOLAR_ID>/<title_publication>.pdf'  
```

# Usage
All the information in this document can be accessed directly by viewing the `xCited.py` script help message via the `-h` or `--help` argument.

For convenience, follows the program invocation prototype:
```
$ python xCited.py [-h] [-v] [-w NUM_WORKERS] scholar_id
```

### Positional Arguments:

 - `scholar_id` the Google Scholar ID is a string of 12 characters corresponding to value of the `user` field in the URL of your profile.

### Optional Arguments:

 - `-h, --help`            show an help message and exit.
 - `-v, --verbose`         if set, it shows a progress bar for each downloaded file, otherwise it shows a single progress bar for all files.   
 - `-w NUM_WORKERS, --num_workers NUM_WORKERS` number of workers (threads) used during downloads (**DEFAULT 4**).
