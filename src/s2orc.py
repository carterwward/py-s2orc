import requests
import os
from dotenv import load_dotenv
from tqdm import tqdm


def unpack_merge_request_results(
    results_dict: dict, request_json: dict, id_field: str, data_field: str
) -> int:
    # TODO: Check for code 429, returning none and letting the program know to pause
    # and retry.
    if data_field not in request_json:
        # TODO: Raise exception
        print(request_json)
        os._exit(1)
    new_results = {
        data_dict[id_field]: data_dict for data_dict in request_json[data_field]
    }
    results_dict.update(new_results)
    return len(new_results)


class PyS2orc:
    SEARCH_ENDPOINT = "https://api.semanticscholar.org/graph/v1/paper/search"
    EMBEDDING_REQUEST_FIELDS = "title,authors,year,journal"
    BATCH_LIMIT = 100
    PAGINATED_LIMIT = 10000
    PAPER_ID = "paperId"
    DATA_FIELD = "data"

    def __init__(self) -> None: # TODO: add API keys and stuff as optional args.
        load_dotenv()
        self.s2_api_key = os.getenv("S2_API_KEY")

    def paper_embeddings_search(self, query: str, sample_size: int,
                                start_year: int, end_year: int) -> dict:
        results_dict = {}

        if sample_size >= self.PAGINATED_LIMIT:
            self.paginate_by_year(
                endpoint=self.SEARCH_ENDPOINT,
                query=query,
                sample_size=sample_size,
                fields=self.EMBEDDING_REQUEST_FIELDS,
                results=results_dict,
                id_field=self.PAPER_ID,
                data_field=self.DATA_FIELD,
                start_year=start_year,
                end_year=end_year
            )
        elif sample_size > self.BATCH_LIMIT:
            self.paginate_by_batch(
                endpoint=self.SEARCH_ENDPOINT,
                query=query,
                sample_size=sample_size,
                fields=self.EMBEDDING_REQUEST_FIELDS,
                results=results_dict,
                id_field=self.PAPER_ID,
                data_field=self.DATA_FIELD,
                start_year=start_year,
                end_year=end_year
            )
        else:
            query_results = self.request_s2orc_api(
                endpoint=self.SEARCH_ENDPOINT,
                query=query,
                batch_limit=sample_size,
                offset=0,
                fields=[self.EMBEDDING_REQUEST_FIELDS],
                start_year=start_year,
                end_year=end_year
            )
            unpack_merge_request_results(
                results_dict, query_results, self.PAPER_ID, self.DATA_FIELD
            )

        return results_dict

    def paginate_by_batch(self, **kwargs):
        # Check if results dict is not empty.
        size_limit = kwargs["sample_size"]
        if len(kwargs["results"]) > 0:
            # Adjust the sample size accordingly.
            size_limit += len(kwargs["results"])

        offset = 0
        pbar = tqdm(total=kwargs["sample_size"])
        pbar.set_description("Request Progress")
        while len(kwargs["results"]) < size_limit:
            query_results = self.request_s2orc_api(
                endpoint=kwargs["endpoint"],
                query=kwargs["query"],
                batch_limit=self.BATCH_LIMIT,
                offset=offset,
                fields=kwargs["fields"],
                start_year=kwargs["start_year"],
                end_year=kwargs["end_year"]
            )
            number_new_results = unpack_merge_request_results(
                kwargs["results"], query_results,
                kwargs["id_field"], kwargs["data_field"]
            )
            pbar.update(number_new_results)
            offset += number_new_results

        pbar.close()
        print("Request Complete.")

    def paginate_by_year(self, **kwargs):
        years = range(kwargs["start_year"], kwargs["end_year"], 1)
        num_years = len(years)
        year_pairs = [(years[i], years[i+1]) for i in range(0, num_years-1, 2)]
        results_per_year = round(kwargs["sample_size"] / len(year_pairs))
        for i, (start_year, end_year) in enumerate(year_pairs):
            print(f"Requesting {start_year} - {end_year}...")
            self.paginate_by_batch(
                endpoint=self.SEARCH_ENDPOINT,
                query=kwargs["query"],
                sample_size=results_per_year,
                fields=kwargs["fields"],
                results=kwargs["results"],
                id_field=kwargs["id_field"],
                data_field=kwargs["data_field"],
                start_year=start_year,
                end_year=end_year
            )

    def request_s2orc_api(self, **kwargs):
        req = requests.get(
                kwargs["endpoint"],
                headers={"X-API-KEY": self.s2_api_key},
                params={
                    "query": kwargs["query"],
                    "limit": kwargs["batch_limit"],
                    "offset": kwargs["offset"],
                    "fields": kwargs["fields"],
                    "year": f"{kwargs['start_year']}-{kwargs['end_year']}"
                },
            )
        return req.json()
