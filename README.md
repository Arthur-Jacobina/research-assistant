# Setup

```(bash)
uv sync
uv run main.py
```

In a new terminal
```(bash)
uv run mlflow ui --port 5000
```

Steps for fully ingesting the paper
1) Download
    1.1) Upload to Bucket
2) Read 
3) Parse
    3.1) Use NLP to extract formulas per section 
4) Insert to neo4j database
    labels:
        :PAPER
        :SECTION
        :FORMULA
        :CITATION
    Relationships:
        (:SECTION) - [:WITHIN] -> (:PAPER) # first section is the root
        (:CITATION) - [:CITED_IN] -> (:SECTION)
        (:FORMULA) - [:USED_IN] -> (:SECTION)
        (:SECTION) - [:LEFT_CHILD] -> (:SECTION) # parent to child
        (:SECTION) - [:RIGHT_SIBLING] -> (:SECTION) # sibling connections