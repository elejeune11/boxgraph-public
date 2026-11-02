"""The BoxGraph schema: the kinds of thing a record can hold.

Generic by construction (principle 12): nothing here names a field, a
model, a quantity or a paper. A paper fills this schema; it never extends it.

Authored records are YAML files in records/<source-id>/. Everything that is
computed (run outputs, comparisons, verdicts, families) is derived and lives
in the build, never in the record (principle 5).
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


# --------------------------------------------------------------------------
# Vocabularies (fixed by the design)
# --------------------------------------------------------------------------


class SourceKind(str, Enum):
    article = "article"
    preprint = "preprint"
    thesis = "thesis"
    book = "book"
    dataset = "dataset"
    software = "software"
    personal_communication = "personal_communication"
    this_work = "this_work"


class Origin(str, Enum):
    """How a datum came to exist (02-boxgraph.md, Origins)."""

    measured = "measured"
    fitted = "fitted"
    estimated = "estimated"
    assumed = "assumed"
    reported = "reported"
    predicted = "predicted"
    derived = "derived"
    run = "run"  # by a source's own software
    assessed = "assessed"


AUTHORED_ORIGINS = {
    Origin.measured,
    Origin.fitted,
    Origin.estimated,
    Origin.assumed,
    Origin.reported,
    Origin.run,
    Origin.predicted,  # a prediction *printed by the paper* is authored
    Origin.derived,  # a derived value *printed by the paper* is authored
}


class ModelRole(str, Enum):
    model = "model"
    fit = "fit"
    processing = "processing"
    comparison = "comparison"


ROLE_OUTPUT_ORIGIN = {
    ModelRole.model: Origin.predicted,
    ModelRole.fit: Origin.fitted,
    ModelRole.processing: Origin.derived,
    ModelRole.comparison: Origin.assessed,
}


class ComparisonPurpose(str, Enum):
    validation = "validation"  # against independent data
    fit_quality = "fit_quality"
    reproduction = "reproduction"  # of the paper's own result
    consistency = "consistency"  # two values that should agree
    approximation = "approximation"  # how good an approximation is


class QuestionKind(str, Enum):
    """Principle 10."""

    possible_error = "possible_error"
    unstated_input = "unstated_input"
    unstated_model = "unstated_model"
    unexplained_difference = "unexplained_difference"
    overstated_claim = "overstated_claim"
    reading = "reading"
    choice = "choice"
    numerics = "numerics"


class RelationKind(str, Enum):
    same_as = "same_as"
    reduces_to = "reduces_to"
    derived_from = "derived_from"
    scales_as = "scales_as"
    approximated_by = "approximated_by"


class RelationStatus(str, Enum):
    verified = "verified"
    ambiguous = "ambiguous"
    refuted = "refuted"
    not_verified = "not_verified"
    pending = "pending"
    unverifiable = "unverifiable"


class Provenance(str, Enum):
    stated = "stated"
    proposed = "proposed"


# --------------------------------------------------------------------------
# Citations
# --------------------------------------------------------------------------


class Citation(Strict):
    """Where something is printed. `page` is the PDF page (1-based). A source that is not a paged
    document is cited by `file` and `lines` (code) or by `sheet` and `cells` (a spreadsheet)."""

    page: int | None = None
    printed_page: str | None = None  # the journal's own page label, if visible
    file: str | None = None  # a file of a code source, relative to its folder
    lines: str | None = None  # "12" or "12-14", 1-based, in `file`
    sheet: str | None = None  # a sheet of a spreadsheet source
    cells: str | None = None  # "B2" or "B2:B8": one cell, or one row or column
    quote: str | None = None  # verbatim text from the page or lines, as short as identifies it
    where: str | None = None  # "Eq. 16", "Table 2", "Fig. 7", "text"
    none: str | None = Field(
        default=None, description="explicit statement that there is no citation, and why"
    )

    @model_validator(mode="after")
    def _has_place_or_none(self) -> Citation:
        if self.none is None and self.page is None and self.file is None and self.sheet is None:
            raise ValueError("a citation needs a page (or a file and lines, or a sheet and cells), "
                             "or `none` saying why there is none")
        if (self.file is None) != (self.lines is None):
            raise ValueError("a citation of code needs both `file` and `lines`")
        if (self.sheet is None) != (self.cells is None):
            raise ValueError("a citation of a spreadsheet needs both `sheet` and `cells`")
        return self


# --------------------------------------------------------------------------
# Record contents
# --------------------------------------------------------------------------


class Reader(Strict):
    """Who read the paper into this record (principle 13)."""

    kind: Literal["human", "agent"]
    name: str
    model: str | None = None
    prompt_version: str | None = None
    date: str


class Source(Strict):
    id: str
    kind: SourceKind
    title: str
    authors: list[str] = []
    year: int | None = None
    venue: str | None = None
    doi: str | None = None
    file: str | None = None  # path under corpus/: a PDF, a code folder, a spreadsheet
    url: str | None = None  # where it is published (a repository, a journal's supplement)
    version: str | None = None  # code and data: 'sha256:...' of the contents read, or a commit
    licence: str | None = None  # code and data: SPDX id, or 'none stated'
    language: str | None = None  # code: e.g. python, matlab
    pages: dict[int, str] | None = None  # pdf page -> printed page label
    page_range: list[int] | None = Field(
        default=None, description="[first, last] PDF pages that belong to this source"
    )
    reader: Reader
    notes: str | None = None


class Quantity(Strict):
    """What a datum measures. `dimension` is a pint dimensionality, e.g.
    '[force]', '[length] ** 2 / [time]', or 'dimensionless'."""

    id: str
    name: str
    dimension: str
    description: str | None = None


class TableData(Strict):
    """A table or a curve as one datum: values indexed by a condition."""

    index_quantity: str
    index_unit: str
    index: list[str]  # printed index values
    values: list[str]  # printed values, same length

    @model_validator(mode="after")
    def _same_length(self) -> TableData:
        if len(self.index) != len(self.values):
            raise ValueError("table index and values must have the same length")
        return self


class AxisCalibration(Strict):
    """An axis of a figure: what it measures, and marks (pixel, printed label).
    The pixel is a coordinate within the reading's crop: a column for the x
    axis, a row for the y axis."""

    quantity: str
    unit: str
    scale: Literal["linear", "log10"] = "linear"
    marks: list[tuple[float, str]] = []  # at least two, except for a reading by the record's own code


class FigureReading(Strict):
    """A calibrated reading of a figure (02-boxgraph.md, Values read from figures).
    The build renders the page region and reads it again every time."""

    id: str
    page: int
    where: str  # "Fig. 3(a)"
    what: str  # which curve or which points, in words
    dpi: int = 300
    crop: tuple[float, float, float, float]  # x0, y0, x1, y1 on the page, in pixels at dpi
    box: tuple[float, float, float, float] | None = None  # plot interior within the crop: c0, r0, c1, r1
    x: AxisCalibration
    y: AxisCalibration
    mode: Literal["curve", "markers", "bars", "code"] = "curve"  # bars: bar charts and histograms;
    # code: read by the record's own code, `code`, which every build runs on the rendered crop
    code: str | None = None  # path within the record, e.g. figures/fig3a.py, defining read(image, at)
    color: str = "#000000"
    tol: float | None = None  # colour tolerance; by default 60% of the colour's contrast with the paper
    seed: tuple[float, float] | None = None  # a point (column, row) on the chosen curve, within the crop
    at: list[str] = []  # curve: printed x positions to read
    min_area: int = 4  # markers: smallest blob in pixels
    max_area: int | None = None
    # error bars on markers or bars: what they are, as the paper says, and where it says so
    error_bars: Literal["sem", "sd", "ci95", "range", "unstated"] | None = None
    error_bars_citation: Citation | None = None
    bar_color: str | None = None  # colour of the error bars, if not the markers' or bars' own


class Datum(Strict):
    id: str
    quantity: str
    unit: str
    origin: Origin
    printed: str | None = None  # scalar, exactly as printed
    table: TableData | None = None  # or a table / curve
    figure: str | None = None  # or read from a figure: the id of a FigureReading
    scale: Literal["linear", "log10", "ln"] = "linear"
    citation: Citation
    conditions: dict[str, str] = {}  # condition quantity id -> printed value with unit
    tuned_to: str | None = None  # datum id this value was set by hand to match
    from_source: str | None = None  # "reports, indirectly": source id it says it comes from
    from_datum: str | None = None  # optional: the datum in that source, if in the record
    note: str | None = None

    @model_validator(mode="after")
    def _scalar_table_or_figure(self) -> Datum:
        if sum(x is not None for x in (self.printed, self.table, self.figure)) != 1:
            raise ValueError(f"datum {self.id}: exactly one of `printed`, `table` or `figure`")
        return self


class Added(Strict):
    """An input the paper does not state, labelled as added (principle 3).
    It behaves as a datum with origin `assumed` wherever it is used."""

    id: str
    quantity: str
    unit: str
    printed: str  # the value chosen, written as a printed value
    basis: str  # what it rests on
    alternatives: list[str] = []  # other values it could reasonably take
    stands_for: str | None = None  # the symbol / thing in the paper it fills in
    conditions: dict[str, str] = {}
    scale: Literal["linear", "log10", "ln"] = "linear"


class Port(Strict):
    quantity: str
    unit: str
    scale: Literal["linear", "log10", "ln"] = "linear"
    description: str | None = None


class Model(Strict):
    """A model as the paper states it. It computes; it holds no values."""

    id: str
    name: str
    role: ModelRole = ModelRole.model
    stated: Citation
    equation: str | None = None  # the equation as printed, in the paper's symbols
    inputs: dict[str, Port]
    outputs: dict[str, Port]
    settings: dict[str, Any] = {}  # numerical settings with the paper's defaults
    built_from: list[str] = []  # model ids
    described_from: str | None = None  # "describes, indirectly": source it says the model is from
    runnable: bool = True
    not_runnable_reason: str | None = None
    from_words: bool = False  # made runnable from a description in words
    stochastic: bool = False
    software: bool = False  # runs the source's own code (a software record): its outputs have origin run

    @model_validator(mode="after")
    def _reason_if_not_runnable(self) -> Model:
        if not self.runnable and not self.not_runnable_reason:
            raise ValueError(f"model {self.id}: not runnable needs a reason")
        return self


class Run(Strict):
    """One model, run once, on recorded inputs and settings."""

    id: str
    model: str
    inputs: dict[str, str]  # model input symbol -> datum or added id
    settings: dict[str, Any] = {}
    outputs: dict[str, str] = {}  # model output symbol -> id for the produced datum
    sweep: dict[str, str] = {}  # input symbol -> table datum id whose *index* it takes, one run per point
    replicates: int | None = None  # a model with randomness: how many seeds (default 5); 1 otherwise
    note: str | None = None


class Comparison(Strict):
    """A comparison is a run of the one model BoxGraph owns."""

    id: str
    purpose: ComparisonPurpose
    computed: str  # datum id (usually a run output)
    printed: str  # datum id (as printed)
    conditions_ok: str | None = None  # label: why differing conditions may still be compared
    note: str | None = None


class Refinement(Strict):
    """A refinement series over a numerical setting (Figure 5)."""

    id: str
    run: str
    setting: str
    factors: list[float] = [1, 2, 4, 8]
    mode: Literal["divide", "multiply"] = "divide"  # step size: divide; sample count: multiply
    output: str  # which output symbol to watch
    tolerance: str  # e.g. "1%" (relative) or "0.01" (absolute, output unit)
    tolerance_basis: str  # the paper's, or why it was chosen (labelled as added)
    tolerance_added: bool = True


class Question(Strict):
    id: str
    kind: QuestionKind
    about: list[str]  # ids of nodes it is about
    text: str
    citation: Citation | None = None


class Reference(Strict):
    id: str  # e.g. "ref-44"
    label: str  # the paper's own reference number or key
    text: str
    source: str | None = None  # source id, if it is in the record


class Relation(Strict):
    """A relation between two models (ModelAtlas). Model ids are global:
    '<source-id>/<model-id>'."""

    id: str
    kind: RelationKind
    a: str
    b: str
    mapping: dict[str, str] = {}  # b's symbol -> expression in a's symbols
    output_map: dict[str, str] = {}  # b's output symbol -> a's output symbol
    regime: dict[str, list[float]] = {}  # a's input symbol -> [lo, hi] for sampling
    limit: dict[str, str] = {}  # reduces_to: a's symbol -> value it tends to ("0", "oo")
    steps: list[str] = []  # derived_from: steps as the paper gives them
    provenance: Provenance
    citation: Citation | None = None  # stated: quote + page
    reason: str | None = None  # proposed: why
    assumptions: list[str] = []
    tolerance: float = 1e-6

    @model_validator(mode="after")
    def _prov(self) -> Relation:
        if self.provenance == Provenance.stated and (self.citation is None or not self.citation.quote):
            raise ValueError(f"relation {self.id}: stated relations need a quote and page")
        if self.provenance == Provenance.proposed and not self.reason:
            raise ValueError(f"relation {self.id}: proposed relations need a reason")
        return self


class Correspondence(Strict):
    """Two quantities, in two sources, that may be the same physical thing.
    Listed with evidence, never merged."""

    id: str
    a: str  # '<source-id>/<quantity-id>'
    b: str
    evidence: str


class CitedLink(Strict):
    """Which value of the cited source a cited datum is, named after both are in the record.
    It adds a link; the datum itself, as printed, is not changed."""

    datum: str  # a datum of this record
    from_source: str | None = None  # the source it comes from, if the datum itself does not say
    from_datum: str  # the datum in the cited source's record
    negated: bool = False  # the two papers print the value with opposite signs, by their own conventions
    evidence: str


class CrossValidation(Strict):
    """A model of this record judged against a measurement printed in another record (05-building:
    "a model in another paper may predict them"). The build runs the model, with inputs from this
    record or the other, and compares its output with the other record's datum at that datum's
    precision. Nothing of the other record is copied here: its values are read at build time."""

    id: str
    model: str  # a model of this record
    inputs: dict[str, str] = {}  # model input -> datum or added id here, or '<record>/<datum>' there
    sweep: dict[str, str] = {}  # model input -> a table (here or '<record>/<datum>') whose index it takes
    settings: dict[str, Any] = {}
    replicates: int | None = None
    output: str  # the model output that predicts the measurement
    against: str  # '<record>/<datum>': the measurement in the other record
    purpose: ComparisonPurpose = ComparisonPurpose.validation  # fit_quality when the model was fitted to it
    quantities: dict[str, str] = {}  # '<record>/<quantity>' there -> the quantity here it is the same as
    conditions_ok: str | None = None  # label: why differing conditions may still be compared
    basis: str  # why this model is expected to predict that measurement
    note: str | None = None


# --------------------------------------------------------------------------
# One record = one source, read once
# --------------------------------------------------------------------------


class Record(Strict):
    source: Source
    quantities: list[Quantity] = []
    data: list[Datum] = []
    added: list[Added] = []
    models: list[Model] = []
    runs: list[Run] = []
    comparisons: list[Comparison] = []
    refinements: list[Refinement] = []
    questions: list[Question] = []
    references: list[Reference] = []
    figures: list[FigureReading] = []
    relations: list[Relation] = []
    correspondences: list[Correspondence] = []
    cited: list[CitedLink] = []
    validations: list[CrossValidation] = []
