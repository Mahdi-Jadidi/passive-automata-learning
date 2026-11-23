
"""Render the English decision reference in landscape A4."""
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

HERE = Path(__file__).resolve().parent
DESTINATION = HERE.parent.parent / "output" / "pdf" / "Partition_Decision_Rules_EN.pdf"
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
            "Exactly which partitions are ruled out", "Why this is sound"]
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
                               + escape(trace + ".json") + "</font>", style)])
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


def run():
    DESTINATION.parent.mkdir(exist_ok=True, parents=True)
    doc = SimpleDocTemplate(str(DESTINATION), pagesize=landscape(A4), leftMargin=30,
                            rightMargin=30, topMargin=28, bottomMargin=49,
                            title="Partition Decision Rules", author="Passive Automata Learning")
    story = page("Analyze traces", "Raw-trace rules for unbounded states. The goal is one compatible partition with the maximum number of blocks.", ANALYZE[:6])
    story += [PageBreak(), *page("Analyze traces", "A verified projection equality can impose a necessary condition before the first query.", ANALYZE[6:])]
    story += [PageBreak(), *page("Select partition after NO",
                                 "Each column is an original negative. Fixed zero means zero in every row. Fresh queries submit complete alphabet partitions.", SELECT[:6])]
    story += [PageBreak(), *page("Select partition after NO",
                                 "An incumbent is a compatible partition with known cost. The cutoff is valid against strictly cheaper answers.", SELECT[6:])]
    story += [PageBreak(), para("Worked query transcript", section), Spacer(1, 10),
              para("Positive traces: ab and cd. The only negative is the empty word. Each merge costs one unit."),
              Spacer(1, 20)]

    transcript = [
        ("Query 0  /  NO", "a | b | c | d", "On a and b the positive cd matches the empty negative. On c and d the positive ab matches it."),
        ("Query 1  /  diagnostic NO", "ab | cd", "The complete query confirms two new zeros. Positive cd witnesses ab, and positive ab witnesses cd."),
        ("Inferred without query", "ab | c | d     and     a | b | cd", "Each block is inside a zero region from query 1. The four refinements include these two unqueried partitions and the two already queried partitions."),
        ("Query 2  /  ACCEPT", "ac | b | d", "On ac the positive projections are a and c. The negative projection is empty. The only cheaper partition was refuted by query 0."),
    ]
    for tag, candidate, why in transcript:
        story += [para(tag, label), Spacer(1, 3), para(candidate), Spacer(1, 3), para(why, small), Spacer(1, 12)]
    story += [Spacer(1, 4), para("How to read a table with tied columns", label), Spacer(1, 4),
              para("With positive ab and negatives ba, baa, aba, block a has fixed zero for ba. "
                   "Columns baa and aba share the free image aa, so the feasible rows are 000 and 011. "
                   "On block b the only row is 000. Thus ba refutes the partition, while the other columns "
                   "still provide reusable information. Evidence: held_together.json."),
              Spacer(1, 11),
              para("Rule IDs refer to the proofs in MENTOR_AGENT.md. The filenames in each row refer to recorded examples under evidence/.", small)]
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    run()
