import asyncio
import aiohttp
from bs4 import BeautifulSoup
from concurrent.futures import ProcessPoolExecutor
from io import BytesIO
import os
from zipfile import ZipFile


async def save_graph_from_zip(graph_zipped, name, group):
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
    pure_filename = os.path.basename(filename)
    directory = (
        os.path.dirname(os.path.realpath(__file__)) +
        "/../data/1-graphs/{}/".format(group)
    )
    loop = asyncio.get_event_loop()
    destination = await loop.run_in_executor(
        None, graph_zipped.extract, filename, directory)
    if destination != directory + pure_filename:
        os.rename(destination, directory + pure_filename)
    return pure_filename


async def extract_links_from_page(
        session, group, html, graph_consumer, filter):
    parsed_html = BeautifulSoup(html, "html.parser")
    table = parsed_html.find(id="myTable")
    rows = table.find_all("tr")

    headers = [e.text.strip() for e in rows[0].find_all("th")]
    # Graph Name |V| |E| dmax davg r |T| Tavg Tmax κavg κ K ωheu Size Download
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
            with ZipFile(BytesIO(await response.read()), "r") as graph_zipped:
                graph_path = await save_graph_from_zip(
                    graph_zipped, graph_nr_properties["name"], group
                )
        if graph_path is None:
            print("skipping", url, "/", graph_nr_properties["name"])
        else:
            graph_nr_properties["path"] = graph_path
            asyncio.ensure_future(graph_consumer(graph_nr_properties))


async def get_page_html(session, group, graph_consumer, filter):
    url = "http://networkrepository.com/{}.php".format(group)
    async with session.get(url) as response:
        html = await response.text()
        await extract_links_from_page(
            session, group, html, graph_consumer, filter
        )


async def crawl_graphs(groups, graph_consumer, filter=None):
    async with aiohttp.ClientSession() as session:
        session_tasks = []
        for group in groups:
            task = asyncio.ensure_future(
                get_page_html(session, group, graph_consumer, filter)
            )
            session_tasks.append(task)
        await asyncio.wait(session_tasks)


async def main():
    async def graph_consumer(graph_nr_properties):
        print(graph_nr_properties)
    await crawl_graphs(["bio"], graph_consumer, lambda x: x["size"] < 100000)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    # loop.set_default_executor(ProcessPoolExecutor())
    loop.run_until_complete(main())
