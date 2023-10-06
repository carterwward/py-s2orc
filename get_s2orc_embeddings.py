import json
import argparse
from src.s2orc import PyS2orc

def main():
    parser = argparse.ArgumentParser(
        description="This script retrieves the sentence embeddings from S2orc API using\
        some topic query. The script requires the number of papers to be retrieved\
        and the topic query."
    )
    parser.add_argument("query")
    parser.add_argument("sample_size")
    parser.add_argument("start_year")
    parser.add_argument("end_year")
    args = parser.parse_args()
    s2orc = PyS2orc()
    search_dict = s2orc.paper_embeddings_search(args.query, int(args.sample_size),
                                                int(args.start_year),
                                                int(args.end_year))
    with open(f"data/{args.query}_{args.sample_size}.json", "w") as f:
        json.dump(search_dict, f, indent=4)


if __name__ == "__main__":
    main()
