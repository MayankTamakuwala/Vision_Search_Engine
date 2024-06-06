# Vision Search Engine

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [License](#license)


## Introduction

Vision Search Engine is a sophisticated and versatile search engine designed to provide highly accurate and efficient search capabilities. Leveraging a suite of advanced algorithms and techniques, this project is equipped to handle a wide array of search functionalities, ensuring precise and relevant results. Key features include tokenization, normalization, boolean retrieval, ranked retrieval, and positional indexing.

The engine employs Variable-Byte Encoding for data compression and On-disk Indexing to manage large datasets efficiently. It supports probabilistic retrieval models, stemming and lemmatization for text processing, stopword removal, and synonym handling to enhance search relevance. Additional features such as phrase searching, wildcard queries, real-time indexing, multi-threaded query processing, and K-means clustering further enhance its performance and flexibility.

With an organized project structure, Vision Search Engine is designed to handle data from diverse sources, including JSON, TXT, and PDF documents. The project also supports API integration, making it easy to incorporate into other applications.

## Features

- Tokenization: Breaks down text into tokens.
- Normalization: Processes text to a standard form.
- Boolean Retrieval: Supports boolean queries.
- Ranked Retrieval: Ranks documents based on relevance.
- Positional Indexing: Indexes terms with their positions in the document.
- Variable-Byte Encoding: Compresses index data to save space.
- On-disk Indexing: Efficiently handles large datasets by storing index data on disk.
- Probabilistic Retrieval: Implements probabilistic models for query processing.
- Stemming and Lemmatization: Reduces words to their base or root form.
- Stopword Removal: Eliminates common words that do not contribute to search relevance.
- Synonym Handling: Recognizes and processes synonyms to improve search results.
- Phrase Searching: Supports searching for exact phrases.
- K-means Clustering: Groups similar documents together for improved search relevance and analysis.
- Wildcard Queries: Allows for flexible search patterns with wildcards.
- Real-time Indexing: Supports real-time updates to the index.
- Multi-threaded Query Processing: Enhances performance with concurrent query handling.
- API Integration: Provides easy integration with other applications through APIs.

## Installation

To install and run the Vision Search Engine, follow these steps:

1. `git clone https://github.com/MayankTamakuwala/Vision_Search_Engine.git`
2. `cd Vision_Search_Engine`
3. `pip install -r requirements.txt`

## Usage

- To use the search engine as an API:

`uvicorn main:app --reload`

- To use the search engine as a terminal application:

`python TermDocumentIndexer.py`

## Project Structure

The project consists of the following directories and files:

- compression/: Contains scripts for data compression using <b>Variabe Byte Encoding</b>.
- mlb/: Includes the 4000 JSON docs corpus web scraped from Major League Baseball website `https://www.mlb.com` used for indexing and searching.
- nps/: Includes the 36804 JSON docs corpus web scraped from National Park Service website `https://www.nps.gov/` used for indexing and searching.
- MobyDick/: Includes the text corpus of first 10 chapters of Moby Dick used for indexing and searching.
- database/: Manages database-related operations.
- documents/: Contains scripts for data processing from JSON, TXT and PDF docs.
- indexing/: Contains indexing algorithms.
- querying/: Handles query processing and retrieval.
- text/: Includes text processing scripts.
- TermDocumentIndexer.py: Main script to run the search engine as a terminal application.
- api_helper.py: Helper functions for API integration.
- main.py: Main script to run the search engine as an API.

## License

This project is licensed under the MIT License. See the LICENSE file for details.