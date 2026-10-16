from goldeneye.reports.pdf_generator import _template_environment


def test_html_templates_enable_autoescaping():
    env = _template_environment()
    rendered = env.from_string("<p>{{ value }}</p>").render(value="<script>alert(1)</script>")
    assert "<script>" not in rendered
    assert "&lt;script&gt;" in rendered
