with open("old.txt") as f:
    page = f.read()
page = page.replace("[b]{", "{")
page = page.replace("}[/b]", "}")
with open("old.txt", "w") as g:
    g.write(page)
