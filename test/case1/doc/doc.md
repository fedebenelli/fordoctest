project: case1
summary: some example
project_github: https://github.com/fedebenelli/fordoctest
author: user
author_description: example_user
github: https://github.com/fedebenelli
src_dir: ..
exclude_dir: ../test ../doc
output_dir: ../doc/ford_site
preprocessor: gfortran -E
display: public
         protected
         private
source: false
proc_internals: true
sort: permission-alpha
docmark_alt: !>
docmark: !
predocmark_alt: *
print_creation_date: true
creation_date: %Y-%m-%d %H:%M %z
md_extensions: markdown.extensions.toc
               markdown.extensions.smarty
graph: true
license: MPL
page_dir:pages
