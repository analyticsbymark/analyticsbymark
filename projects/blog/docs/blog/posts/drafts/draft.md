---
date:
  created: 2025-08-30
---

# Draft

Using this as a template for creating drafts. This is the initital paragraph prior 
to the _more_ section.

<!-- more -->

Here is the rest of the blog post.

```py {.annotate}
--8<-- "dev/docs_src/space_dev/modelling/tutorial_002.py"
```

--8<-- "dev/docs_src/space_dev/modelling/annotations/tutorial_002.md"


[//]: # (```py {.annotate})

[//]: # (--8<-- "../../../../dev/docs_src/space_dev/modelling/tutorial_002.py")

[//]: # (```)

[//]: # ()
[//]: # (--8<-- "./docs_src/space_dev/modelling/annotations/tutorial_002.md")


``` yaml
theme:
  features:
    - content.code.annotate # (1)!
```

1.  :man_raising_hand: I'm a code annotation! I can contain `code`, __formatted
    text__, images, ... basically anything that can be written in Markdown.
