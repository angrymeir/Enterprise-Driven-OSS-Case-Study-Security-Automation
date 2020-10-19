# Enterprise-Driven Open Source Software: A Case Study on Security Automation
This project contains the code and further resources for the paper *Enterprise-Driven Open Source Software: A Case Study on Security Automation*.  

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4104322.svg)](https://doi.org/10.5281/zenodo.4104322)

## Structure
This repository is structured as followed:

### crawling
Code for crawling CI files, log files and characteristics.

### preprocessing
Code to filter and remove package manager/install instructions.

### tool_usage_detection
Code to detect security tools in CI files, log files and to aggregate findings.

### resources
Resources necessary to run the code. Contains 
- list of security tools
- package manager instructions
- outcome of manual review
- anonymized answers from maintainers

### results
Results from the code of crawling, preprocessing and tool_usage_detection.

## How to Use

1. Install requirements from requirements.txt
2. Download and move [OSS Dataset](https://zenodo.org/record/3742962) to resources.
3. Create GitHub personal access token and add to [01.crawl_ci_files.py](01.crawling/01.crawl_ci_files.py) and [03.crawl_characteristics.py](01.crawling/03.crawl_characteristics.py)
4. Create Travis CI access token and add to [02.crawl_ci_logs.py](01.crawling/02.crawl_ci_logs.py)
5. Start at [01.crawling/01.crawl_ci_files.py](01.crawling/01.crawl_ci_files.py) and run successively until [04.analysis/RQ3/02.languages.py](04.analysis/RQ3/02.languages.py).
6. Results will either be written to the console or to the results folder.
