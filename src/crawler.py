import asyncio
import aiohttp
from bs4 import BeautifulSoup
from concurrent.futures import ProcessPoolExecutor
from io import BytesIO
import os
from zipfile import ZipFile

from abstract_stage import AbstractStage


class GraphCrawler(AbstractStage):
    """docstring for GraphCrawler"""
    # def __init__(self, arg):
    #     super(GraphCrawler, self).__init__()
    #     self.arg = arg
    _stage = "1-graphs"

    def convert_mtx_to_edges(self, in_path, out_path):
        info_line_skipped = False
        with open(in_path) as infile:
            with open(out_path, "w") as outfile:
                for line in infile:
                    if not line.startswith("%"):
                        if info_line_skipped:
                            outfile.write(line)
                        else:
                            info_line_skipped = True

    def limit_to_3_columns(self, in_path, out_path):
        with open(in_path) as infile:
            with open(out_path, "w") as outfile:
                for line in infile:
                    reduced_line = " ".join(line.split(" ")[:3])
                    outfile.write(reduced_line)

    async def save_graph_from_zip(self, graph_zipped, name, group):
        potential_files = [
            i for i in graph_zipped.namelist() if
            name + ".edges" in i or
            name + ".mtx" in i or
            name + ".txt" in i
        ]
        if len(potential_files) == 0:
            print("could not find valid file in zip /", name)
            return None
        filename = potential_files[0]
        if len(potential_files) > 1:
            print("too many possible file in zip, taking", filename, "/", name)
        directory = (
            os.path.dirname(os.path.realpath(__file__)) +
            "/../data/1-graphs/{}/".format(group)
        )
        target_filename = name + ".edges"
        target_path = directory + target_filename
        tmp_path = target_path + ".tmp"
        loop = asyncio.get_event_loop()
        zip_destination = await loop.run_in_executor(
            None, graph_zipped.extract, filename, directory)
        if zip_destination.endswith(".mtx"):
            self.convert_mtx_to_edges(zip_destination, tmp_path)
            os.remove(zip_destination)
        else:
            os.rename(zip_destination, tmp_path)
        self.limit_to_3_columns(tmp_path, target_path)
        os.remove(tmp_path)
        return target_filename

    async def extract_links_from_page(
            self, session, group, html, filter):
        parsed_html = BeautifulSoup(html, "html.parser")
        table = parsed_html.find(id="myTable")
        rows = table.find_all("tr")

        headers = [e.text.strip() for e in rows[0].find_all("th")]
        # Graph Name |V| |E| dmax davg r |T|
        # Tavg Tmax κavg κ K ωheu Size Download
        indices = {
            "name": headers.index("Graph Name"),
            "url": headers.index("Download"),
            "nodes": headers.index("|V|"),
            "edges": headers.index("|E|"),
            "size": headers.index("Size"),
        }

        def get_sort_value(element):
            return int(element.get("class")[1][:-1])

        def parse_row(row):
            elements = row.find_all("td")
            return {
                "group": group,
                "name": elements[indices["name"]].text.strip(),
                "url": elements[indices["url"]].find("a").get("href"),
                "nodes": get_sort_value(elements[indices["nodes"]]),
                "edges": get_sort_value(elements[indices["edges"]]),
                "size": get_sort_value(elements[indices["size"]])
            }
        for row in rows[1:]:
            graph_nr_properties = parse_row(row)
            if filter is not None and not filter(graph_nr_properties):
                continue
            async with session.get(graph_nr_properties["url"]) as response:
                with ZipFile(BytesIO(await response.read()), "r") as zipped:
                    graph_path = await self.save_graph_from_zip(
                        zipped, graph_nr_properties["name"], group
                    )
            if graph_path is None:
                print("skipping", url, "/", graph_nr_properties["name"])
            else:
                graph_nr_properties["path"] = graph_path
                self._save_as_csv(graph_nr_properties)

    async def get_page_html(self, session, group, filter):
        url = "http://networkrepository.com/{}.php".format(group)
        async with session.get(url) as response:
            html = await response.text()
            await self.extract_links_from_page(
                session, group, html, filter
            )

    async def crawl_graphs(self, groups, filter=None):
        async with aiohttp.ClientSession() as session:
            session_tasks = []
            for group in groups:
                task = asyncio.ensure_future(
                    self.get_page_html(session, group, filter)
                )
                session_tasks.append(task)
            await asyncio.wait(session_tasks)

    async def async_execute(self):
        await self.crawl_graphs(
            ["bio"],
            lambda x: x["size"] < 100000
        )

    def execute(self, **kwargs):
        loop = asyncio.get_event_loop()
        # loop.set_default_executor(ProcessPoolExecutor())
        loop.run_until_complete(self.async_execute())


if __name__ == "__main__":
    crawler = GraphCrawler()
    crawler.execute()
    crawler.close()
