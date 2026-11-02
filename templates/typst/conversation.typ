// Conversation / call transcript with speech bubbles.
// typst compile --input data=turns.json conversation.typ out.pdf
// turns.json: {"title": "...", "subtitle": "...", "date": "...", "participants": ["Daniel", "Hannah"],
//              "summary": "optional paragraph", "decisions": ["optional"], "turns": [{"speaker": "Daniel", "text": "..."}]}
#let d = json(sys.inputs.at("data", default: "turns.json"))
#let palette = (rgb("#dbeafe"), rgb("#fce7f3"), rgb("#dcfce7"), rgb("#fef3c7"), rgb("#ede9fe"))
#let people = d.at("participants", default: d.turns.map(t => t.speaker).dedup())
#let colour(name) = palette.at(calc.rem(people.position(p => p == name), palette.len()))
#let side(name) = calc.rem(people.position(p => p == name), 2)

#set page(paper: "a4", margin: 2cm, footer: context [
  #set text(8pt, fill: gray)
  #d.at("date", default: "") #h(1fr) Page #counter(page).display() of #counter(page).final().first()
])
#set text(font: ("IBM Plex Sans", "Inter", "Liberation Sans"), size: 10.5pt)

#align(center)[
  #text(18pt, weight: "bold", d.title) \
  #if "subtitle" in d [#text(11pt, fill: gray.darken(30%), d.subtitle) \ ]
  #text(9pt, fill: gray, people.join(" · "))
]
#v(0.6em)
#if "summary" in d [
  #block(fill: luma(245), inset: 10pt, radius: 6pt, width: 100%)[*Summary.* #d.summary]
]
#if "decisions" in d and d.decisions.len() > 0 [
  #block(inset: (x: 10pt))[*Decisions*
    #for x in d.decisions [- #x]]
]
#v(0.6em)
#for t in d.turns {
  let al = if side(t.speaker) == 0 { left } else { right }
  align(al,
    block(width: 82%, breakable: true)[
      #align(al, text(8.5pt, weight: "bold", fill: gray.darken(40%), t.speaker))
      #v(-0.5em)
      #block(fill: colour(t.speaker), inset: 9pt, radius: 10pt, width: 100%, align(left, t.text))
    ])
  v(0.2em)
}
