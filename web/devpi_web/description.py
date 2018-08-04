from __future__ import unicode_literals
from devpi_common.validation import normalize_name
import io
import py
import readme_renderer.rst
import readme_renderer.txt


def get_description_file(stage, name, version):
    config = stage.xom.config
    name = normalize_name(name)
    return config.serverdir.join(
        '.web', stage.user.name, stage.index, name, version, 'description.html')


def get_description(stage, name, version):
    is_mirror = (stage.ixconfig['type'] == 'mirror')
    mirror_web_url_fmt = stage.ixconfig.get('mirror_web_url_fmt')
    if is_mirror and mirror_web_url_fmt is not None:
        html = py.xml.html
        link = mirror_web_url_fmt.format(name=name)
        if link.endswith('/'):
            link = link + "%s/" % version
        else:
            link = link + "/%s/" % version
        return html.div(
            "please refer to description on remote server ",
            html.a(link, href=link)).unicode(indent=2)
    metadata = stage.get_versiondata(name, version)
    desc = metadata.get("description")
    if desc is None:
        html = '<p>No description in metadata</p>'
    else:
        html = render_description(stage, desc)
    return py.builtin._totext(html, "utf-8")


def render_description(stage, desc):
    warnings = io.StringIO()
    html = readme_renderer.rst.render(desc, stream=warnings)
    warnings = warnings.getvalue()
    if warnings:
        desc = "%s\n\nRender warnings:\n%s" % (desc, warnings)
    if html is None:
        html = readme_renderer.txt.render(desc)
    if py.builtin._istext(html):
        html = html.encode("utf8")
    return html
