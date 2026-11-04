"""Restore shortest round-trip text for chart doubles after PowerPoint save."""
from pathlib import Path
import json
import struct
import zipfile
import xml.etree.ElementTree as ET

R = Path(__file__).resolve().parents[1]
source = R / 'private/candidate_v3_RTL.pptx'
target = R / 'private/candidate_v3_RTL_normalized.pptx'
ns = {'c': 'http://schemas.openxmlformats.org/drawingml/2006/chart'}
changes = []
with zipfile.ZipFile(source) as incoming, zipfile.ZipFile(target, 'x') as outgoing:
    for info in incoming.infolist():
        raw = incoming.read(info.filename)
        if info.filename.startswith('ppt/charts/chart') and info.filename.endswith('.xml'):
            root = ET.fromstring(raw)
            for node in root.findall('.//c:ser/c:val//c:v', ns):
                old = node.text
                new = repr(float(old))
                assert struct.pack('d', float(old)) == struct.pack('d', float(new))
                if old != new:
                    pattern = ('<c:v>' + old + '</c:v>').encode()
                    assert pattern in raw
                    raw = raw.replace(pattern, ('<c:v>' + new + '</c:v>').encode())
                    changes.append({'part': info.filename, 'old': old, 'new': new,
                                    'binary64_value_unchanged': True})
        outgoing.writestr(info, raw)
(R / 'private/chart_literal_normalization_v1.json').write_text(
    json.dumps({'status': 'accepted', 'changes': changes,
                'reason': 'PowerPoint emitted 17-digit decimal text; Excel snapshot requires preservable decimal precision'}, indent=2), encoding='utf8')
print('Normalized ' + str(len(changes)) + ' numeric texts; binary64 values unchanged')
