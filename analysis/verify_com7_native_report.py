"""Validate a saved physical COM7 GUI report, without opening any serial port."""
from pathlib import Path
import json,sys
p=Path(sys.argv[1]);d=json.loads(p.read_text());rows=[a for a in d['actions'] if a['action']=='rows']
assert any(any(line.startswith('Com7;9600;e;') and ';SD200;' in line for line in a['lines']) and any(s.get('searching')==0 and 'Exit (passive)' in s.get('last_line','') for s in a['states']) for a in rows),'No completed COM7/native-even main-menu result'
assert any(s.get('uart',{}).get('baud')==9600 and s['uart'].get('bits')==7 and s['uart'].get('parity')==2 and s['uart'].get('stop')==0 for a in rows for s in a['states']),'No actual Windows 9600 7E1 evidence'
for tx in d.get('tx_trace',[]):
 assert chr(tx['char']) in 'GISM',tx
 assert tx['length']==257,tx # packed BOOL success | bytes-written << 8
 rx=[r for r in d.get('rx_trace',[]) if r['length'] and r['result'] and r['handle']==tx['handle'] and r['tick']<=tx['tick']]
 if rx:assert tx['tick']-rx[-1]['tick']>=250,(tx,rx[-1])
print('PASS: COM7 found, main menu complete, Windows UART 9600 7E1; available TX/RX timing valid')
