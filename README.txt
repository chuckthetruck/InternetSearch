WebCrawler, Search Engine, and Create Matrix python programms

python version = 3.7.4

Dependedcies scaper.py:

	requests
	os
	hashlib
	re
	ast

	beautifulsoup4 = 4.8.2
	nltk = 3.4.5

Dependencies SearchEngine.py:
	ast
	copy

	numpy = 1.18.1
	pandas = 1.0.0
	nltk = 3.4.5	

Running scraper.py will create the document repo, the index.txt, dictionary.txt, 
postings_list.txt, and the lines_to_read.txt.

create_matrix.py takes the postings list creates the term frequency matrix.

SearchEngine.py takes in user input, searches the collection and returns the most 
relevant documents form the collection


