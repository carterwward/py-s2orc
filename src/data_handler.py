import hdbscan
from umap import UMAP
import pandas as pd
import json

class PyS2orcDataHandler:
    def __init__(self, s2orc_raw_results: dict):
        self.raw_data = s2orc_raw_results

    def format_embeddings_df(self):
        paper_df = pd.DataFrame.from_dict(
            self.raw_data,
            orient="index",
            columns=["paperId", "title", "year", "tldr", "embedding"],
        )
        paper_df["tldr"] = paper_df["tldr"].apply(lambda x: x["text"] if x else None)
        paper_df.dropna(subset=["embedding"], inplace=True)
        embedding_array = (
            paper_df["embedding"]
            .apply(lambda x: pd.Series(x["vector"]))
            .rename(columns=lambda x: f"embedding_{x}")
        ).values
        fit = UMAP(n_neighbors=15, n_components=2, min_dist=0.0, metric="cosine")
        umap_embeddings = fit.fit_transform(embedding_array)
        cluster = hdbscan.HDBSCAN(
            min_cluster_size=15, metric="euclidean", cluster_selection_method="eom"
        ).fit(umap_embeddings)
        clustered_embeddings = pd.DataFrame(umap_embeddings, columns=["x", "y"])
        clustered_embeddings["label"] = cluster.labels_
        clustered_embeddings.reset_index(drop=True, inplace=True)
        paper_df.drop("embedding", axis=1, inplace=True)
        paper_df.reset_index(drop=True, inplace=True)
        pd.concat(
            [paper_df, clustered_embeddings], axis=1
        ).to_csv("alzheimers_papers.csv", index = False)

with open("data/alzheimers_30000.json", "r") as f:
    raw_data = json.load(f)

dh = PyS2orcDataHandler(raw_data)
dh.format_embeddings_df()
