import asyncio
import aiohttp
import backoff
from bs4 import BeautifulSoup
from concurrent.futures import ProcessPoolExecutor
from io import BytesIO
import os
from zipfile import BadZipFile, ZipFile

from abstract_stage import AbstractStage


class GraphCrawler(AbstractStage):
    """TODO docstring for GraphCrawler"""
    _stage = "1-graphs"

    async def backoff_hdlr(details):
        print("Backing off {wait:0.1f} seconds afters {tries} tries "
              "with args {args}".format(**details), flush=True)

    def __init__(
            self, groups=[
                "bio", "bn", "ca", "chem", "eco", "ia",
                "inf", "rec", "rt", "soc", "socfb", "tech", "web"],
            graph_filter_func=lambda x: True):
        super(GraphCrawler, self).__init__()
        self.groups = groups
        self.graph_filter_func = graph_filter_func

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

    @backoff.on_exception(backoff.expo,
                          FileExistsError,
                          on_backoff=backoff_hdlr,
                          max_tries=50)
    async def save_graph_from_zip(self, graph_zipped, name, group):
        potential_files = [
            i for i in graph_zipped.namelist() if
            i.endswith(".edges") or
            i.endswith(".mtx") or
            i.endswith(".txt")
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

    @backoff.on_exception(backoff.expo,
                          (
                            aiohttp.client_exceptions.ServerDisconnectedError,
                            aiohttp.client_exceptions.ClientPayloadError
                          ),
                          on_backoff=backoff_hdlr,
                          max_tries=50)
    async def download_graph(self, session, group, graph_nr_properties):
        try:
            async with session.get(graph_nr_properties["Url"],
                                   timeout=30*60) as response:
                zipped_bytes = BytesIO(await response.read())
                try:
                    with ZipFile(zipped_bytes, "r") as zipped:
                        graph_path = await self.save_graph_from_zip(
                            zipped, graph_nr_properties["Name"], group
                        )
                except BadZipFile as e:
                    print(e, flush=True)
                    graph_path = None
        except asyncio.TimeoutError:
            graph_path = None
        if graph_path is None:
            print(
                "skipping",
                graph_nr_properties["Url"], "/", graph_nr_properties["Name"])
        else:
            graph_nr_properties["Path"] = graph_path
            self._save_as_csv(graph_nr_properties)

    async def extract_links_from_page(self, session, group, html):
        parsed_html = BeautifulSoup(html, "html.parser")
        table = parsed_html.find(id="myTable")
        rows = table.find_all("tr")

        headers = [e.text.strip() for e in rows[0].find_all("th")]
        # Graph Name |V| |E| dmax davg r |T|
        # Tavg Tmax κavg κ K ωheu Size Download
        indices = {
            "Name": headers.index("Graph Name"),
            "Url": headers.index("Download"),
            "Nodes": headers.index("|V|"),
            "Edges": headers.index("|E|"),
            "Size": headers.index("Size"),
        }

        def get_sort_value(element):
            return int(element.get("class")[1][:-1])

        def parse_row(row):
            elements = row.find_all("td")
            return {
                "Group": group,
                "Name": elements[indices["Name"]].text.strip(),
                "Url": elements[indices["Url"]].find("a").get("href"),
                "Nodes": get_sort_value(elements[indices["Nodes"]]),
                "Edges": get_sort_value(elements[indices["Edges"]]),
                "Size": get_sort_value(elements[indices["Size"]])
            }
        download_tasks = []
        for row in rows[1:]:
            try:
                graph_nr_properties = parse_row(row)
            except Exception as e:
                print("Error parsing html row:", e)
                continue
            if self.graph_filter_func(graph_nr_properties):
                task = asyncio.ensure_future(
                    self.download_graph(session, group, graph_nr_properties)
                )
                download_tasks.append(task)
        await asyncio.wait(download_tasks)

    @backoff.on_exception(backoff.expo,
                          (
                            aiohttp.client_exceptions.ServerDisconnectedError,
                            aiohttp.client_exceptions.ClientPayloadError
                          ),
                          on_backoff=backoff_hdlr,
                          max_tries=50)
    async def get_page_html(self, session, group):
        url = "http://networkrepository.com/{}.php".format(group)
        async with session.get(url) as response:
            html = await response.text()
            await self.extract_links_from_page(session, group, html)

    async def crawl_graphs(self):
        connector = aiohttp.TCPConnector(limit_per_host=10,
                                         force_close=True,
                                         enable_cleanup_closed=True)
        # force_close=False,
        # keepalive_timeout=20)
        async with aiohttp.ClientSession(connector=connector,
                                         read_timeout=None,
                                         conn_timeout=None) as session:
            session_tasks = []
            for group in self.groups:
                task = asyncio.ensure_future(
                    self.get_page_html(session, group)
                )
                session_tasks.append(task)
            await asyncio.wait(session_tasks)

    def _execute(self):
        loop = asyncio.get_event_loop()
        # loop.set_default_executor(ProcessPoolExecutor())
        loop.run_until_complete(self.crawl_graphs())
