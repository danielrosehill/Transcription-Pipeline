// Any Markdown output (cleaned transcript, minutes, summary, spec) as a clean A4 PDF.
// typst compile --input md=minutes.md --input title="Family meeting" document.typ out.pdf
#import "@preview/cmarker:0.1.6"
#set page(paper: "a4", margin: 2cm, footer: context [
  #set text(8pt, fill: gray)
  #sys.inputs.at("date", default: "") #h(1fr) Page #counter(page).display() of #counter(page).final().first()
])
#set text(font: ("IBM Plex Sans", "Inter", "Liberation Sans"), size: 11pt)
#set par(justify: false, leading: 0.7em)
#if "title" in sys.inputs [#text(18pt, weight: "bold", sys.inputs.title) #v(0.4em)]
#cmarker.render(read(sys.inputs.at("md", default: "input.md")))
