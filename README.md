![GSL Data Update](https://github.com/vlahm/gsl_dashboard/actions/workflows/update-data.yml/badge.svg)

### Embeddable surface elevation monitor for the South and North Arms of the Great Salt Lake.

[![GSL water level](https://github.com/vlahm/gsl_realtime/blob/main/resources/preview.png)](https://vlahm.github.io/gsl_realtime)

Interactive graph is live at https://vlahm.github.io/gsl_realtime/. Embed this graph in your webpage with the following HTML:

```html
<iframe width="100%" height="425px" src="https://vlahm.github.io/gsl_realtime/" title="Great Salt Lake Level" frameborder="0"  allowfullscreen></iframe>
```

Updates every six hours via GitHub Actions, using USGS gauges [10010000](https://waterdata.usgs.gov/monitoring-location/10010000/) (South Arm, Saltair Boat Harbor) and [10010100](https://waterdata.usgs.gov/monitoring-location/10010100/) (North Arm, Saline). Hover over either line to see its elevation and total lake volume (as a percentage of volume at 4,207 ft) on that date.

Title and footnote are omitted, so they can be styled to fit your webpage. Title can be something like, "Great Salt Lake, daily water level". Footnote should reference the GSL Strike Team reports, e.g.:

```html
See the <a href=https://gardner.utah.edu/great-salt-lake-strike-team />Strike Team report</a>
```

