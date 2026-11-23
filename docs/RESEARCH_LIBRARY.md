# Research and verification library

This is a register of **candidate** research sources, not evidence that any plant, claim,
image, or publication has been verified. Use the exact record or page supporting a claim,
not merely a source's homepage. See [source policy](SOURCE_POLICY.md),
[botanical verification](BOTANICAL_VERIFICATION.md), and
[climate methodology](LOCAL_CLIMATE_METHODOLOGY.md).

## Availability audit

On 2026-11-22, a redirect-following HTTP GET was attempted for each of the 52 URLs in the
original source audit. JSON Schema and GitHub Actions returned HTTP 200 without redirects.
The other 50 failed DNS resolution in the checking environment; this is **not** evidence
that those sites or paths are broken, and their redirects remain unknown. A browser attempt
on GBIF was blocked by the client. Search indexing provided supporting evidence for some
pages, but is not a live check. Additional URLs in this expanded library have not all been
individually checked. Recheck availability and redirects from a working network before
replacing a link or recording an access date for a claim.

The agent workflow service had no registered workflows and its documentation was unavailable
because extensions were not configured. The manually dispatched Build Encyclopedia GitHub
Actions workflow also runs `check_research_links.py` on a GitHub-hosted runner, checking
the URLs in this library and the previously blocked guide, climate, and GBIF links. It
also records limited metadata from the four priority sources, without uploading their full
contents. Download the `research-link-check` artifact for the access time, status,
redirects, metadata, and errors; a failed check makes the job fail, but available reports
are still uploaded. Run it from Actions or
with `gh workflow run build-encyclopedia.yml --ref <branch>` once the change is available
on that branch. The runner is an alternative network, not a guaranteed DNS bypass: DNS,
HTTP, access-control, and runner failures still need investigation. A reachable URL does
not verify its content, support a claim, or grant reuse rights. Review the original source
and record claim-level evidence separately. On 2026-11-23 the hosted check reached 68 of
89 candidate URLs, including all four priority URLs. Seventeen returned HTTP errors and
four had TLS or timeout errors; these results do not prove a site is permanently broken.
The Environment Canada
[historical data search](https://climate.weather.gc.ca/historical_data/search_historic_data_e.html)
was indexed as a possible alternative to the `www.climat` URL below, but its live availability
and any redirect from the original are unconfirmed.

## Botanical identity and scientific verification

Prioritize accepted names, synonyms, taxonomic concepts, and descriptions. Kew and World
Flora Online can disagree; document differences rather than silently selecting a name.

| Resource | URL | Use |
|---|---|---|
| Plants of the World Online | https://powo.science.kew.org/ | Kew names, synonymy, distributions, descriptions |
| Kew name and synonymy resources | https://www.kew.org/science/collections-and-resources/data-and-digital/names-and-taxonomy | World Checklist of Vascular Plants and related resources |
| World Flora Online | https://www.worldfloraonline.org/ | Independent taxonomy comparison |
| World Flora Online search | https://www.worldfloraonline.org/search?query= | Taxon search; record the resulting taxon URL |
| eFloras | https://www.efloras.org/ | Flora treatments |
| Flora of North America | http://floranorthamerica.org/ | North American descriptions and identification |
| USDA PLANTS | https://plants.usda.gov/ | Taxonomy and U.S. distribution |
| GBIF | https://www.gbif.org/ | Taxonomic datasets and occurrence records |
| GBIF API reference | https://techdocs.gbif.org/en/openapi/ | Programmatic data access |
| GBIF occurrence API | https://techdocs.gbif.org/en/openapi/v1/occurrence | Occurrence API candidate URL |
| GBIF species API | https://techdocs.gbif.org/en/openapi/v1/species | Species API candidate URL; the indexed API reference describes Species as deprecated in favor of Taxon |

## British Columbia and Vancouver Island

Use provincial evidence for native, introduced, naturalized, invasive, and conservation
status. An observation or absence from a database alone does not establish local presence
or absence.

| Resource | URL | Use |
|---|---|---|
| E-Flora BC | https://linnet.geog.ubc.ca/biodiversity/eflora/ | Provincial identification and distribution |
| E-Flora species search | https://linnet.geog.ubc.ca/DB_Query/QueryForm.aspx | Find individual atlas records |
| BC Species and Ecosystems Explorer | https://a100.gov.bc.ca/pub/eswp/ | Species and conservation status |
| BC priority invasive plants | https://www2.gov.bc.ca/gov/content/environment/plants-animals-ecosystems/invasive-species/priority-species/priority-plants | Provincial invasive plant guidance |
| Native Plant Study Group | https://www.npsg.ca/ | Regional native-plant education |
| Garry Oak Ecosystems Recovery Team | https://www.goert.ca/ | Garry oak ecosystems and restoration |
| KPU Plant Database | https://plantdatabase.kpu.ca/ | Plant identification and horticultural descriptions |
| Satinflower Cotyledon Library | https://satinflower.ca/pages/cotyledon-library | Regional native-plant information from a nursery |
| BC plant health | https://www2.gov.bc.ca/gov/content/industry/agriculture-seafood/animals-and-crops/plant-health | Provincial plant health and pest resources |

## Climate, hardiness, and frost

| Resource | URL | Use |
|---|---|---|
| Canadian climate normals | https://climate.weather.gc.ca/climate_normals/ | Station climate normals |
| ECCC climate portal | https://climate.weather.gc.ca/ | Historical climate data |
| Historical data search, supplied URL | https://www.climat.meteo.gc.ca/historical_data/search_historic_data_e.html | Historical observations; hostname and redirect unconfirmed |
| Historical data search | https://climate.weather.gc.ca/historical_data/search_historic_data_e.html | Indexed alternative; live access unconfirmed |
| ClimateData.ca | https://climatedata.ca/ | Climate data and projections |
| Canadian plant hardiness | https://planthardiness.gc.ca/ | Canadian zone information |
| Canadian hardiness page | https://planthardiness.gc.ca/index.php?lang=en&m=15 | Interactive information candidate |
| Canadian hardiness dataset | https://open.canada.ca/data/en/dataset/adda404d-93e4-48e9-b6bf-5d1d3952ff22 | Canadian zones and data |
| Canadian hardiness atlas | https://atlas.gc.ca/PlantHardiness/plantHardinessZones.html | Map candidate |
| USDA plant hardiness | https://planthardiness.ars.usda.gov/ | U.S. zone system |
| USDA map creation | https://planthardiness.ars.usda.gov/pages/map-creation | Map methodology candidate |

Record the system, time period, map resolution, location, station, elevation and limitations.
Canadian zones use multiple climate variables; USDA zones use average annual extreme minimum
temperature. Neither is a frost-date estimate. Compare geographically appropriate stations,
years, completeness and thresholds before proposing frost dates. The source-reported 8a/8b
conflict and April 15/October 15 anchors remain unresolved.

## Horticulture and propagation

Prioritize BC and Pacific Northwest guidance. Do not copy planting dates from other regions
without independent local justification.

| Resource | URL | Use |
|---|---|---|
| BC agriculture | https://www2.gov.bc.ca/gov/content/industry/agriculture-seafood/animals-and-crops | Provincial agriculture guidance |
| BC crop production | https://www2.gov.bc.ca/gov/content/industry/agriculture-seafood/animals-and-crops/crop-production | Provincial crop guidance |
| UBC Botanical Garden | https://botanicalgarden.ubc.ca/ | Regional botanical and horticultural knowledge |
| Master Gardeners Association of BC | https://www.bcmastergardeners.org/ | Regional practical gardening |
| Oregon State Extension | https://extension.oregonstate.edu/ | Pacific Northwest horticulture |
| Washington State Extension | https://extension.wsu.edu/ | Pacific Northwest horticulture |
| Cornell Gardening | https://gardening.cornell.edu/ | General growing and propagation |
| Royal Horticultural Society | https://www.rhs.org.uk/ | Plant profiles and cultivation |
| University of Minnesota vegetables | https://extension.umn.edu/vegetables | General vegetable growing |
| Utah State yard and garden | https://extension.usu.edu/yardandgarden/ | General horticultural guidance |

## Images, illustration, and rights

| Resource | URL | Use |
|---|---|---|
| Wikimedia Commons | https://commons.wikimedia.org/wiki/Main_Page | Media discovery |
| Commons plants | https://commons.wikimedia.org/wiki/Category:Plants | Plant photographs |
| CalPhotos flora | https://calphotos.berkeley.edu/flora/ | Botanical photographs |
| USDA PLANTS gallery | https://plants.usda.gov/gallery.html | Plant photographs; exact path unconfirmed |
| GBIF occurrence search | https://www.gbif.org/occurrence/search | Occurrence records and media |
| iNaturalist | https://www.inaturalist.org/ | Observations and reference photographs |
| iNaturalist API | https://www.inaturalist.org/api | Observation and media access |
| Openverse | https://openverse.org/ | Licensed media discovery |
| Openverse API | https://api.openverse.org/v1/ | Programmatic media discovery |
| Creative Commons licenses | https://creativecommons.org/licenses/ | License terms |
| Creative Commons chooser | https://creativecommons.org/chooser/ | License selection by rights holders |
| CC0 | https://creativecommons.org/public-domain/cc0/ | Public-domain dedication |
| CC license guidance | https://creativecommons.org/share-your-work/cclicenses/ | License conditions |
| Commons reuse guidance | https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia | File reuse and attribution |
| Kew collections | https://www.kew.org/science/collections-and-resources | Botanical and visual references |
| Royal Botanic Garden Edinburgh | https://www.rbge.org.uk/ | Botanical collections and research |
| Biodiversity Heritage Library | https://www.biodiversitylibrary.org/ | Historical botanical literature |
| BHL browse | https://www.biodiversitylibrary.org/browse | Historical material discovery |
| Botanical Art & Artists | https://www.botanicalartandartists.com/ | Illustration practice and visual reference |
| Commons botanical illustrations | https://commons.wikimedia.org/wiki/Category:Botanical_illustrations | Historical and contemporary illustration discovery |

Verify each asset's original source, creator, license, attribution, permitted use, and any
modification or share-alike restrictions. Do not assume all images on a portal share a
license. GBIF occurrence data and media may have separate terms; cite datasets and downloads
as required, including their DOIs where applicable. Review historic works' rights for the
intended jurisdiction. Consult [CalPhotos licenses](https://calphotos.berkeley.edu/licenses.html)
and [GBIF citation guidance](https://www.gbif.org/citation-guidelines). Record permissions
where necessary. Images and generated illustrations require independent identity and
anatomical review; a photograph or historical plate is not proof of a modern cultivar.
Check habit, leaves, flowers, fruits or seeds, roots or bulbs where useful, and distinguishing
features. Keep image approval separate from botanical verification, following
[illustration policy](ILLUSTRATION_POLICY.md).

## Accessibility and PDF publication

| Resource | URL | Use |
|---|---|---|
| WCAG 2.2 | https://www.w3.org/TR/WCAG22/ | Accessibility criteria |
| WCAG quick reference | https://www.w3.org/WAI/WCAG22/quickref/ | Practical checks |
| W3C WCAG overview | https://www.w3.org/WAI/standards-guidelines/wcag/ | Standards guidance |
| veraPDF documentation | https://docs.verapdf.org/ | PDF validation |
| veraPDF validation | https://docs.verapdf.org/validation/ | PDF/A and PDF/UA validation |
| PDF Association | https://pdfa.org/ | PDF standards and guidance |
| Adobe PDF accessibility | https://www.adobe.com/accessibility/pdf.html | Accessible PDF guidance |
| SIL Open Font License | https://openfontlicense.org/ | Font license reference |
| Google Fonts | https://fonts.google.com/ | Font discovery; verify each font's license |

Use automated validation with the applicable PDF profile and separately conduct human
accessibility and visual inspection. A machine pass does not prove accessibility or layout
quality. Record the font's actual license and any redistribution obligations.

## Engineering and reproducible builds

| Resource | URL | Use |
|---|---|---|
| Python | https://docs.python.org/3/ | Language and standard library |
| Python CSV | https://docs.python.org/3/library/csv.html | CSV handling |
| JSON Schema | https://json-schema.org/ | Structured data validation |
| python-jsonschema | https://python-jsonschema.readthedocs.io/ | Python schema validation |
| pytest | https://docs.pytest.org/ | Tests |
| Ruff | https://docs.astral.sh/ruff/ | Lint and formatting |
| GitHub Actions | https://docs.github.com/en/actions | CI |
| Actions workflow syntax | https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax | Workflow configuration |
| GitHub Pages | https://docs.github.com/en/pages | Potential online publication |
| ReportLab | https://docs.reportlab.com/ | PDF generation |
| pypdf | https://pypdf.readthedocs.io/ | PDF inspection |
| Pillow | https://pillow.readthedocs.io/ | Image processing |
| pre-commit | https://pre-commit.com/ | Optional developer checks |
| GitHub code security | https://docs.github.com/en/code-security | Security tooling guidance |

## Verification matrix

These are research starting points, not proof of independence or agreement. Check the
underlying sources and taxonomic concepts: aggregators can reuse an authority's data.

| Claim or output | Primary evidence | Cross-check |
|---|---|---|
| Accepted scientific name | POWO / WCVP | WFO; record disagreements |
| BC native distribution | E-Flora BC | GBIF records, with provenance and limitations |
| Invasive status | BC government | E-Flora BC |
| Plant hardiness | NRCan, with named system and period | Local climate evidence, not an equivalent zone calculation |
| Frost dates | ECCC daily observations | Compare appropriate nearby stations |
| Growing requirements | BC or university extension | Botanical institution |
| Local planting advice | BC / Pacific Northwest extension | Original local calendar as a qualified source, not independent validation |
| Botanical illustration | Verified plant descriptions | Independently sourced photographs and human review |
| Image rights | Original asset rights statement | License terms and attribution requirements |
| PDF accessibility | Applicable automated PDF checks | Human accessibility and visual inspection |
| Build correctness | pytest and CI | Rebuild from a clean checkout |

## Recording claim-level evidence

Use the existing [`claims/CLAIM_SOURCES.csv`](../claims/CLAIM_SOURCES.csv): add a row for
each specific claim and source, linked to the stable `plant_id` when applicable. Record the
exact claim, title, organization, author, record URL or repository path, publication date
if known, actual access date, page or section, evidence type, geographic applicability,
confidence, reviewer, review date, status, and notes. In notes identify related cross-check
rows, agreements or conflicts, source limitations, and whether the evidence is suitable for
publication and why. Preserve unknown fields as unknown; never invent dates or reviews.

A candidate in this library is not a claim citation. Do not mark a claim verified until
the exact sources have actually been examined, applicability and independence evaluated,
conflicts resolved or explicitly retained, and the appropriate human review completed.
Keep taxonomy, cultivar, profile, timing and illustration statuses separate. The existing
Arugula conflict is unresolved. This library does not verify the 137 plant records or
approve the publication.
