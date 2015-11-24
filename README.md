# RoboWriter: A simple pythonic news robot

This is a simple example of what news robot could look like in Python. The robot takes a csv file of data and renders an article based on a template.

It uses [agate][(http://agate.readthedocs.org/) to handle csv files and [Jinja2](http://jinja.pocoo.org/docs/dev/) to render templates.

### Setup

`pip install -r requirements.txt`

### Example usage

See `/examples/unemployment` for a sample config.

``` python
from modules.robowriter import RoboWriter

# Init writer
writer = RoboWriter("examples/unemployment")

# Render texts
writer.render()

# Save texts
writer.save()
```


