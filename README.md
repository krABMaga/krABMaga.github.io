# Introduction

Landing page for the Rust-AB framework. This project uses [Zola](https://github.com/getzola/zola), a fast static site
generator built in Rust.
The embedded wasm binaries of the various Rust-AB based examples require the
[v0.11.0](https://github.com/getzola/zola/releases/tag/v0.11.0) release of Zola, which fixes an important issue where
the responses of the wasm js files being served lacked the proper Content-Type header, required for js modules to be
loaded per HTML spec.

# Contributing

To add a new page for a specific simulation, simply create a new markdown file under the `content` folder, with a
filename equal to the name of the folder containing the simulation project on the
[Rust AB examples](https://github.com/rust-ab/rust-ab-examples) repository. The front matter requires some boilerplate
that will be hopefully removed in recent releases. The template's as follows:

```md
+++
title = "Name of the simulation"
[extra]
last_updated = "2021-05-09"
sim_name = "boids"
charts = [
  {name="Strong scaling", id="strong_scaling", csv="strong_scaling", type="line", caption="Lorem ipsum"}
]
+++
```
The `last_updated` date should be set to the current date. When an example changes, a script will automatically update it.
The `sim_name` should be equal to the name of the file and of the simulation. It will be used to fetch the current wasm binary,
and the chart csv files, if any chart is specified.
Charts are optional, and you can add several basic charts in the front matter without making a custom template. It is assumed
that the data source for the charts is a csv file located within the `static/csv` folder.

# Scripts

The script folder contains the `update.py` script, which is used to update the wasm binaries and the chart data for each example.
The script works under Python 3.8.x.
It simply clones (or updates, if a local copy exists) the Rust-AB examples repository, calling `cargo make build-web --profile release`
on each, moving the generated wasm outputs to the correct folder (`static/wasm`) with the correct name. The script copies all the
csvs contained within the `bench` folder of the specific simulation, if any exist. Lastly, it updates the `last_updated` timestamps
in the related markdown file to notify the simulation page has changed. The script blacklists some examples (notably the template project)
and it is ran automatically by a GitHub Action when a new commit is merged in the [Rust-AB-examples repository](https://github.com/rust-ab/rust-ab-examples).

# Theme

The theme used is [zerm](https://github.com/ejmg/zerm/commit/b316f904dcbe60a255beec68e6c23436c1d11f07). The edits are:

- In index.html which adds a template block in the head tag, to allow for pages extending the index to define custom scripts.
- The list_pages macro has been removed.
