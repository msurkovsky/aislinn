#
#    Copyright (C) 2014 Stanislav Bohm
#
#    This file is part of Aislinn.
#
#    Aislinn is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 2 of the License, or
#    (at your option) any later version.
#
#    Aislinn is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Kaira.  If not, see <http://www.gnu.org/licenses/>.
#


from tags import Tag, embed_img
import xml.etree.ElementTree as xml

plt = None
try:
    import matplotlib.pyplot as plt
    import StringIO
except ImportError:
    pass # User of plt has to make sure that plt is not None

collective_operations = [
    "Gather",
    "Gatherv",
    "Barrier"
    "Scatter",
    "Scatterv",
    "Reduce",
    "Allreduce",
    "Allreduce",
    "Bcast",

    "Igather",
    "Igatherv",
    "Ibarrier"
    "Iscatter",
    "Iscatterv",
    "Ireduce",
    "Iallreduce"
    "Ibcast",
]

wait_operations = [
    "Wait",
    "Waitall",
    "Probe"
]

def make_chart(data, ydata, units):
    fig = plt.figure(figsize=(8, 2))
    plt.plot(ydata, data, "-")
    plt.ylabel(units)
    stringfile = StringIO.StringIO()
    fig.savefig(stringfile, format="png", transparent=True)
    stringfile.seek(0)
    return stringfile.buf


class Entry:

    def __init__(self, name, value, description):
        self.name = name
        self.value = value
        self.description = description

    def make_xml_element(self):
        e = xml.Element(self.name)
        e.text = str(self.value)
        return e

    def make_html_text(self):
        if self.description:
            name = self.description
        else:
            name = self.name.capitalize()
        return "{0}: {1}".format(name, self.value)


class EntryList:

    def __init__(self):
        self.entries = []

    def add(self, name, value, description=None):
        self.entries.append(Entry(name, value, description))


class Report:

    def __init__(self, generator):
        self.program_info = EntryList()
        self.analysis_info = EntryList()
        self.process_count = generator.process_count
        self.statistics = generator.get_statistics()

        self.program_info.add(
                "program-args", " ".join(generator.args), "Program arguments")
        self.program_info.add(
                "processes", generator.process_count, "Number of processes")
        self.program_info.add(
                "send-protocol", generator.send_protocol, "Send protocol")
        self.program_info.add("search",
                              generator.search,
                              "Search strategy")

        if generator.send_protocol == "threshold":
            self.program_info.add(
                    "send-protocol-thresholds",
                    "{0}:{1}".format(
                        generator.send_protocol_eager_threshold,
                        generator.send_protocol_randezvous_threshold),
                    "Threshold values")
        self.analysis_info.add("nodes",
                      generator.statespace.nodes_count,
                      "Number of nodes in statespace")
        self.analysis_info.add("full-statespace",
                      generator.is_full_statespace,
                      "Full statespace")
        self.analysis_info.add("init-time",
                      generator.init_time,
                      "Start time")
        execution_time = generator.end_time - generator.init_time
        self.analysis_info.add("execution-time",
                      execution_time,
                      "Execution time")
        self.analysis_info.add("speed",
                      generator.statespace.nodes_count
                          / execution_time.total_seconds(),
                      "Nodes per second")
        sizes = list(generator.message_sizes)
        sizes.sort()
        self.analysis_info.add("message-sizes",
                      sizes,
                      "Sizes of unicast messages")
        self.error_messages = generator.error_messages

    def entries_to_xml(self, parent_name, entry_list):
        parent = xml.Element(parent_name)
        for entry in entry_list.entries:
            parent.append(entry.make_xml_element())
        return parent

    def entries_to_html(self, tag, entry_list):
        ul = tag.child("ul")
        for entry in entry_list.entries:
            ul.child("li", entry.make_html_text())
        return ul

    def create_xml(self):
        root = xml.Element("report")
        info = self.entries_to_xml("program-info", self.program_info)
        root.append(info)
        info = self.entries_to_xml("analysis-info", self.analysis_info)
        root.append(info)
        for error in self.error_messages:
            e = self.entries_to_xml("error", error.get_entries())
            e.set("name", error.name)
            root.append(e)
            ev = xml.Element("events")
            root.append(ev)
            for event in error.events:
                e = self.entries_to_xml("event", event.get_entries())
                e.set("name", event.name)
                e.set("pid", str(event.pid))
                ev.append(e)
        return xml.ElementTree(root)

    def create_html_head(self, html):
        head = html.child("head")
        head.child("title", "Aislinn report")
        head.child("style", REPORT_CSS)

    def _make_row(self, table, data, classes=None, titles=None):
        tr = table.child("tr")
        for i, d in enumerate(data):
            td = tr.child("td", d)
            if classes and classes[i]:
                td.set("class", classes[i])
            if titles and titles[i]:
                td.set("title", titles[i])

    def export_events(self, events, tag):
        table = tag.child("table")
        process_count = self.process_count
        self._make_row(table.child("thead"), range(process_count))
        tbody = table.child("tbody")
        pids = [ [] for x in xrange(process_count) ]
        for e in events:
            pids[e.pid].append(e)

        step = 0
        while True:
            data = [""] * process_count
            classes = [None] * process_count
            titles = [None] * process_count
            for r in xrange(process_count):
                if len(pids[r]) <= step:
                    continue
                e = pids[r][step]
                name = e.name
                data[r] = name
                if e.stacktrace:
                    titles[r] = e.stacktrace.replace("|", "\n")
                if name in collective_operations:
                    classes[r] = "Collective"
                elif name in wait_operations:
                    classes[r] = "Wait"
                elif name.endswith("end"):
                    classes[r] = "Send"
                elif name.endswith("ecv"):
                    classes[r] = "Recv"
            if not any(data):
                break
            self._make_row(tbody, data, classes, titles)
            step += 1

    def write_html_statistics(self, parent):
        if plt is not None:
            metadata, data, tick = self.statistics
            ydata = range(0, len(data) * tick, tick)
            for i, (name, units) in enumerate(metadata):
                parent.child("h3", name)
                img = make_chart([s[i] for s in data], ydata, units)
                embed_img(parent, img)
        else:
            parent.child("Error: please install matplotlib to obtain charts")

    def create_html(self):
        html = Tag("html")
        self.create_html_head(html)
        body = html.child("body")
        header = body.child("header", id="header").child("div")
        header.set("class", "inner clearfix")
        header.child("h1", "Aislinn report")

        section = body.child("section", id="section")
        div = section.child("div", id="column")
        div.set("class", "inner")

        div.child("h2", "Program information")
        self.entries_to_html(div, self.program_info)

        div.child("h2", "Analysis information")
        self.entries_to_html(div, self.analysis_info)

        div.child("h2", "Errors")

        if self.error_messages:
            div.child("p", "{0} error(s) found" \
                    .format(len(self.error_messages)))
            for error in self.error_messages:
                div.child("h3", "Error: " + error.short_description)
                lst = div.child("ul")
                lst.child("li", error.description)
                if error.pid is not None:
                    lst.child("li", "Rank {0} in MPI_COMM_WORLD".format(error.pid))
                if error.stacktrace is not None:
                    li = lst.child("li", "Stacktrace:")
                    li.child("pre", "{0}" \
                            .format(error.stacktrace.replace("|", "<br>")))
                if error.events:
                    li = lst.child("li", "Events:")
                    self.export_events(error.events, li)
        else:
            div.child("p", "No errors found")

        if self.statistics:
            div.child("h2", "Statistics")
            self.write_html_statistics(div)

        return html

    def write_xml(self, filename):
        self.create_xml().write(filename)

    def write_html(self, filename):
        html = self.create_html()
        with open(filename, "w") as f:
            html.write(f)


REPORT_CSS = """
html, h1, h2, h3, h4, h5, h6, body, div, span,
applet, object, iframe, p, blockquote, pre,
a, abbr, acronym, address, big, cite, code,
del, dfn, em, font, img, ins, kbd, q, s, samp,
small, strike, strong, sub, sup, tt, var,
fieldset, form, label, legend,
dl, dt, dd, ol, ul, li,
table, caption, tbody, tfoot, thead, tr, th, td {
	margin: 0;
	padding: 0;
	border: 0;
	outline: 0;
	font-weight: inherit;
	font-style: inherit;
	font-size: 100%;
	font-family: inherit;
	vertical-align: baseline;
}

body {
	line-height: 1;
	color: black;
	background: white;
	font: 14px/1.8em 'Open Sans', Helvetica, Arial, Helvetica, sans-serif;
	color: #444;
	background: #fff;
	-webkit-font-smoothing: antialiased;
}
h1, h2, h3, h4, h5, h6 {
	color: #000;
	line-height: 1.2em;
	margin-bottom: 0.3em;
}

h2, h3 {
	margin-top: 1em;
}

h1 {
	font-size: 2em;
}

h2 {
	font-size: 1.7em;
}

h3 {
	font-size: 1.5em;
	margin-top: 2em;
}

p {
	margin-bottom: 1em;
}

ol, ul {
	padding-left: 30px;
	margin-bottom: 1em;
}

b, strong {
	font-weight: bold;
}

i, em {
	font-style: italic;
}

u {
	text-decoration: underline;
}

abbr, acronym {
	cursor: help;
	border-bottom: 0.1em dotted;
}

td, td img {
	vertical-align: top;
}

sub {
	vertical-align: sub;
	font-size: smaller;
}

sup {
	vertical-align: super;
	font-size: smaller;
}

code {
	font-family: Courier, "Courier New", Monaco, Tahoma;
	background: #eee;
	color: #333;
	padding: 0px 2px;
}

pre {
	margin-bottom: 1em;
	overflow: auto;
	background-color: #ddd;
	padding: 0.2em;
	border: 1px solid #aaa;
}

header, section, footer,
aside, nav, article, figure {
	display: block;
}

#header {
        background: #025588;
	padding-top: 20px;
	color: #afe1da;
}
#header a { padding: 10px; color: #afe1da; }
#header h1 a,
#header a:hover { color: #dff1fa; }
#header h1 {
	font-size: 2.2em;
	font-weight: bold;
	margin: 10px;
	float: left;
    color: #dff1fa;
}

blockquote {
	font-style: italic;
	margin: 0 0 1em 15px;
	padding-left: 10px;
	border-left: 5px solid #dddddd;
}

.inner {
	width: 840px;
	margin: 0 auto;
}

#column
{
  overflow: hidden;
  margin: 0 auto 0 auto;
  background-color: #EEEEEE;
  padding-left: 40px;
  padding-right: 40px;
}

.clearfix:before,
.clearfix:after {
    content: " ";
    display: table;
}
.clearfix:after {
    clear: both;
}
.clearfix {
    *zoom: 1;
}

table, tr, td {
    border: black solid 1px;
}

td {
    padding: 0.5em;
    text-align: center;
}

.Wait {
    background-color: orange;
}

.Send {
    background-color: lightgreen;
}

.Recv {
    background-color: lightblue;
}

.Collective {
    background-color: #FF5555;
}

"""
