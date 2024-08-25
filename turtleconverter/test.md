---
title: test
slug: test
date: 2021-07-01
info: These tags will be included as a metadata dictionary in the sections output and will not be included in the HTML output (unless specified in the template or by mkdocs)
example_metadata: I'm metadata specified inside a markdown file!
---

# Example Document
Automatically generated using [turtleconverter](https://github.com/sondregronas/turtleconverter)

This document is generated from this markdown file: https://github.com/sondregronas/turtleconverter/blob/main/turtleconverter/test.md (Note that the [example templating file](https://github.com/sondregronas/turtleconverter/blob/main/example_override.html) is also used, hence the weird header and footer)

## Heading 1

Code blocks work <mark style="background: darkblue;">with highlighting</mark>, just like in [mkdocs](https://squidfunk.github.io/mkdocs-material/reference/code-blocks)!

```python hl_lines="3 4"
# This is a python code block
print("Hello, World!") # (1)
# Highlihted line
# Another highlighted line
```

1. You can even add annotations to your code blocks :smile:


## Heading 2

> [!NOTE]+ Callouts are also supported!
> Woohoo!

> [!TIP] You can add as many callouts as you want!

> [!WARNING]- Foldable callouts, either using Obsidians syntax, or mkdocs's
> There's more information below!


> Blockquotes are also supported!

## Embeds

Link: [YouTube video](https://www.youtube.com/watch?v=dQw4w9WgXcQ)

Alternatively just provide the link: https://www.youtube.com/watch?v=dQw4w9WgXcQ

<iframe width="560" height="315" src="https://www.youtube.com/embed/dQw4w9WgXcQ?si=CX_S_qf3As47elL_" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

## Tables

| Tables        |      Are      |  Cool |
|---------------|:-------------:|------:|
| col 3 is      | right-aligned | $1600 |
| col 2 is      |   centered    |   $12 |
| zebra stripes |   are neat    |    $1 |

## Math

Math is supported using LaTeX syntax:

$f(a)=f(b)$ $5*2=10$

$$
\int_{a}^{b} x^2 dx
$$

KaTeX is also supported:

$$
\begin{aligned}
\dot{x} & = \sigma(y-x) \\
\dot{y} & = \rho x - y - xz \\
\dot{z} & = -\beta z + xy
\end{aligned}
$$

## Lists

- Unordered lists are supported
- As well as ordered lists
    - And nested lists
        1. With as many levels as you want
        2. Just like in mkdocs

## Ordered lists:

1. This is a list item
2. This is another list item
    1. This is a nested list item
    2. This is another nested list item

## Task lists

- [ ] Task lists are supported
- [x] As well as completed tasks

## Images

While images _are_ supported, they will need to be placed relative to the rendered HTML output. This is because the script does not move or copy any images.

![img.png](img.png)

`![img.png](img.png)`

Resized

![img.png](img.png){width=128}

`![img.png](img.png){width=128}`

External images however will work just fine:

![External image](https://placehold.co/600x400)

`![External image](https://placehold.co/600x400)`

## Where can I get this markdown to HTML converter?

See the [GitHub page](https://github.com/sondregronas/turtleconverter) for more information.
