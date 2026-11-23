
"""Render the English decision reference in landscape A4."""
import json
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

HERE = Path(__file__).resolve().parent
DESTINATION = HERE.parent.parent / "output" / "pdf" / "Partition_Decision_Rules_Final_EN.pdf"
NAVY = colors.HexColor("#17324A")
TEAL = colors.HexColor("#0C6A64")
GRAY = colors.HexColor("#415365")
PALE = colors.HexColor("#F1F5F6")
INK = colors.HexColor("#192A38")


ANALYZE = [
    ("A01", "The same word has both labels.", "Return INFEASIBLE with both trace IDs.",
     "Every partition.", "Both copies have identical projections on every block.", "opposite_labels"),
    ("A02", "The alphabet is empty and a negative exists.", "Return INFEASIBLE with its trace ID.",
     "The only partition, the empty partition.", "There is no block that could reject the negative.", "empty_alphabet"),
    ("A03", "A declared symbol never occurs.", "Keep it as a singleton in the answer. Retain one active symbol if all are unused.",
     "Partitions joining unused symbols may be omitted in optimization.", "Splitting off an unused symbol keeps all meaningful projections and adds a block. With no positives, a nonempty block can reject all negatives.", "unused_and_contraction"),
    ("A04", "A word repeats with the same label.", "Deduplicate witness mining. Preserve original table column IDs.",
     "None.", "Repeated membership constraints and rejection obligations leave feasibility unchanged.", "duplicate"),
    ("A05", "A trace is the empty word.", "Keep it and compute its ordinary projection.",
     "None from emptiness alone.", "Every projection of the empty word is empty. With positives ab and cd, block ac separates the empty negative.", "example"),
    ("A06", "No negatives, or no positives with a nonempty alphabet.", "The singleton partition is optimal.",
     "No candidate needs a feasibility query.", "With no negatives the obligations are vacuous. With no positives any block can reject all negatives. The singleton partition has the most blocks.", "no_positive"),
    ("A07", "For the same negative, each of two or more atoms has a matching positive on its complement.", "Merge those atoms. Recheck after contraction.",
     "Within the remaining search, every partition that splits the required atoms.", "Away from an atom, projection equality is inherited from its complement. A single rejecting block must therefore contain all required atoms.", "unused_and_contraction"),
    ("A08", "Deleting a set of atoms makes a positive and a negative equal.", "Record a hitting obligation for that negative.",
     "Partitions in which no block can meet all known obligations for that negative.", "A block avoiding a deletion set inherits the equality. One block must meet all the deletion sets of the same negative.", "sunflower"),
    ("A09", "Equal symbol counts can conceal a difference in order.", "Use singleton counts and differing pair projections to propose deletion sets. Check the retained projection.",
     "Only exclusions backed by confirmed A08 witnesses.", "Cover every differing pair after removing count conflicts. On the complement, unary and pair projections agree, which determines the word.", "order_triples"),
    ("A10", "The alphabet is nonempty and no word has opposite labels.", "Use a single active block as an initial incumbent.",
     "None by itself. A certified lower bound can close costlier branches.", "Projection onto all observed symbols preserves each entire word. Every negative is therefore separated.", "unit"),
    ("A11", "For every negative, some singleton count is absent from that symbol's positive counts.",
     "Certify the singleton partition before mining deletion witnesses.",
     "No feasibility query or lower-cost search is required.",
     "On a singleton, counts completely determine the projected word. The singleton partition already attains the alphabet-size upper bound.", "singleton_stage"),
]

SELECT = [
    ("S01", "A column is zero in every row on block U.", "Record U as a zero region with its positive witness.",
     "Every subset of U is incapable of rejecting that negative.", "Applying a second projection preserves equality with the same positive.", "example"),
    ("S02", "For the same negative, every candidate block is inside a known zero region.", "Infer NO without a query. Reuse regions from any earlier evidence.",
     "The covered candidate and every refinement of it.", "Every block inherits a positive witness. Different blocks may inherit different witnesses.", "example_full"),
    ("S03", "A different negative is fixed at zero on a block of a rejected proposal.", "Keep that zero with its own column ID.",
     "Regions from this column may later participate in S02 for that negative.", "The equality holds regardless of which column caused the complete proposal to fail.", "held_together"),
    ("S04", "Each negative has a block that contains a known rejecting region.", "Infer ACCEPT. Update the incumbent if it improves.",
     "No incompatible family follows. Use the improved cost with S08 or S09.", "If the larger block matched a positive, its smaller known rejecting region would match too. All attainable rejections can be realized together.", "reject_superset"),
    ("S05", "A witnessed NO region R coarsens the current partition P.", "Generate only pair merges crossing a boundary of R.",
     "In-region children themselves are incompatible. Keep a route to every compatible coarsening.", "A compatible coarsening has a block spanning two regions of R. Merging two P-atoms across that boundary preserves a route to it.", "example"),
    ("S06", "Several disjoint proposed unions have a shared positive witness on their separate atoms.", "Rank a complete diagnostic partition. Query it once within the budget.",
     "No exclusion from the forecast. A reply can trigger S01 and S02.", "Local equality can fail on a union because relative order becomes visible. Actual returned evidence is required.", "example"),
    ("S07", "Known rejecting blocks or hitting obligations suggest a cheaper complete partition.", "Merge suggested groups. Confirm by S04 or one recorded full query.",
     "None until a verified incumbent and lower bound justify a cutoff.", "Known rejection survives enlargement. A conjectured hitting set may still match an unaccounted-for positive, so verify the entire proposal.", "sunflower"),
    ("S08", "A candidate is known to fail and one more merge reaches the incumbent cost.", "Close the branch and retain the current verified incumbent.",
     "Every strictly improving descendant of this node.", "A failed partition needs at least one additional merge to become compatible.", "unit"),
    ("S09", "Hitting obligations give an internal merge bound. Supports may overlap.", "Combine supports and charge only guaranteed nonduplicate cost.",
     "Strict improvements are impossible if current cost plus the bound reaches the incumbent.", "For supports A and B, add their bounds and subtract at most max(0, |A intersect B| - 1). Uphold each individual bound and use the union for the next step.", "sunflower"),
    ("S10", "Two negatives have the same local projection and form a free group.", "Keep both original IDs in one local decision group.",
     "No global pruning from the tie alone.", "One local image has one label. The two projections can differ on a larger block.", "held_together"),
    ("S11", "A query is incomplete or evidence is insufficient.", "Retain unresolved options. Stop with INCOMPLETE when the budget expires.",
     "None from the missing information.", "An unresolved query supplies neither a complete rejection witness nor an accepted partition.", "unknown"),
]

headings = ["Rule ID", "Observed evidence", "Action or next complete query",
            "Target and scope", "Why this is sound"]
style = ParagraphStyle("Body", fontName="Helvetica", fontSize=10, leading=13.1, textColor=INK)
small = ParagraphStyle("Small", parent=style, fontSize=8.8, leading=12, textColor=GRAY)
header = ParagraphStyle("Header", parent=style, fontName="Helvetica-Bold", textColor=colors.white)
section = ParagraphStyle("Section", parent=style, fontName="Helvetica-Bold", fontSize=25, leading=29, textColor=NAVY)
label = ParagraphStyle("Label", parent=style, fontName="Helvetica-Bold", fontSize=10, textColor=TEAL)
WIDTH = landscape(A4)[0] - 72


def para(value, paragraph_style=style):
    return Paragraph(escape(value), paragraph_style)


def table(rows):
    data = [[para(x, header) for x in headings]]
    for rule, observed, action, family, proof, trace in rows:
        data.append([para(rule, label), para(observed), para(action), para(family),
                     Paragraph(escape(proof) + "<br/><font color='#415365' size='8.5'>"
                               + escape(evidence_label(rule)) + "</font>", style)])
    grid = Table(data, colWidths=[50, 150, 157, 167, WIDTH-524], repeatRows=1)
    grid.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, -1), (-1, -1), 0.5, colors.HexColor("#CBD7DC")),
    ]))
    return grid


def page(title, introduction, rows):
    return [para(title, section), Spacer(1, 9), para(introduction), Spacer(1, 14), table(rows)]


def footer(canvas, document):
    w, _ = landscape(A4)
    canvas.setStrokeColor(colors.HexColor("#CBD7DC"))
    canvas.line(30, 38, w-30, 38)
    canvas.setFillColor(GRAY)
    canvas.setFont("Helvetica", 9)
    canvas.drawString(30, 23, "PASSIVE AUTOMATA LEARNING  /  CERTIFIED PARTITION SELECTION")
    canvas.drawRightString(w-30, 23, str(document.page))


def evidence_label(rule):
    entry = INDEX[rule]
    indices = entry["event_indices"]
    events = ", ".join(map(str, indices)) if len(indices) < 5 else f"{indices[0]}-{indices[-1]}"
    return f"{entry['file']} / events {events}"


HYBRID = [
    ("A12", "A singleton count is absent from all positive counts for an original negative.",
     "Seed its rejecting region and skip costly mining for that column.",
     "That negative's obligation in every coarsening of the root.",
     "Projecting any larger matching block to this singleton would give a matching count.", "exam_multi"),
    ("A13", "The root fails. One pair covers all residual negatives, or two disjoint pairs cover them and all one-pair candidates fail.",
     "Return the covering partition and replay all cheaper layers.",
     "Cost zero in both cases. Cost one when all pairs carry a negative and positive equality witness.",
     "Every cost-one partition has one pair block. Root coverage survives merges and the submitted answer is checked on all traces.", "hdfs_1024"),
    ("A14", "Every residual negative-positive comparison has a complete list of unary and binary discrepancies.",
     "Choose one alternative per comparison and minimize the number of component unions.",
     "Every partition below the minimum rank of a witness choice.",
     "Number same-symbol occurrences. Unary and pair agreement determines their full relative order. Each witness choice forces one connected block per negative, and its components realize exactly that rank.", "rank_triple"),
    ("A15", "A greedy collection of disjoint pairs covers all residual negatives by raw projection.",
     "Seed merge search with the compatible pair partition. Respect any mandatory contractions.",
     "The compatible incumbent itself. Its cost becomes the strict-improvement cutoff threshold.",
     "Each negative retains at least one separating block. Coarsening to respect mandatory atoms preserves the separating projections.", "cover_path_8"),
    ("S12", "For several negatives, two disjoint hitting obligations are available on mutually disjoint supports.",
     "Charge one merge per support and compare to the incumbent.",
     "All strict improvements above the cited node when the bound meets the incumbent.",
     "The rejecting block needs one atom from each side. Joining two atoms costs one rank unit within each support. The disjoint necessary connections add even when they lie in the same final block.", "cover_path_8"),
]

MISUSE = [
    ("A01", "Distinct words aba and aab agree on singletons. Opposite labels are conclusive only for the same full word."),
    ("A02", "The empty alphabet with no negatives has the compatible empty partition."),
    ("A03", "Removing a declared unused symbol changes |P|. It must be retained as its own block."),
    ("A04", "Deduplicating a word across labels would erase the infeasibility witness a / a."),
    ("A05", "With positives ab and cd, the empty negative is separated by ac."),
    ("A06", "An empty positive class with an empty alphabet still cannot reject an existing negative."),
    ("A07", "Against positives ab and cd, the hitting obligation {a,b} allows either symbol. It cannot force a and b together."),
    ("A08", "Intersecting only {a,b} against ab,cd / empty leaves the negative matched by cd on block a."),
    ("A09", "aba and aab have equal counts. Repeated occurrence order is essential."),
    ("A10", "An identical positive and negative agree even on the full alphabet."),
    ("A11", "abc / bac has the same singleton counts. The singleton shortcut requires a witness for each negative."),
    ("A12", "For ab / aa,ba, a separates aa and leaves ba unresolved. Keep both original IDs."),
    ("A13", "For positives a,b,c and empty negative, every pair fails. The full triple works at cost two."),
    ("A14", "For ab / empty, keeping only discrepancy {a} would incorrectly forbid the valid alternative {b}."),
    ("A15", "With positives af,de,ace,ba and negatives eae,abf,dc,dfe,ebe, the greedy ab | cd | ef costs three. The compatible bef | a | c | d costs two."),
    ("S01", "A free column allows both 0 and 1. One zero in a feasible row proves no fixedness."),
    ("S02", "For ab / a,b, both singletons match some negative, but each negative is rejected on the other singleton."),
    ("S03", "A zero for one negative in a NO reply cannot be reassigned to the reported failing column."),
    ("S04", "For ab,cd / empty, blocks a and c each match a positive. Their union ac separates the negative."),
    ("S05", "The waived child ab | c | d has compatible descendant abc | d. The latter is reachable through ac first."),
    ("S06", "Singleton regions can share a positive while their union differs in order, as in ab / ba."),
    ("S07", "A partial witness set for ab,cd / empty may suggest a, which still matches cd."),
    ("S08", "A failed node at the incumbent's threshold can still have compatible descendants."),
    ("S09", "For aabc / abac,baac, the same merge ab handles both negatives. Charging twice overstates the bound."),
    ("S10", "For ab / baa,aba the projections agree on a and differ on ab."),
    ("S11", "A query cap of zero on the example leaves unresolved candidates and yields INCOMPLETE."),
    ("S12", "Two obligations {a,b} and {b,c} may both be hit by b. Disjointness is needed to charge a merge."),
]


def run():
    DESTINATION.parent.mkdir(exist_ok=True, parents=True)
    doc = SimpleDocTemplate(str(DESTINATION), pagesize=landscape(A4), leftMargin=30,
                            rightMargin=30, topMargin=28, bottomMargin=49,
                            title="Final Partition Decision Rules", author="Passive Automata Learning")
    pages = [
        ("Analyze traces", "One compatible partition of maximum size, with independently replayed optimality.", ANALYZE[:6]),
        ("Analyze traces", "Projection equalities give necessary conditions and preserve the original trace IDs.", ANALYZE[6:]),
        ("Select partition after NO", "Every query submits a complete partition of the declared alphabet.", SELECT[:6]),
        ("Search and optimality", "Compare the certified lower bound with the cost of a compatible incumbent.", SELECT[6:]),
        ("Hybrid raw analysis", "Raw analysis can discharge obligations before constructing a complete query table.", HYBRID),
    ]
    story = []
    for title, intro, rows in pages:
        if story:
            story.append(PageBreak())
        story += page(title, intro, rows)

    transcript = [
        ("Query 0 / NO", "a | b | c | d", "For the empty negative, cd witnesses zero on a and b. Positive ab witnesses zero on c and d."),
        ("Query 1 / diagnostic NO", "ab | cd", "The same negative matches cd on ab and ab on cd."),
        ("Inferred without a query", "ab | c | d and a | b | cd", "Each block is contained in an evidenced zero region for that negative. These are the two actually skipped candidates in this run."),
        ("Query 2 / ACCEPT", "ac | b | d", "On ac the positive images are a and c. The negative image is empty. Query 0 excludes the only cheaper partition."),
    ]
    story += [PageBreak(), para("Worked diagnostic transcript", section), Spacer(1, 10),
              para("Positive traces are ab and cd. The negative is the empty word."), Spacer(1, 15)]
    for tag, candidate, why in transcript:
        story += [para(tag, label), Spacer(1, 3), para(candidate), Spacer(1, 3), para(why, small), Spacer(1, 10)]
    story += [para("Controlled probe test", label), Spacer(1, 4),
              para("With abcde / abced and a fixed candidate order, passive reuse, one paid probe and two paid probes took 11, 6 and 4 total calls. They skipped 0, 6 and 9 actual candidates. The corresponding proved NO families before the scan had 1, 15 and 37 partitions. Evidence is in diagnostics.json.", small)]

    story += [PageBreak(), para("Two independently verified optima", section), Spacer(1, 15)]
    for title, statements in (
        ("HDFS-1024 / 27 blocks / cost 2", [
            "Singleton counts establish rejection for every original negative except 288 IDs representing 130 distinct words.",
            "Each of the 406 one-pair candidates has a residual negative whose projection on the pair matches a named positive. Its other blocks are singletons and that negative was unresolved at the root.",
            "E16 with E18, and E20 with E4, cover the residual negatives. The answer has those two pair blocks and 25 singletons. Replay checks all raw traces and all 406 cheaper candidates.",
            "Evidence is in hdfs_1024.json, event 1 and certificate.failures.",
        ]),
        ("Eight-vertex path / 12 blocks / cost 4", [
            "The raw analyzer finds two disjoint hitting obligations for each of four negatives, corresponding to path edges 1-2, 3-4, 5-6 and 7-8.",
            "For each selected edge, compare its negative ai a(i+1) with each endpoint's positive trace ai bi. Each difference in counts gives a projection equality after deletion. Together they force a connection within that edge's support.",
            "These four supports use disjoint atoms, so the cost is at least four. The emitted compatible incumbent uses bj, dl, fn and gh. Replay checks the whole answer and the four supports at the root.",
            "Evidence is in cover_path_8.json under A15 and S12 and in certificate.records.",
        ]),
    ):
        story += [para(title, label), Spacer(1, 5)]
        for statement in statements:
            story += [para(statement), Spacer(1, 6)]
        story.append(Spacer(1, 14))

    for offset in range(0, len(MISUSE), 14):
        story += [PageBreak(), para("Counterexamples and boundary cases", section), Spacer(1, 12)]
        for rule, example in MISUSE[offset:offset + 14]:
            story += [para(f"{rule}    {example}", small), Spacer(1, 8)]
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    INDEX = json.loads((HERE / "evidence" / "rule_index.json").read_text(encoding="utf-8"))
    run()
