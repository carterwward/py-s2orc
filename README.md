# PyS2orc
A python class for easily communicating with the s2orc API.

## Set-up
1. Create a virtual environment:
`python -m venv venv`

2. Activate the virtual environment you created: `source venv/bin/activate`

3. Install project dependencies: `pip install -r requirements.txt`

## Usage
### get_s2orc_embeddings.py
`python get_s2orc_embeddings.py <query> <sample size> <start year> <end year>`

**Description**:
Requests the relevance search end-point of the S2orc API for paper embedding and metadata.

- `<query>`: The key-word or key-phrase in the relevance search query.
- `<sample_size`: Maximum total number of paper results to return.
-  `<start year>`: The first year of the time span the query should cover.
- `<end year>`: The last year of the time span the query should cover.