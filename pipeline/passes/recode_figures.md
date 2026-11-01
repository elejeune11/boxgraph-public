This is a second figure pass, because the guide's way of reading figures has changed: readings are now
usually your own code (`mode: code`), at a resolution where the plot box is at least 1500 px on its
shorter side. Earlier readings in `figures.yaml` used the shared digitizer at 300 dpi.

For every figure reading already in `figures.yaml`:
- write a new reading of the same curve or points with your own code, with a new id (the old id plus
  `_code`), and the same `at` positions;
- change the datum that used the old reading to use the new one (`figure: <new id>`), and change nothing
  else in that datum; leave the old reading in `figures.yaml`, unused, so the two can be compared;
- check the new reading with `figure check` and look at the overlay.
Then read anything the earlier pass left out that the guide now asks for (measured data, error bars).
In `figures.md`, add a section "Second pass (own code)" listing each new reading, how it was read, and
how its values differ from the old reading's.
