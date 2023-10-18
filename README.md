Adds highlights added to Readwise to a plain-text notes repository, in an
opinionated format that looks like this:

```
# Fuel Cells

---
source: https://www.energy.gov/eere/fuelcells/fuel-cells
highlighter_url: https://read.readwise.io/read/01hcvg45jhb33qzfvy6nfybchb
tags: #literature #inbox
uid: [[202310152243]]
---

> Fuel cells work like batteries, but they do not run down or need recharging. They produce electricity and heat as long as fuel is supplied. A fuel cell consists of two electrodes—a negative electrode (or anode) and a positive electrode (or cathode)—sandwiched around an electrolyte. A fuel, such as hydrogen, is fed to the anode, and air is fed to the cathode. In a hydrogen fuel cell, a catalyst at the anode separates hydrogen molecules into protons and electrons, which take different paths to the cathode. The electrons go through an external circuit, creating a flow of electricity. The protons migrate through the electrolyte to the cathode, where they unite with oxygen and the electrons to produce water and heat. Learn more about:

```

Especially useful if run as a cron.

Has some custom funky logic (for example, all notes in my Zettelkasten are
prepended with a UUID like 202310172218), but should be fairly straightforward
to customize for your use case!
